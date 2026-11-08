from typing import TYPE_CHECKING

from ....locations import PokemonBWLocation

if TYPE_CHECKING:
    from .... import PokemonBWWorld
    from BaseClasses import Region
    from ... import SpeciesEntry
    from ....data import AccessRule


def lookup(domain: int) -> dict[str, int]:
    from ....data.locations.sanity.countsanity import shinygendercountsanity

    to_shift = {"male": 0, "female": 1, "any": 2}
    return {name: number * 3 + to_shift[gender] + domain for name, (number, gender) in shinygendercountsanity.items()}


def create(world: "PokemonBWWorld", catchable_species_data: dict[str, "SpeciesEntry"]) -> None:
    from ....data.locations.rules import build_caught_rule

    option_value = world.options.shinygendercountsanity.value
    if isinstance(option_value, int):
        option_value = {
            "Maximum": option_value,
            "Steps": 1,
            "Leniency": 0,
        }
    if not option_value["Maximum"]:
        return

    def get_rule(x: int) -> "AccessRule":
        x = min(x, 649)
        if (build_caught_rule, x) not in world.rules_dict:
            world.rules_dict[build_caught_rule, x] = build_caught_rule(x, world)
        return world.rules_dict[build_caught_rule, x]

    r: "Region" = world.regions["Pokédex"]
    genderable_dex = set()  # Only for counting
    is_any_gender = world.options.gendercountmode == "any"
    for data in catchable_species_data.values():
        if data.gender_ratio in world.options.gendersanity.gender_threshold:
            genderable_dex.add(data.dex_number)
    maximum = min(len(genderable_dex) * 2, option_value["Maximum"])

    def create_location(count: int, gender: str) -> None:
        loc_name = f"Pokédex - Find {count} shiny {gender} Pokémon"
        l: PokemonBWLocation = PokemonBWLocation(world.player, loc_name, world.location_name_to_id[loc_name], r)
        rule_count = count if not is_any_gender else (count // 2 + count % 2)
        l.access_rule = get_rule(min(rule_count + option_value["Leniency"], maximum))
        r.locations.append(l)

    if is_any_gender:
        for c in range(1, maximum+1):
            if c % option_value["Steps"]:
                continue
            create_location(c, "gendered")
        if maximum == option_value["Maximum"] and maximum % option_value["Steps"]:
            create_location(maximum, "gendered")
    else:
        max_per_gender = min(maximum, len(genderable_dex))
        male_loc_count = world.random.randint(maximum - max_per_gender, max_per_gender)
        female_loc_count = maximum - male_loc_count
        assert male_loc_count + female_loc_count == maximum
        for c in range(1, male_loc_count+1):
            if c % option_value["Steps"]:
                continue
            create_location(c, "male")
        for c in range(1, female_loc_count+1):
            if c % option_value["Steps"]:
                continue
            create_location(c, "female")
        if male_loc_count % option_value["Steps"]:
            create_location(male_loc_count, "male")
        if female_loc_count % option_value["Steps"]:
            create_location(female_loc_count, "female")
