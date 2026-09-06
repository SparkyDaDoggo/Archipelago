from typing import TYPE_CHECKING

from Options import OptionError
from .. import SpeciesChecklist, CopyChecklist, EncounterEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def get_species_checklist(world: "PokemonBWWorld") -> SpeciesChecklist:
    from ...data.pokemon.species import form_alias
    # Species needed for trade are added in generate_trade_encounters()

    if not world.options.randomize_wild_pokemon.is_randomize:
        return SpeciesChecklist([], world)
    elif world.options.randomize_wild_pokemon.is_ensure_all:
        return SpeciesChecklist([data for data in world.species_entries.values() if data.form < 6], world)
    else:  # Just "Randomize"
        always_required = [world.species_entries[spec_name] for spec_name in (
            "Celebi",
            "Raikou",
            "Entei",
            "Suicune",
            "Tornadus",
            "Thundurus",
            "Genesect",
            "Shaymin",
            "Deerling (Spring)",
            "Deerling (Summer)",
            "Deerling (Autumn)",
            "Deerling (Winter)",
        )]
        blacklist = world.options.wild_randomization_blacklist.value

        if isinstance(world.options.dexsanity.value, list):
            for dex_num in world.options.dexsanity.value:
                spec = world.species_entries_by_id[(dex_num, 0)]
                if spec not in always_required:
                    always_required.append(spec)

        if isinstance(world.options.seensanity.value, list):
            for dex_num in world.options.seensanity.value:
                spec = world.species_entries_by_id[(dex_num, 0)]
                if spec not in always_required:
                    always_required.append(spec)

        if isinstance(world.options.formsanity.value, list):
            for form_name in world.options.formsanity.value:
                spec = world.species_entries[form_alias.get(form_name, form_name)]
                if spec not in always_required:
                    always_required.append(spec)

        if isinstance(world.options.shinysanity.value, list):
            for dex_num in world.options.shinysanity.value:
                spec = world.species_entries_by_id[(dex_num, 0)]
                if spec not in always_required:
                    always_required.append(spec)

        if isinstance(world.options.shinyformsanity.value, list):
            for form_name in world.options.shinyformsanity.value:
                spec = world.species_entries[form_alias.get(form_name, form_name)]
                if spec not in always_required:
                    always_required.append(spec)

        # Ensure one fighting type for challenge rock
        for spec_name, data in world.species_entries.items():
            if "Fighting" in data.types and spec_name not in blacklist:
                if data not in always_required:
                    always_required.append(data)
                break

        # cannot use world.disallowed_all_seen since that will only be filled at a later point
        seen_amount = world.options.seensanity if isinstance(world.options.seensanity.value, int) else len(world.options.seensanity.value)
        form_amount = 16  # for simplicity, let's just assume all forms are included
        auto_seen = 649 - max(seen_amount, form_amount) if world.options.all_pokemon_seen else 0
        if auto_seen < 115:
            # Get list of ALL pokémon
            pool_115 = list(data for spec_name, data in world.species_entries.items()
                            if not data.form and spec_name not in blacklist)
            # Removes what's already ensured
            for spec in always_required:
                if spec in pool_115:
                    pool_115.remove(spec)
            # Assert that there are actually 115 pokemon available
            if len(always_required) + len(pool_115) < auto_seen:
                raise OptionError(f"Player {world.player_name}: Less than {auto_seen} pokémon available. Please either "
                                  f"reduce the amount of blacklisted pokémon or add **Ensure all obtainable**.")
            # Random picking begins here
            world.random.shuffle(pool_115)
            # Remove overpowered stuff and save it in case of not enough non-overpowered
            underpowered, overpowered = [], []
            if world.options.randomize_wild_pokemon.is_prevent_overpowered:
                threshold: int = world.options.pokemon_randomization_adjustments["Overpowered threshold"]
                for spec in pool_115:
                    (underpowered if sum(spec.base_stats) <= threshold else overpowered).append(spec)
                pool_115 = underpowered
            # Fill with random to get 115 total
            always_required += (pool_115[i] for i in range(min(auto_seen-len(always_required), len(pool_115))))
            # Add overpowered stuff in case of not enough non-overpowered
            if len(always_required) < auto_seen:
                always_required += (overpowered[i] for i in range(auto_seen-len(always_required)))

        return SpeciesChecklist(always_required, world)


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


