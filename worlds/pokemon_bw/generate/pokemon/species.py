from typing import TYPE_CHECKING
from .. import SpeciesEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def generate_species_data(world: "PokemonBWWorld") -> dict[str, SpeciesEntry]:
    from ...data.pokemon import species
    from .evolutions import randomize_evolutions, replace_evolutions
    from .plando import plando_evolutions_override, plando_evolutions_append

    all_species = {name: SpeciesEntry(name, data) for name, data in species.by_name.items()}

    replace_evolutions(world, all_species)
    plando_evolutions_override(world, all_species)
    randomize_evolutions(world, all_species)
    plando_evolutions_append(world, all_species)

    return all_species
