from typing import TYPE_CHECKING, Callable

from BaseClasses import LocationProgressType, CollectionState

from ....locations import PokemonBWLocation

if TYPE_CHECKING:
    from .... import PokemonBWWorld
    from BaseClasses import Region
    from ... import SpeciesEntry


def lookup(domain: int) -> dict[str, int]:
    from ....data.locations.sanity.shinyformsanity import table

    return {name: data.flag_id + domain for name, data in table.items()}


def create(world: "PokemonBWWorld", catchable_species_data: dict[str, "SpeciesEntry"]) -> None:
    from ....data.locations.sanity.shinyformsanity import table
    from ....data.pokemon.species import form_alias

    if not world.options.shinyformsanity:
        return

    r: "Region" = world.regions["Pokédex"]
    catchable_forms: list[str] = []
    for data in catchable_species_data.values():
        if data.dex_name not in catchable_forms:
            catchable_forms.append(data.dex_name)

    def create_location(loc_name: str, spec: str) -> None:
        l: PokemonBWLocation = PokemonBWLocation(world.player, loc_name, world.location_name_to_id[loc_name], r)
        l.progress_type = LocationProgressType.DEFAULT
        l.access_rule = lambda state: state.has(spec, world.player)
        r.locations.append(l)

    if isinstance(world.options.shinyformsanity.value, list):
        for form_name in sorted(set(world.options.shinyformsanity.value)):
            spec_name = form_alias.get(form_name, form_name)
            if spec_name in catchable_species_data:
                name = f"Pokédex - Find a shiny {form_name}"
                create_location(name, spec_name)
    else:
        catchable_forms: list[tuple[int, int]] = []
        for data in catchable_species_data.values():
            if (data.dex_number, data.form) not in catchable_forms:
                catchable_forms.append((data.dex_number, data.form))
        possible = list(it for it in table.items() if it[1].species_id in catchable_forms)
        world.random.shuffle(possible)
        count = min(world.options.shinyformsanity.value, len(possible))
        for _ in range(count):
            chosen = possible.pop()
            create_location(chosen[0], world.species_entries_by_id[chosen[1].species_id].species_name)
