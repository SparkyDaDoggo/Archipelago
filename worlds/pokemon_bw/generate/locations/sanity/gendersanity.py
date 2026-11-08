from typing import TYPE_CHECKING, Callable

from BaseClasses import CollectionState

from ....locations import PokemonBWLocation

if TYPE_CHECKING:
    from .... import PokemonBWWorld
    from BaseClasses import Region
    from ... import SpeciesEntry


def lookup(domain: int) -> dict[str, int]:
    from ....data.locations.sanity.gendersanity import location_table

    return {name: data.dex_number * 2 + bool(data.gender) + domain for name, data in location_table.items()}


def create(world: "PokemonBWWorld", catchable_species_data: dict[str, "SpeciesEntry"],
           seeable_species_data: dict[str, "SpeciesEntry"]) -> None:
    from ....data.locations.sanity.gendersanity import location_table
    from ....data.pokemon.pokedex import by_number

    if not world.options.gendersanity:
        return

    def get_rule(dex: int) -> Callable[[CollectionState], bool]:
        all_forms = tuple(prefix + f.species_name for f in world.species_entries_by_id[dex, 0].all_forms
                          for prefix in ("", "[Seen] ") if f)
        if len(all_forms) > 1:
            return lambda state: state.has_any(all_forms, world.player)
        else:
            f = all_forms[0]
            return lambda state: state.has_any((f, "[Seen] " + f), world.player)

    r: "Region" = world.regions["Pokédex"]
    genderable_dex: list[str] = []
    male_loc_dexgend_numbers: list[int] = []
    female_loc_dexgend_numbers: list[int] = []
    for data in seeable_species_data.values():
        if data.dex_name not in genderable_dex and data.gender_ratio in world.options.gendersanity.gender_threshold:
            genderable_dex.append(data.dex_name)
    for data in catchable_species_data.values():
        if data.dex_name not in genderable_dex and data.gender_ratio in world.options.gendersanity.gender_threshold:
            genderable_dex.append(data.dex_name)

    def create_location(loc_name: str) -> None:
        loc_data = location_table[loc_name]
        l: PokemonBWLocation = PokemonBWLocation(world.player, loc_name, world.location_name_to_id[loc_name], r)
        l.access_rule = get_rule(loc_data.dex_number)
        if loc_data.ut_alias is not None:
            world.location_id_to_alias[world.location_name_to_id[loc_name]] = loc_data.ut_alias
        r.locations.append(l)
        if loc_data.gender:
            female_loc_dexgend_numbers.append(loc_data.dex_number + 1024)
        else:
            male_loc_dexgend_numbers.append(loc_data.dex_number)

    if isinstance(world.options.gendersanity.value, list):
        for dex_num, gender_id in sorted(set(world.options.gendersanity.value)):
            dex_num: int
            gender_id: int
            pokemon = by_number[dex_num]
            if pokemon in genderable_dex:
                gender = "female" if gender_id else "male"
                create_location(f"Pokédex - See a {gender} {pokemon}")
    else:
        possible = [(p, g) for g in ("male", "female") for p in genderable_dex]
        world.random.shuffle(possible)
        for _ in range(min(world.options.gendersanity.value, len(possible))):
            chosen = possible.pop()
            create_location(f"Pokédex - See a {chosen[1]} {chosen[0]}")

    disallowed = [dex for dex in male_loc_dexgend_numbers if dex + 1024 in female_loc_dexgend_numbers]
    world.disallowed_all_seen_male.extend(male_loc_dexgend_numbers)
    world.disallowed_all_seen_female.extend(female_loc_dexgend_numbers)
    world.disallowed_all_seen.extend(dex for dex in disallowed if dex not in world.disallowed_all_seen)
    world.dexsanity_numbers["gendersanity"] = male_loc_dexgend_numbers + female_loc_dexgend_numbers
