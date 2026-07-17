from typing import TYPE_CHECKING
from .. import SpeciesEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def generate_species_data(world: "PokemonBWWorld") -> tuple[dict[str, SpeciesEntry], dict[tuple[int, int], SpeciesEntry]]:
    from ...data.pokemon import species
    from ...data.pokemon import pokedex
    from .evolutions import randomize_evolutions, replace_evolutions, fix_curves_stages
    from .evo_plando import plando_evolutions_override, plando_evolutions_append
    from .base_stats import randomize_stats_post_evo, randomize_stats_pre_evo
    from .catch_rates import randomize_catch_rates
    from .levelup_movesets import randomize_levelup_movesets
    from .types import randomize_types_pre_evo, randomize_types_post_evo
    from .tm_hm_compatibility import randomize_tm_hm_compat

    all_species = {name: SpeciesEntry(name, data) for name, data in species.by_name.items()}
    by_id = {(data.dex_number, data.form): data for data in all_species.values()}
    for name, data in species.by_name.items():  # Fill (pre-)evolution lists
        entry = all_species[name]
        for evo in data.evolutions:
            evo_dex = pokedex.by_name[evo[2]]
            # evo tuple gets a tuple of all base or custom form species
            evo_entries = ()
            for form in range(6):
                if (evo_dex, form) not in by_id:
                    break
                evo_entry = by_id[evo_dex, form]
                # all species, even is non-custom form, get pre-evos
                evo_entry.pre_evolutions[entry] = True
                if form and not evo_entry.is_custom_form:
                    break
                evo_entries += (evo_entry, )
            entry.evolutions.append((evo[0], evo[1], evo_entries))
            # evo tuples copy is only for reference and thereby doesn't need all entries
            entry.evolutions_copy.append((evo[0], evo[1], evo_dex))

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

    randomize_stats_pre_evo(world, all_species, by_id)
    randomize_types_pre_evo(world, all_species, by_id)
    # randomize_gender_ratio_pre_evo(world, all_species, by_id)

    replace_evolutions(world, all_species)
    plando_evolutions_override(world, all_species, by_id)
    randomize_evolutions(world, all_species, by_id)
    plando_evolutions_append(world, all_species, by_id)
    fix_curves_stages(by_id)

    randomize_stats_post_evo(world, all_species, by_id)
    randomize_types_post_evo(world, all_species, by_id)
    # randomize_gender_ratio_post_evo(world, all_species, by_id)

    randomize_catch_rates(world, all_species, by_id)
    randomize_levelup_movesets(world, all_species, by_id)
    randomize_tm_hm_compat(world, all_species, by_id)
    # randomize_abilities(world, all_species, by_id)
    # randomize_held_items(world, all_species, by_id)
    # randomize_egg_groups(world, all_species, by_id)

    return all_species, by_id
