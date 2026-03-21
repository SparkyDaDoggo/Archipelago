from typing import TYPE_CHECKING
from .. import StaticEncounterEntry, TradeEncounterEntry, SpeciesChecklist

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def generate_static_encounters(world: "PokemonBWWorld",
                               species_checklist: SpeciesChecklist) -> dict[str, StaticEncounterEntry]:
    from ...data.locations.encounters.static import static, legendary, fossils, gift
    from ...data.pokemon.species import by_id

    versioned_species = (
        (lambda d: d.species_white)
        if world.options.version == "white"
        else (lambda d: d.species_black)
    )

    encounters: dict[str, StaticEncounterEntry] = {}
    for table in (static, legendary, fossils, gift):
        for name, data in table.items():
            encounters[name] = StaticEncounterEntry(
                versioned_species(data), data.encounter_region, data.inclusion_rule, data.access_rule
            )
            if (
                (data.inclusion_rule is None or data.inclusion_rule(world))
                and world.options.modify_logic.is_consider_static
            ):
                species_checklist.check(by_id[versioned_species(data)])

    return encounters


def generate_trade_encounters(world: "PokemonBWWorld",
                              species_checklist: SpeciesChecklist) -> dict[str, TradeEncounterEntry]:
    from ...data.locations.encounters.static import trade
    from ...data.pokemon.species import by_id

    is_black = world.options.version == "black"
    versioned_species = (
        (lambda d: d.species_black)
        if is_black
        else (lambda d: d.species_white)
    )
    versioned_wanted = (
        (lambda d: d.wanted_black)
        if is_black
        else (lambda d: d.wanted_white)
    )

    encounters: dict[str, TradeEncounterEntry] = {}
    for name, data in trade.items():
        encounters[name] = TradeEncounterEntry(
            versioned_species(data),
            versioned_wanted(data),
            data.encounter_region
        )
        if (world.options.modify_logic.is_consider_trades and (world.options.modify_logic.is_consider_static
                                                               or world.options.randomize_wild_pokemon.is_randomize)):
            species_checklist.check(by_id[versioned_species(data)])
            species_checklist.add(by_id[(versioned_wanted(data), 0)])

    return encounters
