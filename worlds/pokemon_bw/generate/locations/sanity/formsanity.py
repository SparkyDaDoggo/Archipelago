from typing import TYPE_CHECKING, Callable

from BaseClasses import LocationProgressType, CollectionState

from ....locations import PokemonBWLocation

if TYPE_CHECKING:
    from .... import PokemonBWWorld
    from BaseClasses import Region
    from ... import SpeciesEntry


def lookup(domain: int) -> dict[str, int]:
    from ....data.locations.sanity.formsanity import table

    return {name: data.flag_id + domain for name, data in table.items()}


def create(world: "PokemonBWWorld", catchable_species_data: dict[str, "SpeciesEntry"],
           seeable_species_data: dict[str, "SpeciesEntry"]) -> None:
    from ....data.locations.sanity.formsanity import table
    from ....data.pokemon.species import form_alias, forms_by_dex

    if not world.options.formsanity:
        return

    r: "Region" = world.regions["Pokédex"]
    formsanity_ids: list[int] = []
    full_formsanity_pokemon: list[int] = []
    poke_forms_counts: dict[int, int] = {}

    def create_location(loc_name: str, spec: str) -> None:
        loc_data = table[loc_name]
        l: PokemonBWLocation = PokemonBWLocation(world.player, loc_name, world.location_name_to_id[loc_name], r)
        l.progress_type = LocationProgressType.DEFAULT
        l.access_rule = lambda state: state.has_any((spec, "[Seen] " + spec), world.player)
        r.locations.append(l)
        formsanity_ids.append(loc_data.flag_id)
        poke_forms_counts[loc_data.species_id[0]] = poke_forms_counts.get(loc_data.species_id[0], 0) + 1

    if isinstance(world.options.formsanity.value, list):
        for form_name in world.options.formsanity.value:
            spec_name = form_alias.get(form_name, form_name)
            if spec_name in seeable_species_data or spec_name in catchable_species_data:
                a_an = "an" if form_name[0] in "AEIOU" else "a"
                name = f"Pokédex - See {a_an} {form_name}"
                create_location(name, spec_name)
    else:
        seeable_forms: list[tuple[int, int]] = []
        for data in seeable_species_data.values():
            if (data.dex_number, data.form) not in seeable_forms:
                seeable_forms.append((data.dex_number, data.form))
        for data in catchable_species_data.values():
            if (data.dex_number, data.form) not in seeable_forms:
                seeable_forms.append((data.dex_number, data.form))
        possible = list(it for it in table.items() if it[1].species_id in seeable_forms)
        world.random.shuffle(possible)
        count = min(world.options.formsanity.value, len(possible))
        for _ in range(count):
            chosen = possible.pop()
            create_location(chosen[0], world.species_entries_by_id[chosen[1].species_id].species_name)

    for dex, count in poke_forms_counts.items():
        if count >= len(forms_by_dex[dex]):
            full_formsanity_pokemon.append(dex)
    world.disallowed_all_seen.extend(dex for dex in full_formsanity_pokemon if dex not in world.disallowed_all_seen)
