from typing import TYPE_CHECKING

from ...locations import PokemonBWLocation
from BaseClasses import ItemClassification
from ...items import PokemonBWItem

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from BaseClasses import Region
    from .. import SpeciesEntry


def create(world: "PokemonBWWorld") -> dict[str, "SpeciesEntry"]:
    from ...data.locations import rules

    catchable_species_data: dict[str, "SpeciesEntry"] = {}
    # To remove duplicates
    available_in_region: dict[str, set[str]] = {}
    is_changeable_seasons = rules.changeable_seasons(world)
    method_offset = lambda x: (x % 12) if x < 36 else ((x - 12) % 5)

    for data in world.wild_encounter.values():
        if is_changeable_seasons or not data.encounter_region[1]:
            if data.region not in available_in_region:
                available_in_region[data.region] = set()
            r: "Region" = world.regions[data.region]
            species_data: "SpeciesEntry" = world.species_entries_by_id[data.species_id]
            species_name: str = species_data.species_name
            if species_name in available_in_region[data.region]:
                continue
            l: PokemonBWLocation = PokemonBWLocation(
                world.player, data.region + f" {method_offset(data.file_index[2])}", None, r)
            item: PokemonBWItem = PokemonBWItem(species_name, ItemClassification.progression, None, world.player)
            l.place_locked_item(item)
            l.show_in_spoiler = False
            r.locations.append(l)

            catchable_species_data[species_name] = species_data
            available_in_region[data.region].add(species_name)

    return catchable_species_data
