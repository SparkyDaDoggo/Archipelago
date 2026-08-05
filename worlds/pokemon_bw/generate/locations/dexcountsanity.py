from typing import TYPE_CHECKING, Callable

from BaseClasses import LocationProgressType, CollectionState

from ...locations import PokemonBWLocation

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from BaseClasses import Region
    from .. import SpeciesEntry


def lookup(domain: int) -> dict[str, int]:
    from ...data.locations.dexcountsanity import location_table

    return {name: number + domain for name, number in location_table.items()}


def create(world: "PokemonBWWorld", catchable_species_data: dict[str, "SpeciesEntry"]) -> None:
    from ...data.pokemon.species import forms_by_dex

    def build_rule(x: int) -> Callable[[CollectionState], bool]:
        def r(state: CollectionState) -> bool:
            found: int = 0
            prog_items = state.prog_items[world.player]
            for forms_list in forms_by_dex.values():
                for form in forms_list:
                    if prog_items[form]:
                        found += 1
                        break
                if found >= x:
                    return True
            return False
        return r

    capped_rule = build_rule(649)

    def get_rule(x: int) -> Callable[[CollectionState], bool]:
        if x == 649:
            return capped_rule
        return build_rule(x)

    r: "Region" = world.regions["Pokédex"]
    option = world.options.dexcountsanity
    catchable_dex = set()  # Only for counting
    for data in catchable_species_data.values():
        catchable_dex.add(data.dex_number)
    maximum = min(len(catchable_dex), option["Maximum"])

    def create_location(count: int) -> None:
        loc_name = f"Pokédex - Catch {count} Pokémon"
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
