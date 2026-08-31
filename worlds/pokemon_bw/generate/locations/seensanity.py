from typing import TYPE_CHECKING, Callable

from BaseClasses import LocationProgressType, CollectionState

from ...locations import PokemonBWLocation

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from BaseClasses import Region
    from .. import SpeciesEntry


def lookup(domain: int) -> dict[str, int]:
    from ...data.locations.seensanity import location_table

    return {name: data.dex_number + domain for name, data in location_table.items()}


def create(world: "PokemonBWWorld", catchable_species_data: dict[str, "SpeciesEntry"], seeable_species_data: dict[str, "SpeciesEntry"]) -> None:
    from ...data.locations.seensanity import location_table
    from ...data.pokemon.pokedex import by_number

    if not world.options.seensanity:
        return

    def get_rule(dex: int) -> Callable[[CollectionState], bool]:
        all_forms = world.species_entries_by_id[dex, 0].all_forms
        return lambda state: state.has_any((prefix + f for f in all_forms for prefix in ("", "[Seen] ")), world.player)

    r: "Region" = world.regions["Pokédex"]
    seeable_dex: list[str] = []
    for data in seeable_species_data.values():
        if data.dex_name not in seeable_dex:
            seeable_dex.append(data.dex_name)
    for data in catchable_species_data.values():
        if data.dex_name not in seeable_dex:
            seeable_dex.append(data.dex_name)

    def create_location(loc_name: str) -> None:
        loc_data = location_table[loc_name]
        l: PokemonBWLocation = PokemonBWLocation(world.player, loc_name, world.location_name_to_id[loc_name], r)
        l.progress_type = LocationProgressType.DEFAULT
        l.access_rule = get_rule(loc_data.dex_number)
        if loc_data.ut_alias is not None:
            world.location_id_to_alias[world.location_name_to_id[loc_name]] = loc_data.ut_alias
        r.locations.append(l)

    if isinstance(world.options.seensanity.value, list):
        for dex_num in sorted(set(world.options.seensanity.value)):
            dex_num: int
            pokemon = by_number[dex_num]
            if pokemon in seeable_dex:
                a_an = "an" if pokemon[0] in "AEIOU" and pokemon != "Uxie" else "a"
                name = f"Pokédex - See {a_an} {pokemon}"
                create_location(name)
    else:
        world.random.shuffle(seeable_dex)
        count = min(world.options.seensanity.value, len(seeable_dex))
        for _ in range(count):
            chosen = seeable_dex.pop()
            a_an = "an" if chosen[0] in "AEIOU" and chosen != "Uxie" else "a"
            name = f"Pokédex - See {a_an} {chosen}"
            create_location(name)
