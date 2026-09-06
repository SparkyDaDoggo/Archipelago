from typing import TYPE_CHECKING

from BaseClasses import LocationProgressType

from ....locations import PokemonBWLocation
from ....data import AccessRule

if TYPE_CHECKING:
    from .... import PokemonBWWorld
    from BaseClasses import Region
    from ... import SpeciesEntry


def lookup(domain: int) -> dict[str, int]:
    from ....data.locations.sanity.countsanity import formcountsanity

    return {name: number + domain for name, number in formcountsanity.items()}


def create(world: "PokemonBWWorld", catchable_species_data: dict[str, "SpeciesEntry"],
           seeable_species_data: dict[str, "SpeciesEntry"]) -> None:
    from ....data.pokemon.species import unique_forms, form_alias
    from ....data.locations.rules import build_form_seen_rule

    option_value = world.options.formcountsanity.value
    if isinstance(option_value, int):
        option_value = {
            "Maximum": option_value,
            "Steps": 1,
            "Leniency": 0,
        }
    if not option_value["Maximum"]:
        return

    r: "Region" = world.regions["Pokédex"]
    all_forms = tuple(form_alias.get(f, f) for f in unique_forms)
    seeable_forms = set()  # Only for counting
    for data in seeable_species_data.values():
        if data.species_name in all_forms:
            seeable_forms.add(data.species_name)
    for data in catchable_species_data.values():
        if data.species_name in all_forms:
            seeable_forms.add(data.species_name)
    maximum = min(len(seeable_forms), option_value["Maximum"])

    def get_rule(x: int) -> AccessRule:
        x = min(x, 72)
        if (build_form_seen_rule, x) not in world.rules_dict:
            world.rules_dict[build_form_seen_rule, x] = build_form_seen_rule(x, world, all_forms)
        return world.rules_dict[build_form_seen_rule, x]

    def create_location(count: int) -> None:
        loc_name = f"Pokédex - See {count} alternate forms"
        l: PokemonBWLocation = PokemonBWLocation(world.player, loc_name, world.location_name_to_id[loc_name], r)
        l.progress_type = LocationProgressType.DEFAULT
        l.access_rule = get_rule(min(count + option_value["Leniency"], maximum))
        r.locations.append(l)

    for c in range(1, maximum+1):
        if c % option_value["Steps"]:
            continue
        create_location(c)
    if maximum == option_value["Maximum"] and maximum % option_value["Steps"]:
        create_location(maximum)

    world.disallowed_all_seen.extend(dex for dex in (world.species_entries[form].dex_number for form in all_forms) if dex not in world.disallowed_all_seen)
