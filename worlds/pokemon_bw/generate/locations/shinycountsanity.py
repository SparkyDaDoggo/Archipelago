from typing import TYPE_CHECKING

from BaseClasses import LocationProgressType

from ...locations import PokemonBWLocation

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from BaseClasses import Region
    from .. import SpeciesEntry
    from ...data import AccessRule


def lookup(domain: int) -> dict[str, int]:
    from ...data.locations.countsanity import shinycountsanity

    return {name: number + domain for name, number in shinycountsanity.items()}


def create(world: "PokemonBWWorld", catchable_species_data: dict[str, "SpeciesEntry"]) -> None:
    from ...data.locations.rules import build_caught_rule

    option_value = world.options.shinycountsanity.value
    if isinstance(option_value, int):
        option_value = {
            "Maximum": option_value,
            "Steps": 1,
            "Leniency": 0,
        }
    if not option_value["Maximum"]:
        return

    capped_rule = build_caught_rule(649, world)

    def get_rule(x: int) -> "AccessRule":
        if x == 649:
            return capped_rule
        return build_caught_rule(x, world)

    r: "Region" = world.regions["Pokédex"]
    catchable_dex = set()  # Only for counting
    for data in catchable_species_data.values():
        catchable_dex.add(data.dex_number)
    maximum = min(len(catchable_dex), option_value["Maximum"])

    def create_location(count: int) -> None:
        loc_name = f"Pokédex - See {count} shiny Pokémon"
        l: PokemonBWLocation = PokemonBWLocation(world.player, loc_name, world.location_name_to_id[loc_name], r)
        l.progress_type = LocationProgressType.DEFAULT
        l.access_rule = get_rule(count + option_value["Leniency"])
        r.locations.append(l)

    for c in range(1, maximum+1):
        if c % option_value["Steps"]:
            continue
        create_location(c)
    if maximum == option_value["Maximum"] and maximum % option_value["Steps"]:
        create_location(maximum)
