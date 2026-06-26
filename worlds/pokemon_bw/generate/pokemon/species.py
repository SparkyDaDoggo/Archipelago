from typing import TYPE_CHECKING
from .. import SpeciesEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def generate_species_data(world: "PokemonBWWorld") -> dict[str, SpeciesEntry]:
    from ...data.pokemon import species
    from .evolutions import randomize_evolutions, replace_evolutions
    from .evo_plando import plando_evolutions_override, plando_evolutions_append
    from .base_stats import randomize_stats_post_evo, randomize_stats_pre_evo
    from .catch_rates import randomize_catch_rates
    from .levelup_movesets import randomize_levelup_movesets
    from .types import randomize_types_pre_evo, randomize_types_post_evo

    all_species = {name: SpeciesEntry(name, data) for name, data in species.by_name.items()}

    # Dependencies:
    # Base stats - Evolutions
    # Evolutions - Types, base stats, gender ratio
    # Types - Evolutions
    # Catch rates - Evolutions, base stats
    # Gender ratio - Evolutions
    # Levelup movesets - Evolutions, types
    # TM/HM compatibility - Evolutions, types
    # Abilities - Evolutions
    # Held items - Evolutions
    # Egg groups - Evolutions, types

    randomize_stats_pre_evo(world, all_species)
    randomize_types_pre_evo(world, all_species)
    # randomize_gender_ratio_pre_evo(world, all_species)

    replace_evolutions(world, all_species)
    plando_evolutions_override(world, all_species)
    randomize_evolutions(world, all_species)
    plando_evolutions_append(world, all_species)

    randomize_stats_post_evo(world, all_species)
    randomize_types_post_evo(world, all_species)
    # randomize_gender_ratio_post_evo(world, all_species)

    randomize_catch_rates(world, all_species)
    randomize_levelup_movesets(world, all_species)
    # randomize_tm_hm(world, all_species)
    # randomize_abilities(world, all_species)
    # randomize_held_items(world, all_species)
    # randomize_egg_groups(world, all_species)

    return all_species
