import itertools
from typing import TYPE_CHECKING

from Options import OptionError
from .. import EncounterEntry, SpeciesChecklist, CopyChecklist, SpeciesEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld

prepare = 25350666777563370117040793671783381956473107378414503005100223998849054326267652480678608918097127753


def organize_by_method(world: "PokemonBWWorld") -> dict[str, list[int]]:
    # {method: ([species names], [dex numbers])}
    ret: dict[str, list[int]] = {}
    for data in world.wild_encounter.values():
        if data.encounter_region not in ret:
            ret[data.region] = []
        if data.species_id[0] not in ret[data.region]:
            ret[data.region].append(data.species_id[0])
    for static_slot, entry in world.static_encounter.items():
        ret[static_slot] = [entry.species_id[0]]
    for trade_slot, trade_entry in world.trade_encounter.items():
        ret[trade_slot] = [trade_entry.species_id[0]]
    return ret


def organize_trades(world: "PokemonBWWorld") -> dict[str, tuple[int, int]]:
    return {trade_slot: (trade_entry.species_id[0], trade_entry.wanted_dex_number)
            for trade_slot, trade_entry in world.trade_encounter.items()}


def generate_wild_encounters(world: "PokemonBWWorld",
                             species_checklist: SpeciesChecklist,
                             copy_checklist: CopyChecklist):
    from ...data.pokemon.species import forms_by_dex, get_weighted_random_species
    from ...data.pokemon.types import by_name as types_by_name
    from ...data.locations import rules

    if not world.options.randomize_wild_pokemon.is_randomize:
        return

    logic_slots: list[EncounterEntry] = []
    other_slots: list[EncounterEntry] = []
    copy_slots: list[EncounterEntry] = []
    is_vanilla_seasons = rules.vanilla_seasons(world)
    for entry in world.wild_encounter.values():
        if entry.write & 2:
            continue
        group = copy_checklist[entry.file_index]
        if group and group.search().head != entry:
            copy_slots.append(entry)
        elif entry.encounter_region[1] and is_vanilla_seasons:
            other_slots.append(entry)
        else:
            logic_slots.append(entry)
    world.random.shuffle(logic_slots)
    world.random.shuffle(other_slots)

    mods = world.options.randomize_wild_pokemon
    stats_threshold: int = world.options.pokemon_randomization_adjustments["Overpowered threshold"]
    blacklist = world.options.wild_randomization_blacklist.value
    area_types: dict[str, str] = {}

    # Devolve overpowered species, might be able to reduce the species list a bit
    if mods.is_prevent_overpowered and world.options.modify_logic.is_consider_evos:

        def try_devolve(_entry: SpeciesEntry):
            stats_total = sum(_entry.base_stats)
            if stats_total <= stats_threshold:
                return
            for pre_entry in _entry.pre_evolutions:
                if pre_entry.dex_number == _entry.dex_number:  # Same species
                    continue
                # Same-stat pre evos not allowed because of looping evo lines with all members having same stats
                if not pre_entry.has_form(_entry.form) or sum(pre_entry.base_stats) >= stats_total:
                    continue
                # Make sure the evolution is not Level up with party member, which we will not touch
                for evo_tuple in pre_entry.evolutions:
                    if _entry.dex_number == evo_tuple.species.dex_number and evo_tuple.method != "Level up with party member":
                        break
                else:
                    continue
                species_checklist.check(_entry)
                species_checklist.add(pre_entry)
                try_devolve(pre_entry)
                return

        for spec_entry in species_checklist.copy_list():
            try_devolve(spec_entry)

    if len(species_checklist) > len(logic_slots):
        if world.options.modify_logic.is_consider_evos:
            for species_data in species_checklist.copy_list():
                for evolution in species_data.evolutions:
                    if evolution.method == "Level up with party member":
                        continue
                    species_checklist.check(evolution.species.by_form(species_data.form))
        if len(species_checklist) > len(logic_slots):
            raise OptionError(
                f"More required species for randomized wild encounter than slots they could be placed in "
                f"for player {world.player_name}: {len(species_checklist)} > {len(logic_slots)}.\n"
                f"Please remove some restrictive options or tweak the \"Modify Logic\" option."
            )

    while len(species_checklist) > 0:
        spec_entry = world.random.choice(species_checklist.to_check)
        # Reload stat tolerance every time, it might be increased
        stat_tolerance = world.options.pokemon_randomization_adjustments["Stats leniency"]
        skip_type = skip_bad = False
        while True:
            skipped_stat = skipped_type = skipped_bad = False
            for slot in logic_slots:
                # Why this order:
                # Stats increase is not that bad, so this first
                # Skipping themed areas is bad game design, but still manageable
                # If Shedinja should be banned from early areas, then only allow as last resort
                if mods.is_prevent_bad_early and not skip_bad:
                    if world.region_distances[slot.region] / world.max_distance <= 0.2:
                        if "Wonder Guard" in spec_entry.abilities:
                            skipped_bad = True
                            continue
                        moveset = spec_entry.level_up_moves.level_up_moves
                        if any((move_learn[1] in ("Sonic Boom", "Dragon Rage")) for move_learn in moveset):
                            skipped_bad = True
                            continue
                if mods.is_type_themed_areas and not skip_type:
                    area = slot.encounter_region[0]
                    if area not in area_types:
                        area_types[area] = world.random.choice(spec_entry.types)
                    elif area_types[area] not in spec_entry.types:
                        skipped_type = True
                        continue
                if mods.is_similar_stats:  # stats last because it's more lenient than others
                    random_stats = sum(spec_entry.base_stats)
                    vanilla_stats = sum(world.species_entries_by_id[slot.species_id].base_stats)
                    if random_stats not in range(vanilla_stats - stat_tolerance, vanilla_stats + stat_tolerance + 1):
                        skipped_stat = True
                        continue
                slot.species_id = spec_entry.dex_number, spec_entry.form
                slot.write |= 2
                species_checklist.check(spec_entry)
                logic_slots.remove(slot)
                break
            else:
                if skipped_stat:
                    stat_tolerance += 10
                elif skipped_type:
                    # Force place into any slot that still kinda fits
                    skip_type = True
                elif skipped_bad:
                    # I really hope that this will only ever happen if someone heavily abuses encounter plando
                    skip_bad = True
                else:
                    # Should be unreachable
                    raise Exception
                continue
            break

    any_species_by_type: dict[str, dict[int, list[SpeciesEntry]]] = {t: {} for t in types_by_name}
    any_species: dict[int, list[SpeciesEntry]] = {}
    if not world.random.randint(0, 999) and len(set(w.game for w in world.multiworld.worlds.values())) > 3:
        print(world.prepare_text(prepare))
    if mods.is_type_themed_areas:
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
    else:
        for dex, species_names in forms_by_dex.items():
            if mods.is_prevent_overpowered:
                all_forms = [spec_entry for spec_entry in
                             (world.species_entries[s_name] for s_name in species_names if s_name not in blacklist)
                             if sum(spec_entry.base_stats) <= stats_threshold]
            else:
                all_forms = [world.species_entries[s_name] for s_name in species_names if s_name not in blacklist]
            if all_forms:
                any_species[dex] = all_forms
    if mods.is_type_themed_areas and not all(any_species_by_type.values()):
        raise OptionError("At least one type has all its species prevented in wild randomization due to some option. "
                          "Please remove some restrictions in your yaml.")
    for slot in itertools.chain(logic_slots, other_slots):
        stat_tolerance = world.options.pokemon_randomization_adjustments["Stats leniency"]
        area = slot.encounter_region[0]
        while True:
            current_any_species = any_species
            if mods.is_type_themed_areas:
                if area not in area_types:
                    area_types[area] = world.random.choice(tuple(types_by_name))
                current_any_species = any_species_by_type[area_types[area]]
            random_spec = get_weighted_random_species(world.random, current_any_species)
            if mods.is_prevent_bad_early:
                if world.region_distances[slot.region] / world.max_distance <= 0.2:
                    if "Wonder Guard" in random_spec.abilities:
                        continue
                    moveset = random_spec.level_up_moves.level_up_moves
                    if any((move_learn[1] in ("Sonic Boom", "Dragon Rage")) for move_learn in moveset):
                        continue
            if mods.is_similar_stats:  # stats last because it's more lenient than others
                random_stats = sum(random_spec.base_stats)
                vanilla_stats = sum(world.species_entries_by_id[slot.species_id].base_stats)
                if random_stats not in range(vanilla_stats - stat_tolerance, vanilla_stats + stat_tolerance + 1):
                    stat_tolerance += 10
                    continue
            slot.species_id = random_spec.dex_number, random_spec.form
            slot.write |= 2
            break
    for slot in copy_slots:
        group = copy_checklist[slot.file_index].search()  # group is here definitely not None
        slot.species_id = group.head.species_id
        slot.write |= 2
