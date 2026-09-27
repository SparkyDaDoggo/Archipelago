from typing import TYPE_CHECKING
from .. import StaticEncounterEntry, TradeEncounterEntry, SpeciesChecklist

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def generate_static_encounters(world: "PokemonBWWorld",
                               species_checklist: SpeciesChecklist) -> dict[str, StaticEncounterEntry]:
    from ...data.locations.encounters.static import static, legendary, fossils, gift

    is_dynamic = world.options.version.current_key == "dynamic"  # .current_key == ... because dynamic might not be added yet
    versioned_species = (
        (lambda d: d.species_white)
        if world.options.version == "white" or (is_dynamic and world.random.random() < 0.5)
        else (lambda d: d.species_black)
    )

    encounters: dict[str, StaticEncounterEntry] = {}
    for table in (static, legendary, fossils, gift):
        for name, data in table.items():
            diff_enc = data.species_black != data.species_white
            encounters[name] = StaticEncounterEntry(versioned_species(data), data.encounter_region,
                                                    data.inclusion_rule, data.access_rule, diff_enc, 0)
            if not world.options.modify_logic.is_consider_static:
                continue
            if data.inclusion_rule and not data.inclusion_rule(world):
                continue
            if is_dynamic and diff_enc:
                continue
            species_checklist.check(world.species_entries_by_id[versioned_species(data)])

    return encounters


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


def generate_starters(world: "PokemonBWWorld") -> dict[str, StaticEncounterEntry]:
    from ...data.locations.encounters.static import starters

    mods = world.options.randomize_starter_pokemon

    if not mods.is_randomize:
        # All three starters are the same in both versions, so no need to get the versioned species
        return {name: StaticEncounterEntry(data.species_black, data.encounter_region, data.inclusion_rule,
                                           data.access_rule, False, 0) for name, data in starters.items()}

    used_types = []
    official = (1, 4, 7, 152, 155, 158, 252, 255, 258, 387, 390, 393, 495, 498, 501)
    vanilla_types = ("Grass", "Fire", "Water")

    encounters: dict[str, StaticEncounterEntry] = {}
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

    return encounters
