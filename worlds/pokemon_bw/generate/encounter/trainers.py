from typing import TYPE_CHECKING

from Options import OptionError
from .. import TrainerPokemonEntry, SpeciesEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def generate_trainer_teams(world: "PokemonBWWorld"):
    from ...data.trainers.data import table as trainer_table
    from ...data.pokemon.species import get_weighted_random_species, forms_by_dex
    from ...data.pokemon.evolution_methods import methods
    from ...data.pokemon.types import by_name as types_by_name

    if not world.options.randomize_trainer_pokemon.is_randomize:
        return

    mods = world.options.randomize_trainer_pokemon
    gym_types: dict[str, str] = {}
    t_types: list[str | None] | None = None if not mods.is_type_themed else [None] * len(trainer_table)
    rivals_starter: tuple[list[SpeciesEntry], ...] | None = ([], [], [], [], [], []) if mods.is_rivals_keep_starter else None
    rivals_slots: tuple[list[TrainerPokemonEntry], ...] | None = ([], [], [], [], [], []) if mods.is_rivals_keep_starter else None
    stats_threshold: int = world.options.pokemon_randomization_adjustments["Overpowered threshold"]
    underpowered_threshold: int = world.options.pokemon_randomization_adjustments["Underpowered threshold"]
    force_threshold: int = world.options.pokemon_randomization_adjustments["Force threshold"]
    blacklist = world.options.trainer_randomization_blacklist.value

    any_species_by_type: dict[str, dict[int, list[SpeciesEntry]]] = {t: {} for t in types_by_name}
    any_species: dict[int, list[SpeciesEntry]] = {}
    for dex, species_names in forms_by_dex.items():
        for species_name in species_names:
            if species_name in blacklist:
                continue
            spec_entry = world.species_entries[species_name]
            if mods.is_prevent_overpowered and sum(spec_entry.base_stats) > stats_threshold:
                continue
            for t in spec_entry.types:
                if dex not in any_species_by_type[t]:
                    any_species_by_type[t][dex] = [spec_entry]
                else:
                    any_species_by_type[t][dex].append(spec_entry)
        if mods.is_prevent_overpowered:
            all_forms = [spec_entry for spec_entry in
                         (world.species_entries[s_name] for s_name in species_names if s_name not in blacklist)
                         if sum(spec_entry.base_stats) <= stats_threshold]
        else:
            all_forms = [world.species_entries[s_name] for s_name in species_names if s_name not in blacklist]
        if all_forms:
            any_species[dex] = all_forms
    if not all(any_species_by_type.values()):
        raise OptionError("At least one type has all its species prevented in wild randomization due to some option. "
                          "Please remove some restrictions in your yaml.")

    def can_evolve(spec: SpeciesEntry, level: int) -> SpeciesEntry | None:
        for evo_tup in spec.evolutions:
            evo_spec = evo_tup.species.by_form(spec.form)
            if evo_spec.dex_number == spec.dex_number:
                continue
            if evo_spec.species_name in blacklist:
                continue
            if level < (evo_tup[1] if methods[evo_tup[0]].has_level_value else 25):
                continue
            if mods.is_prevent_overpowered and sum(evo_spec.base_stats) > stats_threshold:
                continue
            return evo_spec
        return None

    if mods.is_rivals_keep_starter:

        def get_rival_last(slot: TrainerPokemonEntry) -> SpeciesEntry:
            rival_id = trainer_table[slot.trainer_id - 1].rival - 1
            stages = rivals_starter[rival_id]
            if not stages:
                stages.append(get_random(slot, ""))
                return stages[0]
            for stage in stages[:-1]:
                if not can_evolve(stage, slot.level):
                    # Checking for whether it can evolve into that specific next species isn't necessary
                    return stage
            while True:
                stage = can_evolve(stages[-1], slot.level)
                if stage and stage not in stages:
                    stages.append(stage)
                else:
                    return stages[-1]
            pass

    else:
        get_rival_last = None

    # TODO option for stricter mods enforcement, with note that it increases gen time
    # def get_viable(fbd: dict[int, list[SpeciesEntry]], slot: TrainerPokemonEntry, evo_possible: bool, prevent_op: bool,
    #                force_evo: bool, similar_stats: bool, stat_tolerance: int) -> dict[int, list[SpeciesEntry]]:
    #     ret = {}
    #     vanilla_total = sum(world.species_entries[slot.species].base_stats)
    #     for specs in fbd.values():
    #        this_specs = []
    #        for spec in specs:
    #             if evo_possible and can_evolve(spec, slot.level):
    #                 continue
    #             if prevent_op and sum(spec.base_stats) > stats_threshold:
    #                 continue
    #             if force_evo and spec.evolutions:
    #                 continue
    #             if similar_stats:

    def get_random(slot: TrainerPokemonEntry, typ: str) -> SpeciesEntry:
        stat_tolerance = world.options.pokemon_randomization_adjustments["Stats leniency"]
        op_skipped = possible_skipped = force_skipped = 0
        vanilla_total = sum(world.species_entries[slot.species].base_stats)
        while True:
            spec = (get_weighted_random_species(world.random, any_species_by_type[typ])
                    if typ else get_weighted_random_species(world.random, any_species))
            if mods.is_evolve_possible:
                evo_spec = can_evolve(spec, slot.level)
                if evo_spec:
                    if possible_skipped < 10:
                        possible_skipped += 1
                        continue
                    if typ not in evo_spec.types and possible_skipped < 20:
                        possible_skipped += 1
                        continue
                    spec = evo_spec  # Not repeating can_evolve because too much spaghetti
            if mods.is_prevent_overpowered and op_skipped < 10 and sum(spec.base_stats) > stats_threshold:
                op_skipped += 1
                continue
            if mods.is_force_evolved and force_skipped < 15 and spec.evolutions and slot.level > force_threshold:
                force_skipped += 1
                continue
            if (
                mods.is_force_not_underpowered and force_skipped < 15 and slot.level > force_threshold
                and sum(spec.base_stats) < underpowered_threshold
            ):
                force_skipped += 1
                continue
            if mods.is_similar_stats:
                if not (vanilla_total - stat_tolerance <= sum(spec.base_stats) <= vanilla_total + stat_tolerance):
                    stat_tolerance += 10
                    continue
            return spec

    for next_slot in world.trainer_teams:
        trainer = trainer_table[next_slot.trainer_id - 1]
        # Sort out rivals' last pokémon
        if rivals_starter and trainer.rival not in (0, 7) and next_slot.team_number == trainer.pokemon_count - 1:
            rivals_slots[trainer.rival - 1].append(next_slot)
            continue
        # Get type if type themed or gym
        this_type = ""
        if trainer.gym and (trainer.gym[2] or mods.is_themed_gym_trainers):
            if trainer.gym[0] not in gym_types:
                gym_types[trainer.gym[0]] = (trainer.gym[1] if not mods.is_shuffle_gym_types
                                             else world.random.choice(tuple(types_by_name)))
            this_type = gym_types[trainer.gym[0]]
        elif mods.is_type_themed:
            if not t_types[next_slot.trainer_id]:
                t_types[next_slot.trainer_id] = world.random.choice(tuple(types_by_name))
            this_type = t_types[next_slot.trainer_id]
        # Roll species
        next_slot.species = get_random(next_slot, this_type).species_name
        next_slot.write |= 2
    # fill rivals' last pokémon
    for r_slot in rivals_slots:
        r_slot.sort(key=lambda _slot: _slot.level)
    for r_slot in rivals_slots:
        for next_slot in r_slot:
            next_slot.species = get_rival_last(next_slot).species_name
            next_slot.write |= 2
