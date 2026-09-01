from typing import TYPE_CHECKING
from .. import SpeciesEntry, EvolutionsEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def generate_species_data(world: "PokemonBWWorld") -> tuple[dict[str, SpeciesEntry], dict[tuple[int, int], SpeciesEntry]]:
    from ...data.pokemon import species
    from ...data.pokemon import pokedex
    from .evolutions import randomize_evolutions, replace_evolutions, fix_curves_stages_order
    from .evolutions_plando import plando_evolutions
    from .base_stats import randomize_stats_post_evo, randomize_stats_pre_evo
    from .catch_rates import randomize_catch_rates
    from .levelup_movesets import randomize_levelup_movesets
    from .types import randomize_types_pre_evo, randomize_types_post_evo
    from .tm_hm_compatibility import randomize_tm_hm_compat
    from .egg_groups import randomize_egg_groups
    from .egg_species import randomize_egg_species

    all_species = {name: SpeciesEntry(name, data) for name, data in species.by_name.items()}
    by_id = {(data.dex_number, data.form): data for data in all_species.values()}
    for name, entry in all_species.items():  # Fill (pre-)evolution lists
        if not entry.form:
            entry.evolutions = []
            entry.all_forms = [entry]
            for evo in entry.evolutions_copy:
                evo_dex = pokedex.by_name[evo[2]]
                evo_entry = by_id[evo_dex, 0]
                entry.evolutions.append(EvolutionsEntry(evo[0], evo[1], evo_entry))
                evo_entry.pre_evolutions[entry] = True
        else:
            base_entry = by_id[entry.dex_number, 0]
            entry.evolutions = base_entry.evolutions
            entry.pre_evolutions = base_entry.pre_evolutions
            entry.all_forms = base_entry.all_forms
            assert len(entry.all_forms) == entry.form
            entry.all_forms.append(entry)
            if not entry.is_custom_form:
                entry.level_up_moves = base_entry.level_up_moves
                entry.tm_hm_moves = base_entry.tm_hm_moves

    # Dependencies:
    # Base stats - Evolutions
    # Evolutions - Types, base stats, gender ratio
    # Types - Evolutions
    # Catch rates - Evolutions, base stats
    # Gender ratio - Evolutions
    # Levelup movesets - Evolutions, types
    # TM/HM compatibility - Evolutions, types
    # Egg groups - Evolutions, types
    # Abilities - Evolutions
    # Held items - Evolutions

    randomize_stats_pre_evo(world, all_species)
    randomize_types_pre_evo(world, all_species)
    # randomize_gender_ratio_pre_evo(world, all_species, by_id)

    replace_evolutions(world, all_species)
    plando_evolutions(world, all_species, by_id)
    randomize_evolutions(world, by_id)
    fix_curves_stages_order(by_id)

    randomize_stats_post_evo(world, all_species)
    randomize_types_post_evo(world, all_species)
    # randomize_gender_ratio_post_evo(world, all_species, by_id)

    randomize_catch_rates(world, all_species)
    randomize_levelup_movesets(world, all_species)
    randomize_tm_hm_compat(world, all_species)
    randomize_egg_groups(world, all_species)
    randomize_egg_species(world, all_species, by_id)
    # randomize_abilities(world, all_species, by_id)
    # randomize_held_items(world, all_species, by_id)

    return all_species, by_id
