from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def get_species_checklist(world: "PokemonBWWorld") -> tuple[list[str], set[str]]:
    # Returns ({to be checked species}, {already checked species})
    # Species needed for trade are added in generate_trade_encounters()
    from ...data.pokemon.species import by_name, unova_species

    if "Randomize" not in world.options.randomize_wild_pokemon:
        return [], set()
    elif "Ensure all obtainable" in world.options.randomize_wild_pokemon:
        return [species for species in by_name], set()
    else:  # Just "Randomize"
        always_required = [
            "Celebi",
            "Raikou",
            "Entei",
            "Suicune",
        ]

        unova = [name for name in unova_species]
        world.random.shuffle(unova)
        for spec in unova:
            if "Fighting" in (unova_species[spec].type_1, unova_species[spec].type_2):
                always_required.append(spec)
                unova.remove(spec)
                break
        always_required += unova[:114]

        unova_guaranteed = [
            "Tornadus",
            "Thundurus",
            "Deerling (Spring)",
            "Deerling (Summer)",
            "Deerling (Autumn)",
            "Deerling (Winter)",
        ]
        for species in unova_guaranteed:
            if species not in always_required:
                always_required.append(species)

        return always_required, set()


def check_species(world: "PokemonBWWorld", checklist: tuple[list[str], set[str]], species: str, loop=0) -> None:
    from ...data.pokemon.species import by_name, by_id

    if species in checklist[0]:
        checklist[0].remove(species)
    checklist[1].add(species)

    # Looping evolutions are not planned to be prevented
    if loop >= 5:
        return

    data = by_name[species]
    for evolution in data.evolutions:
        if evolution[0] == "Level up with party member":
            add_species_to_check(checklist, by_id[(evolution[1], 0)])
        check_species(world, checklist, evolution[2], loop+1)


def add_species_to_check(checklist: tuple[list[str], set[str]], species: str) -> None:
    if species not in checklist[1]:
        checklist[0].append(species)


def get_slots_checklist(world: "PokemonBWWorld") -> dict[str, str | None]:
    from ...data.locations.encounters.slots import table

    # {slot: to copy from}
    copy_from: dict[str, str | None] = {slot: None for slot in table}

    if "Randomize" not in world.options.randomize_wild_pokemon:
        return copy_from

    merge_phenomenons = "Merge phenomenons" in world.options.randomize_wild_pokemon
    area_1_to_1 = "Area 1-to-1" in world.options.randomize_wild_pokemon
    prevent_rare_encounters = "Prevent rare encounters" in world.options.randomize_wild_pokemon
    versioned_species = (
        (lambda d: d.species_white)
        if world.options.version == "white"
        else (lambda d: d.species_black)
    )

    if merge_phenomenons:
        # Assumes a fresh copy_from dict without any modifier applied
        for slot in copy_from:
            file_index = table[slot].file_index
            if 24 < file_index[2] < 34 or 41 < file_index[2] < 46 or 51 < file_index[2]:
                copy_from[slot] = slot[:-1] + "0"
            elif file_index[2] in (34, 35):
                copy_from[slot] = slot[:-2] + "0"

    if area_1_to_1:
        # {area: {(dex_num, form): slot}}
        first_slot: dict[int, dict[tuple[int, int], str]] = {}
        for slot in copy_from:
            if copy_from[slot] is None:
                area = table[slot].file_index[0]
                species: tuple[int, int] = versioned_species(table[slot])
                if area not in first_slot:
                    first_slot[area] = {}
                if species not in first_slot[area]:
                    first_slot[area][species] = slot
                else:
                    copy_from[slot] = first_slot[area][species]

    if prevent_rare_encounters:
        # rates = [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1] * 3 + [60, 30, 5, 4, 1] * 2 + [40, 40, 15, 4, 1] * 2
        # {region: [slot1 rate, slot2 rate]}
        region_added_rates: dict[str, list[int]] = {}
        for slot in copy_from:
            region = table[slot].encounter_region
            method_index = int(slot[-2:])
            if region not in region_added_rates:
                if "G" in region[-2:]:
                    region_added_rates[region] = [20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1]
                elif "S" in region[-2:]:
                    region_added_rates[region] = [60, 30, 5, 4, 1]
                elif "F" in region[-2:]:
                    region_added_rates[region] = [40, 40, 15, 4, 1]
            if copy_from[slot] is not None:
                region_added_rates[region][int(copy_from[slot][-2:])] += region_added_rates[region][method_index]
                region_added_rates[region][method_index] = 0
        for slot in copy_from:
            region = table[slot].encounter_region
            method_index = int(slot[-2:])
            if copy_from[slot] is None:
                if region_added_rates[region][method_index] < 10:
                    # for next_index_down in (9/8/7/...)...0
                    for next_index_down in reversed(range(min(method_index, 10))):
                        next_slot = table[slot].encounter_region + f" {next_index_down}"
                        if copy_from[next_slot] is None:
                            copy_from[slot] = next_slot
                            region_added_rates[region][next_index_down] += region_added_rates[region][method_index]
                            region_added_rates[region][method_index] = 0

    return copy_from
