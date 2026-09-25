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
                                                    data.inclusion_rule, data.access_rule, diff_enc)
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
