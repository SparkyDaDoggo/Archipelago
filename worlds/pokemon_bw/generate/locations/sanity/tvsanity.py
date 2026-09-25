from typing import TYPE_CHECKING

from ....locations import PokemonBWLocation

if TYPE_CHECKING:
    from .... import PokemonBWWorld


def lookup(domain: int) -> dict[str, int]:
    from ....data.locations.sanity.tvsanity import table

    return {
        name: (data.lines[0] if isinstance(data.lines, tuple) else data.lines) + domain for name, data in table.items()
    }


def create(world: "PokemonBWWorld") -> None:
    from ....data.locations.sanity.tvsanity import table

    all_locs = list(table)
    world.random.shuffle(all_locs)

    def create_location(loc_name: str) -> None:
        data = table[loc_name]
        region = world.regions[data.region]
        l: PokemonBWLocation = PokemonBWLocation(world.player, loc_name, world.location_name_to_id[loc_name], region)
        l.access_rule = world.rules_dict.get_or_add(data.rule)
        region.locations.append(l)

    for _ in range(world.options.tvsanity.value):
        create_location(all_locs.pop())
