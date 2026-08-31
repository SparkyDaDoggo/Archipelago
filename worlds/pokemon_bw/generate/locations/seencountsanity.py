from typing import TYPE_CHECKING

from BaseClasses import LocationProgressType

from ...locations import PokemonBWLocation

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from BaseClasses import Region
    from .. import SpeciesEntry
    from ...data import AccessRule


def lookup(domain: int) -> dict[str, int]:
    from ...data.locations.countsanity import seencountsanity

    return {name: number + domain for name, number in seencountsanity.items()}


def create(world: "PokemonBWWorld", catchable_species_data: dict[str, "SpeciesEntry"], seeable_species_data: dict[str, "SpeciesEntry"]) -> None:
    from ...data.locations.rules import build_seen_rule

    if not world.options.seencountsanity["Maximum"]:
        return

    capped_rule = build_seen_rule(649, world)

    def get_rule(x: int) -> "AccessRule":
        if x == 649:
            return capped_rule
        return build_seen_rule(x, world)

    r: "Region" = world.regions["Pokédex"]
    option = world.options.seencountsanity
    seeable_dex = set()  # Only for counting
    for data in seeable_species_data.values():
        seeable_dex.add(data.dex_number)
    for data in catchable_species_data.values():
        seeable_dex.add(data.dex_number)
    maximum = min(len(seeable_dex), option["Maximum"])

    def create_location(count: int) -> None:
        loc_name = f"Pokédex - See {count} Pokémon"
        l: PokemonBWLocation = PokemonBWLocation(world.player, loc_name, world.location_name_to_id[loc_name], r)
        l.progress_type = LocationProgressType.DEFAULT
        l.access_rule = get_rule(count + option["Leniency"])
        r.locations.append(l)

    for c in range(1, maximum+1):
        if c % option["Steps"]:
            continue
        create_location(c)
    if maximum == option["Maximum"] and maximum % option["Steps"]:
        create_location(maximum)
