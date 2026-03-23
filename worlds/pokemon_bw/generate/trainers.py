from typing import TYPE_CHECKING, Callable
from . import TrainerPokemonEntry

if TYPE_CHECKING:
    from .. import PokemonBWWorld
    from ..data import SpeciesData


def generate_trainer_teams(world: "PokemonBWWorld") -> list[TrainerPokemonEntry]:
    from ..data.trainers.pokemon import table
    from ..data.pokemon.species import by_name, get_weighted_random_species, forms_by_dex
    from ..data.pokemon.evolution_methods import methods

    if not world.options.randomize_trainer_pokemon.is_randomize:
        return [
            TrainerPokemonEntry(data.trainer_id, data.team_number, data.species)
            for data in table
        ]

    ret: list[TrainerPokemonEntry] = []
    similar_base_stats = world.options.randomize_trainer_pokemon.is_similar_stats
    prevent_overpowered = world.options.randomize_trainer_pokemon.is_prevent_overpowered
    evolve_if_possible = world.options.randomize_trainer_pokemon.is_evolve_possible
    force_evolve = world.options.randomize_trainer_pokemon.is_force_evolved
    stats_threshold: int = world.options.pokemon_randomization_adjustments["Overpowered threshold"]
    force_threshold: int = world.options.pokemon_randomization_adjustments["Force evolutions threshold"]
    stats_total: Callable[["SpeciesData"], int] = lambda data: (
        data.base_hp + data.base_attack + data.base_defense +
        data.base_sp_attack + data.base_sp_defense + data.base_speed
    )

    for next_data in table:
        stat_tolerance = world.options.pokemon_randomization_adjustments["Stats leniency"]
        vanilla_total = stats_total(by_name[next_data.species])
        while True:
            species_name, species_data = get_weighted_random_species(world.random, forms_by_dex)
            random_total = stats_total(species_data)
            if prevent_overpowered and random_total > stats_threshold:
                continue
            if force_evolve and species_data.evolutions and next_data.level >= force_threshold:
                while species_data.evolutions:
                    evo_tups = species_data.evolutions.copy()
                    world.random.shuffle(evo_tups)
                    for evo_tup in evo_tups:
                        evo_name = evo_tup[2]
                        evo_data = by_name[species_name]
                        evo_total = stats_total(evo_data)
                        if prevent_overpowered and evo_total > stats_threshold:
                            continue
                        species_name, species_data, random_total = evo_name, evo_data, evo_total
                        break
            if evolve_if_possible and species_data.evolutions:
                while species_data.evolutions:
                    evo_tups = species_data.evolutions.copy()
                    world.random.shuffle(evo_tups)
                    for evo_tup in evo_tups:
                        if next_data.level < (evo_tup[1] if methods[evo_tup[0]].has_level_value else 25):
                            continue
                        evo_name = evo_tup[2]
                        evo_data = by_name[species_name]
                        evo_total = stats_total(evo_data)
                        if prevent_overpowered and evo_total > stats_threshold:
                            continue
                        species_name, species_data, random_total = evo_name, evo_data, evo_total
                        break
            if similar_base_stats and random_total not in range(vanilla_total - stat_tolerance,
                                                                vanilla_total + stat_tolerance + 1):
                stat_tolerance += 5
                continue
            ret.append(TrainerPokemonEntry(next_data.trainer_id, next_data.team_number, species_name))
            break

    return ret
