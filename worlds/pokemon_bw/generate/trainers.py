from typing import TYPE_CHECKING, Callable
from . import TrainerPokemonEntry

if TYPE_CHECKING:
    from .. import PokemonBWWorld
    from ..data import SpeciesData


def generate_trainer_teams(world: "PokemonBWWorld") -> list[TrainerPokemonEntry]:
    from ..data.trainers.pokemon import table
    from ..data.trainers.data import table as trainer_table
    from ..data.pokemon.species import by_name, get_weighted_random_species, forms_by_dex
    from ..data.pokemon.evolution_methods import methods

    if not world.options.randomize_trainer_pokemon.is_randomize:
        return [
            TrainerPokemonEntry(data.trainer_id, data.team_number, data.species)
            for data in table
        ]

    ret: list[TrainerPokemonEntry] = []
    gym_types: dict[str, str] = {}
    t_types: list[str | None] = []
    opt = world.options.randomize_trainer_pokemon
    rivals_starter: list[str | int] | None = ["", "", 0, 0] if opt.is_rivals_keep_starter else None
    stats_threshold: int = world.options.pokemon_randomization_adjustments["Overpowered threshold"]
    force_threshold: int = world.options.pokemon_randomization_adjustments["Force evolutions threshold"]
    blacklist = world.options.trainer_randomization_blacklist.value
    stats_total: Callable[["SpeciesData"], int] = lambda data: (
        data.base_hp + data.base_attack + data.base_defense +
        data.base_sp_attack + data.base_sp_defense + data.base_speed
    )
    allowed_forms_by_dex = forms_by_dex if not blacklist else {
        i: [tup for tup in forms if tup[0] not in blacklist]
        for i, forms in forms_by_dex.items()
    }
    if any(not len(value) for value in allowed_forms_by_dex.values()):
        allowed_forms_by_dex = {key: value for key, value in allowed_forms_by_dex.items() if value}

    for next_data in table:
        trainer = trainer_table[next_data.trainer_id]
        if (
            rivals_starter and trainer.rival in (1, 2) and rivals_starter[trainer.rival - 1]
            and next_data.team_number == trainer.pokemon_count - 1
        ):
            species_name = rivals_starter[trainer.rival - 1]
            species_data = by_name[species_name]
            loop = 0
            while species_data.evolutions and loop < 5:
                loop += 1
                evo_tup = species_data.evolutions[rivals_starter[trainer.rival + 1] % len(species_data.evolutions)]
                if next_data.level < (evo_tup[1] if methods[evo_tup[0]].has_level_value else 25):
                    break
                evo_name = evo_tup[2]
                if evo_name == species_name:
                    break
                evo_data = by_name[species_name]
                evo_total = stats_total(evo_data)
                if opt.is_prevent_overpowered and evo_total > stats_threshold:
                    break
                species_name, species_data = evo_name, evo_data
            ret.append(TrainerPokemonEntry(next_data.trainer_id, next_data.team_number, species_name))
            continue
        stat_tolerance = world.options.pokemon_randomization_adjustments["Stats leniency"]
        vanilla_total = stats_total(by_name[next_data.species])
        overpowered_count = 0
        themed_count = 0
        while True:
            species_name, species_data = get_weighted_random_species(world.random, allowed_forms_by_dex)
            random_total = stats_total(species_data)
            if opt.is_prevent_overpowered and random_total > stats_threshold:
                overpowered_count += 1
                continue
            if overpowered_count < 50 and themed_count < 500:
                both_types = (species_data.type_1, species_data.type_2)
                if trainer.gym and (trainer.gym[2] or opt.is_themed_gym_trainers):
                    if opt.is_shuffle_gym_types:
                        if trainer.gym[0] not in gym_types:
                            gym_types[trainer.gym[0]] = world.random.choice(both_types)
                        elif gym_types[trainer.gym[0]] not in both_types:
                            themed_count += 1
                            continue
                    elif trainer.gym[1] not in both_types:
                        themed_count += 1
                        continue
                elif opt.is_type_themed:
                    if len(t_types) <= next_data.trainer_id:
                        t_types += (None for _ in range(next_data.trainer_id-len(t_types)+1))
                    if t_types[next_data.trainer_id] is None:
                        t_types[next_data.trainer_id] = world.random.choice(both_types)
                    elif t_types[next_data.trainer_id] not in both_types:
                        themed_count += 1
                        continue
            if opt.is_force_evolved and species_data.evolutions and next_data.level >= force_threshold:
                cached_spec = ""
                loop = 0
                while species_data.evolutions and cached_spec != species_name and loop < 5:
                    cached_spec = species_name
                    loop += 1
                    evo_tups = species_data.evolutions.copy()
                    world.random.shuffle(evo_tups)
                    for evo_tup in evo_tups:
                        evo_name = evo_tup[2]
                        if evo_name == species_name:
                            continue
                        evo_data = by_name[species_name]
                        evo_total = stats_total(evo_data)
                        if opt.is_prevent_overpowered and evo_total > stats_threshold:
                            continue
                        species_name, species_data, random_total = evo_name, evo_data, evo_total
                        break
            if opt.is_evolve_possible and species_data.evolutions:
                cached_spec = ""
                loop = 0
                while species_data.evolutions and cached_spec != species_name and loop < 5:
                    cached_spec = species_name
                    loop += 1
                    evo_tups = species_data.evolutions.copy()
                    world.random.shuffle(evo_tups)
                    for evo_tup in evo_tups:
                        if next_data.level < (evo_tup[1] if methods[evo_tup[0]].has_level_value else 25):
                            continue
                        evo_name = evo_tup[2]
                        if evo_name == species_name:
                            continue
                        evo_data = by_name[species_name]
                        evo_total = stats_total(evo_data)
                        if opt.is_prevent_overpowered and evo_total > stats_threshold:
                            continue
                        species_name, species_data, random_total = evo_name, evo_data, evo_total
                        break
            if opt.is_similar_stats and random_total not in range(vanilla_total - stat_tolerance,
                                                                  vanilla_total + stat_tolerance + 1):
                stat_tolerance += 5
                continue
            ret.append(TrainerPokemonEntry(next_data.trainer_id, next_data.team_number, species_name))
            if (
                rivals_starter and trainer.rival in (1, 2) and not rivals_starter[trainer.rival-1]
                and next_data.team_number == trainer.pokemon_count-1
            ):
                rivals_starter[trainer.rival - 1] = species_name
                rivals_starter[trainer.rival + 1] = world.random.randint(10, 19)
            break

    return ret
