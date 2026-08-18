from typing import TYPE_CHECKING, Callable

from BaseClasses import LocationProgressType, CollectionState

from ...locations import PokemonBWLocation

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from BaseClasses import Region
    from .. import SpeciesEntry


def lookup(domain: int) -> dict[str, int]:
    from ...data.locations.shinysanity import location_table

    return {name: data.dex_number + domain for name, data in location_table.items()}


def create(world: "PokemonBWWorld", catchable_species_data: dict[str, "SpeciesEntry"]) -> None:
    from ...data.locations.shinysanity import location_table
    from ...data.pokemon.pokedex import by_number

    # These lambdas have to be created from functions, because else they would all use the same 'name' variable
    def get_standard_rule(dex_name: str) -> Callable[[CollectionState], bool]:
        return lambda state: state.has(dex_name, world.player)

    def get_special_rule(x: str) -> Callable[[CollectionState], bool]:
        sp = location_table[x].special_rule
        return lambda state: sp(state, world)

    r: "Region" = world.regions["Pokédex"]
    catchable_dex: list[str] = []
    for data in catchable_species_data.values():
        if data.dex_name not in catchable_dex:
            catchable_dex.append(data.dex_name)

    def create_location(loc_name: str, dex_name: str) -> None:
        data = location_table[loc_name]
        l: PokemonBWLocation = PokemonBWLocation(world.player, loc_name, world.location_name_to_id[loc_name], r)
        l.progress_type = LocationProgressType.DEFAULT
        if data.special_rule is not None:
            l.access_rule = get_special_rule(loc_name)
        else:
            l.access_rule = get_standard_rule(dex_name)
        if data.ut_alias is not None:
            world.location_id_to_alias[world.location_name_to_id[loc_name]] = data.ut_alias
        r.locations.append(l)

    if isinstance(world.options.shinysanity.value, list):
        for dex_num in world.options.shinysanity.value:
            dex_num: int
            pokemon = by_number[dex_num]
            if pokemon in catchable_dex:
                name = f"Pokédex - Find a shiny {pokemon}"
                create_location(name, pokemon)
    else:
        world.random.shuffle(catchable_dex)
        count = min(world.options.shinysanity.value, len(catchable_dex))
        for _ in range(count):
            pokemon = catchable_dex.pop()
            name = f"Pokédex - Find a shiny {pokemon}"
            create_location(name, pokemon)
