from typing import TYPE_CHECKING
from .. import StaticEncounterEntry, TradeEncounterEntry, SpeciesChecklist
from ...data import StaticEncounterData

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def generate_static_encounters(world: "PokemonBWWorld", species_checklist: SpeciesChecklist):
    from ...data.locations.encounters.static import static, legendary, fossils, gift

    is_dynamic = world.options.version == "dynamic"
    versioned_species = (
        (lambda d: d.species_white)
        if world.options.version == "white" or (is_dynamic and world.random.random() < 0.5)
        else (lambda d: d.species_black)
    )
    legendaries_mythicals = [144, 145, 146, 159, 151,
                             243, 244, 245, 249, 250, 251,
                             377, 378, 379, 380, 381, 382, 383, 384, 385, 386,
                             480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493,
                             494, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649]
    pseudos = [149, 248, 373, 376, 445, 635, 479]
    encounters = world.static_encounter
    not_randomized: dict[str, StaticEncounterData] = {}

    if not world.options.randomize_static_pokemon.is_randomize:
        not_randomized |= static
    else:
        mods = world.options.randomize_static_pokemon
        statues = small_mimics = big_mimics = None
        for name, data in static.items():
            possible = list(spec for spec in world.species_entries_by_id.values() if not spec.form)
            if not mods.is_split_statues and "Desert Resort" in name and statues:
                encounters[name] = StaticEncounterEntry(statues, data.encounter_region,
                                                        data.inclusion_rule, data.access_rule, False, 0b1)
                continue
            if not mods.is_split_mimics and "Item" in name:
                if name.endswith(("1", "2")) and small_mimics:
                    encounters[name] = StaticEncounterEntry(small_mimics, data.encounter_region,
                                                            data.inclusion_rule, data.access_rule, False, 0b1)
                    continue
                if name.endswith(("3", "4")) and big_mimics:
                    encounters[name] = StaticEncounterEntry(big_mimics, data.encounter_region,
                                                            data.inclusion_rule, data.access_rule, False, 0b1)
                    continue
            if mods.is_no_legendaries:
                possible = [spec for spec in possible
                            if spec.dex_number not in legendaries_mythicals] or possible
            if mods.is_similar_stats:
                # Similar stats at last because it gradually increases instead of simple True/False
                stat_tolerance = world.options.pokemon_randomization_adjustments["Stats leniency"]
                vanilla_spec = world.species_entries_by_id[versioned_species(data)]
                while True:
                    if next := [spec for spec in possible
                                if abs(sum(vanilla_spec.base_stats) - sum(spec.base_stats)) <= stat_tolerance]:
                        possible = next
                        break
                    stat_tolerance += 10
            chosen = world.random.choice(possible)
            encounters[name] = StaticEncounterEntry((chosen.dex_number, chosen.form), data.encounter_region,
                                                    data.inclusion_rule, data.access_rule, False, 0b1)
            if "Desert Resort" in name:
                statues = (chosen.dex_number, chosen.form)
            if "Item" in name and name.endswith(("1", "2")):
                small_mimics = (chosen.dex_number, chosen.form)
            if "Item" in name and name.endswith(("3", "4")):
                big_mimics = (chosen.dex_number, chosen.form)

    if not world.options.randomize_gift_pokemon.is_randomize:
        not_randomized |= gift | fossils
    else:
        mods = world.options.randomize_gift_pokemon
        monkeys = None
        for name, data in (gift | fossils).items():
            possible = list(world.species_entries_by_id.values())
            if not mods.is_split_monkeys and "Dreamyard" in name and monkeys:
                encounters[name] = StaticEncounterEntry(monkeys, data.encounter_region,
                                                        data.inclusion_rule, data.access_rule, False, 0b1)
                continue
            if mods.is_no_legendaries:
                possible = [spec for spec in possible if spec.dex_number not in legendaries_mythicals] or possible
            if mods.is_any_base:
                possible = [spec for spec in possible if not spec.pre_evolutions] or possible
            if mods.is_similar_stats:
                # Similar stats at last because it gradually increases instead of simple True/False
                stat_tolerance = world.options.pokemon_randomization_adjustments["Stats leniency"]
                vanilla_spec = world.species_entries_by_id[versioned_species(data)]
                while True:
                    if next := [spec for spec in possible
                                if abs(sum(vanilla_spec.base_stats) - sum(spec.base_stats)) <= stat_tolerance]:
                        possible = next
                        break
                    stat_tolerance += 10
            chosen = world.random.choice(possible)
            encounters[name] = StaticEncounterEntry((chosen.dex_number, chosen.form), data.encounter_region,
                                                    data.inclusion_rule, data.access_rule, False, 0b1)
            if "Dreamyard" in name:
                monkeys = (chosen.dex_number, chosen.form)

    if not world.options.randomize_legendary_pokemon.is_randomize:
        not_randomized |= legendary
    else:
        mods = world.options.randomize_legendary_pokemon
        vanilla_spec = None
        for name, data in legendary.items():
            if data.fixed:
                not_randomized[name] = data
                continue
            if mods.is_keep_legendary and mods.is_no_legendaries:
                possible = [spec for spec in world.species_entries.values()
                            if spec.dex_number in pseudos and not spec.form]
            elif mods.is_no_legendaries:
                possible = [spec for spec in world.species_entries.values()
                            if spec.dex_number not in legendaries_mythicals and not spec.form]
            elif mods.is_keep_legendary:
                possible = [spec for spec in world.species_entries.values()
                            if spec.dex_number in legendaries_mythicals and not spec.form]
            else:
                possible = list(spec for spec in world.species_entries_by_id.values() if not spec.form)
            if mods.is_same_type:
                this1, this2 = (vanilla_spec := world.species_entries_by_id[versioned_species(data)]).types
                possible = [spec for spec in possible if this1 in spec.types or this2 in spec.types] or possible
            if mods.is_similar_stats:
                # Similar stats at last because it gradually increases instead of simple True/False
                stat_tolerance = world.options.pokemon_randomization_adjustments["Stats leniency"]
                vanilla_spec = vanilla_spec or world.species_entries_by_id[versioned_species(data)]
                while True:
                    if next := [spec for spec in possible
                                if abs(sum(vanilla_spec.base_stats) - sum(spec.base_stats)) <= stat_tolerance]:
                        possible = next
                        break
                    stat_tolerance += 10
            chosen = world.random.choice(possible)
            encounters[name] = StaticEncounterEntry((chosen.dex_number, chosen.form), data.encounter_region,
                                                    data.inclusion_rule, data.access_rule,
                                                    data.species_black != data.species_white, 0b1)
            if mods.is_keep_legendary and mods.is_no_legendaries:
                pseudos.remove(chosen.dex_number)
            elif mods.is_keep_legendary:
                legendaries_mythicals.remove(chosen.dex_number)

    for name, data in not_randomized.items():
        encounters[name] = StaticEncounterEntry(versioned_species(data), data.encounter_region,
                                                data.inclusion_rule, data.access_rule,
                                                data.species_black != data.species_white, 0)

    if world.options.modify_logic.is_consider_static:
        for name, entry in encounters.items():
            if entry.inclusion_rule and not entry.inclusion_rule(world):
                continue
            if is_dynamic and entry.different_vanilla:
                continue
            species_checklist.check(world.species_entries_by_id[entry.species_id])


