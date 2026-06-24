import itertools
from typing import TYPE_CHECKING, Callable

from Options import OptionError
from .. import EncounterEntry, SpeciesChecklist

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from .. import SpeciesEntry
    from .. import EncounterEntry

prepare = 25350666777563370117040793671783381956473107378414503005100223998849054326267652480678608918097127753


def organize_by_method(world: "PokemonBWWorld") -> dict[str, list[int]]:
    # {method: ([species names], [dex numbers])}
    ret: dict[str, list[int]] = {}
    for slot, data in world.wild_encounter.items():
        if data.encounter_region not in ret:
            ret[data.encounter_region] = []
        if data.species_id[0] not in ret[data.encounter_region]:
            ret[data.encounter_region].append(data.species_id[0])
    for static_slot, entry in world.static_encounter.items():
        ret[static_slot] = [entry.species_id[0]]
    for trade_slot, trade_entry in world.trade_encounter.items():
        ret[trade_slot] = [trade_entry.species_id[0]]
    return ret


def organize_trades(world: "PokemonBWWorld") -> dict[str, tuple[int, int]]:
    return {trade_slot: (trade_entry.species_id[0], trade_entry.wanted_dex_number)
            for trade_slot, trade_entry in world.trade_encounter.items()}


def generate_wild_encounters(world: "PokemonBWWorld",
                             species_checklist: SpeciesChecklist,
                             slots_checklist: dict[str, str | None]) -> dict[str, EncounterEntry]:
    from ...data.pokemon.species import by_id, forms_by_dex, get_weighted_random_species
    from ...data.locations.encounters.slots import table
    from ...data.locations.encounters.regions import bad_early_areas
    from ...data.pokemon.movesets_level_up import table as moveset_table

    versioned_species = (
        (lambda d: d.species_white)
        if world.options.version == "white"
        else (lambda d: d.species_black)
    )

    if not world.options.randomize_wild_pokemon.is_randomize:
        return {
            name: EncounterEntry(
                versioned_species(table[name]), table[name].encounter_region, table[name].file_index, False
            )
            for name, to_copy in slots_checklist.items() if to_copy != "FILLED"
        }

    encounter_entries: dict[str, EncounterEntry] = {}
    logic_slots: list[str] = []
    other_slots: list[str] = []
    copy_slots: list[str] = []
    for name, to_copy in slots_checklist.items():
        if to_copy == "FILLED":
            continue
        elif to_copy is not None:
            copy_slots.append(name)
        elif table[name].encounter_region in world.regions:
            logic_slots.append(name)
        else:
            other_slots.append(name)
    world.random.shuffle(logic_slots)
    world.random.shuffle(other_slots)

    if len(species_checklist) > len(logic_slots):
        if world.options.modify_logic.is_consider_evos:
            for species in species_checklist.copy_list():
                species_data = world.species_entries[species]
                for evolution in species_data.evolutions:
                    if evolution[0] != "Level up with party member":
                        evo_id_tup = (evolution[2], species_data.form)
                        species_checklist.check(by_id[evo_id_tup if evo_id_tup in by_id else (evolution[2], 0)])
        if len(species_checklist) > len(logic_slots):
            raise OptionError(
                f"More required species for randomized wild encounter than slots they could be placed in "
                f"for player {world.player_name}: {len(species_checklist)} > {len(logic_slots)}.\n"
                f"Please remove some restrictive options or tweak the \"Modify Logic\" option."
            )

    similar_base_stats = world.options.randomize_wild_pokemon.is_similar_stats
    type_themed = world.options.randomize_wild_pokemon.is_type_themed_areas
    prevent_overpowered = world.options.randomize_wild_pokemon.is_prevent_overpowered
    prevent_bad_early = world.options.randomize_wild_pokemon.is_prevent_bad_early
    stats_threshold: int = world.options.pokemon_randomization_adjustments["Overpowered threshold"]
    blacklist = world.options.wild_randomization_blacklist.value
    area_types: dict[str, str] = {}
    stats_total: Callable[["SpeciesEntry"], int] = lambda data: (
        data.base_hp + data.base_attack + data.base_defense +
        data.base_sp_attack + data.base_sp_defense + data.base_speed
    )

    # Devolve overpowered species
    if prevent_overpowered and world.options.modify_logic.is_consider_evos:
        for name, spec_data in world.species_entries.items():
            if name in blacklist:
                continue
            spec_total = stats_total(spec_data)
            for evo_tuple in spec_data.evolutions:
                evo_id_tup = (evo_tuple[2], spec_data.form)
                evolved_name = by_id[evo_id_tup if evo_id_tup in by_id else (evo_tuple[2], 0)]
                if evolved_name not in species_checklist.to_check:
                    continue
                if evo_tuple[0] == "Level up with party member":
                    # This frickin' evolution method is too complicated once more
                    continue
                evolved_data = world.species_entries[evolved_name]
                evo_total = stats_total(evolved_data)
                if evo_total <= stats_threshold:
                    continue
                if spec_total >= evo_total:
                    # Devolving to an even stronger pre-evolution doesn't make sense
                    continue
                species_checklist.check(evolved_name)
                species_checklist.add(name)

    while len(species_checklist) > 0:
        random_species = world.random.choice(species_checklist.to_check)
        species_data = world.species_entries[random_species]
        stat_tolerance = world.options.pokemon_randomization_adjustments["Stats leniency"]
        skip_type = skip_bad = False
        while True:
            skipped_stat = skipped_type = skipped_bad = False
            for slot in logic_slots:
                if type_themed and not skip_type:
                    region = table[slot].encounter_region
                    area = region[:region.index(" - ")]
                    if area not in area_types:
                        area_types[area] = world.random.choice((species_data.type_1, species_data.type_2))
                    elif area_types[area] not in (species_data.type_1, species_data.type_2):
                        skipped_type = True
                        continue
                if prevent_bad_early and not skip_bad:
                    region = table[slot].encounter_region
                    area = region[:region.index(" - ")]
                    if area in bad_early_areas:
                        if "Wonder Guard" in species_data.abilities:
                            skipped_bad = True
                            continue
                        moveset = moveset_table[random_species].level_up_moves
                        if any((move_learn[1] in ("SonicBoom", "Dragon Rage")) for move_learn in moveset):
                            skipped_bad = True
                            continue
                if similar_base_stats:  # stats last because it's more lenient than others
                    random_stats = stats_total(species_data)
                    vanilla_stats = stats_total(world.species_entries[by_id[versioned_species(table[slot])]])
                    if random_stats not in range(vanilla_stats - stat_tolerance, vanilla_stats + stat_tolerance + 1):
                        skipped_stat = True
                        continue
                encounter_entries[slot] = EncounterEntry(
                    (species_data.dex_number, species_data.form),
                    table[slot].encounter_region, table[slot].file_index, True
                )
                species_checklist.check(random_species)
                logic_slots.remove(slot)
                break
            else:
                if skipped_stat:
                    stat_tolerance += 10
                elif skipped_type:
                    # Force place into any slot that still kinda fits
                    skip_type = True
                elif skipped_bad:
                    # I really hope that this will only ever happen if someone heavily abuses encounter plando
                    skip_bad = True
                else:
                    # Should be unreachable
                    pass
                continue
            break

    any_species = forms_by_dex if not (prevent_overpowered or blacklist) else {
        key: [
            name
            for name in value
            if stats_total(world.species_entries[name]) <= stats_threshold and name not in blacklist
        ]
        for key, value in forms_by_dex.items()
    }
    if any(not len(value) for value in any_species.values()):
        any_species = {key: value for key, value in any_species.items() if value}
    any_species_by_type: dict[str, dict[int, list[str]]] = {}
    if not world.random.randint(0, 999) and len(set(w.game for w in world.multiworld.worlds.values())) > 3:
        print(world.prepare_text(prepare))
    for forms_list in any_species.values():
        for spe in forms_list:
            data = world.species_entries[spe]
            for typ in (data.type_1, data.type_2):
                if typ not in any_species_by_type:
                    any_species_by_type[typ] = {data.dex_number: [spe]}
                elif data.dex_number not in any_species_by_type[typ]:
                    any_species_by_type[typ][data.dex_number] = [spe]
                else:
                    any_species_by_type[typ][data.dex_number].append(spe)
    if type_themed and len(any_species_by_type) < 17:
        raise OptionError("At least one type has all its species prevented in wild randomization due to some option. "
                          "Please remove some restrictions in your yaml.")
    for slot in itertools.chain(logic_slots, other_slots):
        stat_tolerance = world.options.pokemon_randomization_adjustments["Stats leniency"]
        region = table[slot].encounter_region
        area = region[:region.index(" - ")]
        while True:
            random_species = get_weighted_random_species(world.random, any_species)
            species_data = world.species_entries[random_species]
            if type_themed:
                if area not in area_types:
                    area_types[area] = world.random.choice((species_data.type_1, species_data.type_2))
                elif area_types[area] not in (species_data.type_1, species_data.type_2):
                    random_species = get_weighted_random_species(world.random, any_species_by_type[area_types[area]])
                    species_data = world.species_entries[random_species]
            if prevent_bad_early:
                if area in bad_early_areas:
                    if "Wonder Guard" in species_data.abilities:
                        continue
                    moveset = moveset_table[random_species].level_up_moves
                    if any((move_learn[1] in ("SonicBoom", "Dragon Rage")) for move_learn in moveset):
                        continue
            if similar_base_stats:
                random_stats = stats_total(species_data)
                vanilla_stats = stats_total(world.species_entries[by_id[versioned_species(table[slot])]])
                if random_stats not in range(vanilla_stats - stat_tolerance, vanilla_stats + stat_tolerance + 1):
                    stat_tolerance += 10
                    continue
            encounter_entries[slot] = EncounterEntry(
                (species_data.dex_number, species_data.form), table[slot].encounter_region, table[slot].file_index, True
            )
            break
    for slot in copy_slots:
        to_copy = slots_checklist[slot]
        while slots_checklist[to_copy] is not None:
            to_copy = slots_checklist[to_copy]
        encounter_entries[slot] = EncounterEntry(
            encounter_entries[to_copy].species_id, table[slot].encounter_region, table[slot].file_index, True
        )

    if len(encounter_entries) + len(world.wild_encounter) != len(table):
        raise Exception(f"Player {world.player_name}: Number of generated encounters does not match data "
                        f"({len(encounter_entries) + len(world.wild_encounter)} entries, {len(table)} data rows)")

    return encounter_entries
