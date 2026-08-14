from typing import TYPE_CHECKING

from ...locations import PokemonBWLocation

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from BaseClasses import Region, LocationProgressType


def lookup(domain: int) -> dict[str, int]:
    from ...data.locations.visitsanity import table

    return {
        name: data.map_id + domain for name, data in table.items()
    }


def create(world: "PokemonBWWorld") -> None:
    from ...data.locations.visitsanity import table

    r: "Region" = world.regions["Map Visits"]
    all_locs = list(table)
    world.random.shuffle(all_locs)

    def create_location(loc_name: str) -> None:
        data = table[loc_name]
        if len(data.regions) == 1:
            l: PokemonBWLocation = PokemonBWLocation(world.player, loc_name, world.location_name_to_id[loc_name], world.regions[data.regions[0]])
            l.progress_type = LocationProgressType.DEFAULT
        else:
            l: PokemonBWLocation = PokemonBWLocation(world.player, loc_name, world.location_name_to_id[loc_name], r)
            l.progress_type = LocationProgressType.DEFAULT
            l.access_rule = lambda state: any(state.can_reach_region(reg, world.player) for reg in data.regions)
        r.locations.append(l)

    for _ in range(world.options.visitsanity.value):
        create_location(all_locs.pop())
