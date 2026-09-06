from typing import TYPE_CHECKING

from ...locations import PokemonBWLocation
from BaseClasses import ItemClassification
from ...items import PokemonBWItem

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from BaseClasses import Region
    from .. import SpeciesEntry


def create(world: "PokemonBWWorld") -> dict[str, "SpeciesEntry"]:
    from ...data.trainers.data import table

    seeable_species_data: dict[str, "SpeciesEntry"] = {}

    for data in world.trainer_teams:
        trainer = table[data.trainer_id - 1]
        if trainer.logic_inc_rule and not trainer.logic_inc_rule(world):
            continue
        r: "Region" = world.regions[trainer.region]
        species_data: "SpeciesEntry" = world.species_entries[data.species]
        l: PokemonBWLocation = PokemonBWLocation(
            world.player, f"[TrPkmn] {data.trainer_id}-{data.team_number}", None, r)
        item: PokemonBWItem = PokemonBWItem("[Seen] " + data.species, ItemClassification.progression, None, world.player)
        l.access_rule = world.rules_dict.get_or_add(trainer.access_rule)
        l.place_locked_item(item)
        l.show_in_spoiler = False
        r.locations.append(l)

        seeable_species_data[data.species] = species_data

    return seeable_species_data
