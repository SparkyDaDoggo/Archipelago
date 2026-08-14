from typing import TYPE_CHECKING

from ...locations import PokemonBWLocation
from BaseClasses import ItemClassification
from ...items import PokemonBWItem

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from BaseClasses import Region
    from .. import SpeciesEntry


def create(world: "PokemonBWWorld") -> dict[str, "SpeciesEntry"]:
    from ...data.pokemon.species import by_id as species_by_id

    catchable_species_data: dict[str, "SpeciesEntry"] = {}
    # To remove duplicates
    available_in_region: dict[str, set[str]] = {}

    for data in world.wild_encounter.values():
        if data.encounter_region in world.regions:
            if data.region not in available_in_region:
                available_in_region[data.region] = set()
            r: "Region" = world.regions[data.region]
            species_name: str = species_by_id[data.species_id].species_name
            if species_name in available_in_region[data.region]:
                continue
            l: PokemonBWLocation = PokemonBWLocation(world.player, data.region + f" {data.file_index[2]}", None, r)
            item: PokemonBWItem = PokemonBWItem(species_name, ItemClassification.progression, None, world.player)
            l.place_locked_item(item)
            l.show_in_spoiler = False
            r.locations.append(l)

            species_data: "SpeciesEntry" = world.species_entries[species_name]
            catchable_species_data[species_name] = species_data
            available_in_region[data.region].add(species_name)

    return catchable_species_data
