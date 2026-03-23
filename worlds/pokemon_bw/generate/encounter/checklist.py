from typing import TYPE_CHECKING, Callable

from .. import SpeciesChecklist

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from ...data import SpeciesData


def get_species_checklist(world: "PokemonBWWorld") -> SpeciesChecklist:
    # Returns ({to be checked species}, {already checked species})
    # Species needed for trade are added in generate_trade_encounters()
    from ...data.pokemon.species import by_name, by_id
    from ...data.pokemon.pokedex import by_number

    if not world.options.randomize_wild_pokemon.is_randomize:
        return SpeciesChecklist([])
    elif world.options.randomize_wild_pokemon.is_ensure_all:
        return SpeciesChecklist([species for species, data in by_name.items() if data.form < 6])
    else:  # Just "Randomize"
        always_required = [
            "Celebi",
            "Raikou",
            "Entei",
            "Suicune",
            "Tornadus",
            "Thundurus",
            "Deerling (Spring)",
            "Deerling (Summer)",
            "Deerling (Autumn)",
            "Deerling (Winter)",
        ]
        both_types: Callable[["SpeciesData"], tuple[str, str]] = lambda data: (data.type_1, data.type_2)
        # Ensure one fighting type for challenge rock
        for num in range(len(by_number)):
            spec = by_id[(num, 0)]
            if "Fighting" in both_types(by_name[spec]):
                if spec not in always_required:
                    always_required.append(spec)
                break

        if not world.options.all_pokemon_seen:
            # Get list of ALL pokémon
            pool_115 = list((spec, data) for spec, data in by_name.items() if not data.form)
            # Removes what's already ensured
            for spec in always_required:
                spec_tup = (spec, by_name[spec])
                if spec_tup in pool_115:
                    pool_115.remove(spec_tup)
            # Random picking begins here
            world.random.shuffle(pool_115)
            # Remove overpowered stuff and save it in case of not enough non-overpowered
            underpowered, overpowered = [], []
            if world.options.randomize_wild_pokemon.is_prevent_overpowered:
                stats_total: Callable[["SpeciesData"], int] = lambda data: (
                    data.base_hp + data.base_attack + data.base_defense +
                    data.base_sp_attack + data.base_sp_defense + data.base_speed
                )
                threshold: int = world.options.pokemon_randomization_adjustments["Overpowered threshold"]
                for spec_tup in pool_115:
                    (underpowered if stats_total(spec_tup[1]) <= threshold else overpowered).append(spec_tup)
                pool_115 = underpowered
            # Fill with random to get 115 total
            always_required += (pool_115[i] for i in range(min(115-len(always_required), len(pool_115))))
            # Add overpowered stuff in case of not enough non-overpowered
            if len(always_required) < 115:
                always_required += (overpowered[i] for i in range(115-len(always_required)))

        if isinstance(world.options.dexsanity.value, list):
            for dex_num in world.options.dexsanity.value:
                spec = by_id[(dex_num, 0)]
                if spec not in always_required:
                    always_required.append(spec)

        return SpeciesChecklist(always_required)


def random_percentage_distribution(world: "PokemonBWWorld", length: int) -> list[int]:
    ret = []
    remaining = 100
    for i in reversed(range(2, length+1)):
        rand = world.random.random() ** (i//2)
        if int(rand * 100) % 2:
            value = (remaining//i) + int((remaining-(remaining//i))*rand)
        else:
            value = (remaining//i) + int(-(remaining//i)*rand)
        value = max(1, min(value, remaining-i+1))
        ret.append(value)
        remaining -= value
    ret.append(remaining)
    return ret


def track_down_copy_from(copy_from: dict[str, str | None], slot: str) -> str:
    current = slot
    while copy_from[current] is not None:
        current = copy_from[current]
    return current


def get_slots_checklist(world: "PokemonBWWorld") -> dict[str, str | None]:
    from ...data.locations.encounters.slots import table
    from ...data.locations.encounters import rates

    # {slot: to copy from}
    copy_from: dict[str, str | None] = {slot: None for slot in table}
    # Important: make copies of lists afterwards
    if world.options.modify_encounter_rates.current_key == "plando":
        plando = world.options.modify_encounter_rates.value
        encounter_rates = (
            plando["grass"] if "grass" in plando else rates.tables["vanilla"][0],
            plando["surfing"] if "surfing" in plando else rates.tables["vanilla"][1],
            plando["fishing"] if "fishing" in plando else rates.tables["vanilla"][2],
        )
        world.options.modify_encounter_rates.custom_rates = encounter_rates
    elif world.options.modify_encounter_rates.current_key == "randomized_12":
        encounter_rates = (
            random_percentage_distribution(world, 12),
            random_percentage_distribution(world, 5),
            random_percentage_distribution(world, 5),
        )
        world.options.modify_encounter_rates.custom_rates = encounter_rates
    else:
        encounter_rates = rates.tables[world.options.modify_encounter_rates.current_key]

    if not world.options.randomize_wild_pokemon.is_randomize:
        return copy_from

    merge_phenomenons = world.options.randomize_wild_pokemon.is_merge_phenomena
    area_1_to_1 = world.options.randomize_wild_pokemon.is_area_1_to_1
    prevent_rare_encounters = world.options.randomize_wild_pokemon.is_prevent_rare
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
        # {region: [slot1 rate, slot2 rate, ...]}
        threshold = world.options.pokemon_randomization_adjustments["Rare encounters threshold"]
        region_added_rates: dict[str, list[int]] = {}
        for slot in copy_from:
            region = table[slot].encounter_region
            method_index = int(slot[-2:])
            if region not in region_added_rates:
                if "G" in region[-2:]:
                    region_added_rates[region] = list(encounter_rates[0])
                elif "S" in region[-2:]:
                    region_added_rates[region] = list(encounter_rates[1])
                elif "F" in region[-2:]:
                    region_added_rates[region] = list(encounter_rates[2])
            if copy_from[slot] is not None:
                to_copy = track_down_copy_from(copy_from, slot)
                region_added_rates[region][int(to_copy[-2:])] += region_added_rates[region][method_index]
                region_added_rates[region][method_index] = 0
        for slot in copy_from:  # StrCity - FR 0, 1, ...11
            region = table[slot].encounter_region  # StrCity - FR
            added_rates = region_added_rates[region]
            method_index = int(slot[-2:])  # 0, 1, ..., 11
            is_grass = region[-2:] in (" G", "DG", "RG")
            if copy_from[slot] is None and added_rates[method_index] < threshold:
                # combined threshold that gradually increases, so that merges are distributed more evenly
                for combined_threshold in (threshold * step // 2 for step in range(1, 201)):
                    for next_index_down in range(12 if is_grass else 5):
                        if next_index_down == method_index:
                            continue
                        next_slot = table[slot].encounter_region + f" {next_index_down}"
                        tracked_slot = track_down_copy_from(copy_from, next_slot)
                        tracked_index = int(tracked_slot[-2:])
                        if (
                            tracked_slot != slot and
                            added_rates[tracked_index] + added_rates[method_index] <= combined_threshold
                        ):
                            copy_from[slot] = next_slot
                            added_rates[tracked_index] += added_rates[method_index]
                            added_rates[method_index] = 0
                            break
                    else:
                        continue
                    break

    return copy_from