def generate_trade_encounters(world: "PokemonBWWorld",
                              species_checklist: SpeciesChecklist) -> dict[str, TradeEncounterEntry]:
    from ...data.locations.encounters.static import trade

    is_black = world.options.version == "black"
    is_dynamic = world.options.version.current_key == "dynamic"  # .current_key == ... because dynamic might not be added yet
    versioned_species = (
        (lambda d: d.species_black)
        if is_black or (is_dynamic and world.random.random() < 0.5)
        else (lambda d: d.species_white)
    )
    versioned_wanted = (
        (lambda d: d.wanted_black)
        if is_black or (is_dynamic and world.random.random() < 0.5)
        else (lambda d: d.wanted_white)
    )

    encounters: dict[str, TradeEncounterEntry] = {}
    for name, data in trade.items():
        diff_enc = data.species_black != data.species_white
        encounters[name] = TradeEncounterEntry(versioned_species(data), versioned_wanted(data),
                                               data.encounter_region, diff_enc)
        if not world.options.modify_logic.is_consider_trades:
            continue
        if not world.options.modify_logic.is_consider_static and not world.options.randomize_wild_pokemon.is_randomize:
            continue
        if is_dynamic and diff_enc:
            continue
        species_checklist.check(world.species_entries_by_id[versioned_species(data)])
        species_checklist.add(world.species_entries_by_id[(versioned_wanted(data), 0)])

    return encounters


def generate_starters(world: "PokemonBWWorld"):
    from ...data.locations.encounters.static import starters

    mods = world.options.randomize_starter_pokemon

    if not mods.is_randomize:
        # All three starters are the same in both versions, so no need to get the versioned species
        world.static_encounter |= {name: StaticEncounterEntry(data.species_black, data.encounter_region,
                                                              data.inclusion_rule, data.access_rule, False, 0)
                                   for name, data in starters.items()}
        return

    used_types = []
    official = (1, 4, 7, 152, 155, 158, 252, 255, 258, 387, 390, 393, 495, 498, 501)
    vanilla_types = ("Grass", "Fire", "Water")

    encounters = world.static_encounter
    for name, data in starters.items():
        possible = [world.species_entries_by_id[i, 0] for i in (official if mods.is_only_official else range(1, 650))]
        if not mods.is_only_official and (mods.is_any_base or mods.is_base_2_evos):
            possible = [spec for spec in possible if not spec.pre_evolutions] or possible
        if not mods.is_only_official and mods.is_base_2_evos:
            possible = [spec for spec in possible
                        if any(evo.species.evolutions for evo in spec.evolutions)] or possible
        if mods.is_vanilla_types:
            possible = [spec for spec in possible
                        if spec.types[0] in vanilla_types or spec.types[1] in vanilla_types] or possible
        if mods.is_type_variety:
            possible = [spec for spec in possible
                        if spec.types[0] not in used_types and spec.types[1] not in used_types] or possible
        if mods.is_similar_stats:
            # Similar stats at last because it gradually increases instead of simple True/False
            stat_tolerance = world.options.pokemon_randomization_adjustments["Stats leniency"]
            vanilla_spec = world.species_entries_by_id[data.species_black]  # Species is same in both versions anyway
            while True:
                if next := [spec for spec in possible
                            if abs(sum(vanilla_spec.base_stats) - sum(spec.base_stats)) <= stat_tolerance]:
                    possible = next
                    break
                stat_tolerance += 10
        chosen = world.random.choice(possible)
        used_types += chosen.types
        encounters[name] = StaticEncounterEntry((chosen.dex_number, chosen.form), data.encounter_region,
                                                data.inclusion_rule, data.access_rule, False, 0b1)