def get_copy_checklist(world: "PokemonBWWorld") -> CopyChecklist | None:
    from ...data.locations.encounters import rates

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
        return None

    copy_list = CopyChecklist()
    mods = world.options.randomize_wild_pokemon
    rates_by_global_slot: tuple[int, ...] = (*encounter_rates[0], *encounter_rates[0], *encounter_rates[0],
                                             *encounter_rates[1], *encounter_rates[1],
                                             *encounter_rates[2], *encounter_rates[2])

    if mods.is_merge_phenomena:
        first_phen: dict[tuple[str, str, str], EncounterEntry] = {}
        for slot in world.wild_encounter.values():
            if slot.encounter_region[2] in ("RG", "SR", "FR"):
                if slot.encounter_region not in first_phen:
                    first_phen[slot.encounter_region] = slot
                else:
                    f_slot = first_phen[slot.encounter_region]
                    copy_list.merge(f_slot, slot,
                                    rates_by_global_slot[f_slot.file_index[2]],
                                    rates_by_global_slot[slot.file_index[2]])

    if mods.is_global_1_to_1 and not mods.is_ensure_all:
        first_global: dict[tuple[int, int], EncounterEntry] = {}
        for slot in world.wild_encounter.values():
            group = copy_list[slot.file_index]
            if group is None:
                continue
            group = group.search()
            if group.head != slot:
                continue
            if slot.species_id not in first_global:
                first_global[slot.species_id] = slot
            else:
                f_slot = first_global[slot.species_id]
                copy_list.merge(f_slot, slot,
                                rates_by_global_slot[f_slot.file_index[2]],
                                rates_by_global_slot[slot.file_index[2]])
    elif mods.is_dungeon_1_to_1:
        first_dungeon: dict[tuple[str, tuple[int, int]], EncounterEntry] = {}
        for slot in world.wild_encounter.values():
            group = copy_list[slot.file_index]
            if group is None:
                continue
            group = group.search()
            if group.head != slot:
                continue
            dungeon_name = slot.encounter_region[0]
            if " " in dungeon_name:
                dungeon_name = dungeon_name[:dungeon_name.index(" ")]
            g_key = dungeon_name, slot.species_id
            if g_key not in first_dungeon:
                first_dungeon[g_key] = slot
            else:
                f_slot = first_dungeon[g_key]
                copy_list.merge(f_slot, slot,
                                rates_by_global_slot[f_slot.file_index[2]],
                                rates_by_global_slot[slot.file_index[2]])
    elif mods.is_area_1_to_1:
        first_area: dict[tuple[str, tuple[int, int]], EncounterEntry] = {}
        for slot in world.wild_encounter.values():
            group = copy_list[slot.file_index]
            if group is None:
                continue
            group = group.search()
            if group.head != slot:
                continue
            g_key = slot.encounter_region[0], slot.species_id
            if g_key not in first_area:
                first_area[g_key] = slot
            else:
                f_slot = first_area[g_key]
                copy_list.merge(f_slot, slot,
                                rates_by_global_slot[f_slot.file_index[2]],
                                rates_by_global_slot[slot.file_index[2]])

    if mods.is_prevent_rare:
        threshold = world.options.pokemon_randomization_adjustments["Rare encounters threshold"]
        for file_index, slot in world.wild_encounter.items():
            group = copy_list[file_index]
            if group:
                group = group.search()
                chance = group.chances[slot.encounter_region]
            else:
                chance = rates_by_global_slot[file_index[2]]
            is_grass = "G" in slot.encounter_region[2]
            method_index = (file_index[2] % 12) if is_grass else ((file_index[2] - 36) % 5)
            method_start = file_index[2] - method_index
            if chance < threshold:
                for combined_threshold in (threshold * step // 2 for step in range(1, 201)):
                    for next_index_down in range(12 if is_grass else 5):
                        if next_index_down == method_index:  # cannot be merged with itself
                            continue
                        next_slot = world.wild_encounter[file_index[0], file_index[1], method_start + next_index_down]
                        next_group = copy_list[next_slot.file_index]
                        if next_group:
                            next_group = next_group.search()
                            if group == next_group:  # already merged
                                continue
                            next_chance = next_group.chances[next_slot.encounter_region]
                        else:
                            next_chance = rates_by_global_slot[next_slot.file_index[2]]
                        if chance + next_chance <= combined_threshold:
                            copy_list.merge(slot, next_slot, chance, next_chance)
                            break
                    else:
                        continue
                    break

    return copy_list
