from typing import TYPE_CHECKING, Callable

from BaseClasses import LocationProgressType, CollectionState

from ....locations import PokemonBWLocation

if TYPE_CHECKING:
    from .... import PokemonBWWorld
    from BaseClasses import Region
    from ... import SpeciesEntry


def lookup(domain: int) -> dict[str, int]:
    from ....data.locations.sanity.dexsanity import location_table

    return {name: data.dex_number + domain for name, data in location_table.items()}


def create(world: "PokemonBWWorld", catchable_species_data: dict[str, "SpeciesEntry"]) -> None:
    from ....data.locations.sanity.dexsanity import location_table
    from ....data.pokemon.pokedex import by_number

    if not world.options.dexsanity:
        return

    def get_rule(dex: int) -> Callable[[CollectionState], bool]:
        all_forms = tuple(f.species_name for f in world.species_entries_by_id[dex, 0].all_forms if f)
        return lambda state: state.has_any(all_forms, world.player)

    r: "Region" = world.regions["Pokédex"]
    catchable_dex: list[str] = []
    dexsanity_numbers: list[int] = []
    for data in catchable_species_data.values():
        if data.dex_name not in catchable_dex:
            catchable_dex.append(data.dex_name)

    def create_location(loc_name: str) -> None:
        data = location_table[loc_name]
        dexsanity_numbers.append(data.dex_number)
        l: PokemonBWLocation = PokemonBWLocation(world.player, loc_name, world.location_name_to_id[loc_name], r)
        l.progress_type = LocationProgressType.DEFAULT
        l.access_rule = get_rule(data.dex_number)
        if data.ut_alias is not None:
            world.location_id_to_alias[world.location_name_to_id[loc_name]] = data.ut_alias
        r.locations.append(l)

    if isinstance(world.options.dexsanity.value, list):
        for dex_num in sorted(set(world.options.dexsanity.value)):
            dex_num: int
            pokemon = by_number[dex_num]
            if pokemon in catchable_dex:
                name = f"Pokédex - {pokemon}"
                create_location(name)
    else:
        world.random.shuffle(catchable_dex)
        count = min(world.options.dexsanity.value, len(catchable_dex))
        for _ in range(count):
            name = f"Pokédex - {catchable_dex.pop()}"
            create_location(name)

    world.dexsanity_numbers.extend(dexsanity_numbers)
