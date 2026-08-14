from typing import TYPE_CHECKING

from ...locations import PokemonBWLocation
from BaseClasses import ItemClassification
from ...items import PokemonBWItem

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def create(world: "PokemonBWWorld") -> None:
    from ...data.locations.story_events import table

    for data in table:
        if data.inclusion_rule and not data.inclusion_rule(world):
            continue
        name = "[Event] " + data.name
        loc = PokemonBWLocation(world.player, name, None, world.regions[data.region])
        world.regions[data.region].locations.append(loc)
        loc.place_locked_item(
            PokemonBWItem(name, ItemClassification.progression, None, world.player)
        )
        if data.access_rule is not None:
            loc.access_rule = world.rules_dict.get_or_add(data.access_rule)
