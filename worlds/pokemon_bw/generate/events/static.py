from typing import TYPE_CHECKING, Callable

from ...locations import PokemonBWLocation
from BaseClasses import ItemClassification, CollectionState
from ...items import PokemonBWItem

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from BaseClasses import Region
    from .. import SpeciesEntry


def create(world: "PokemonBWWorld") -> dict[str, "SpeciesEntry"]:
    from ...generate import TradeEncounterEntry, StaticEncounterEntry

    catchable_species_data: dict[str, "SpeciesEntry"] = {}

    def get_trade_rule(x: str) -> Callable[[CollectionState], bool]:
        return lambda state: state.has(x, world.player)

    def f(table: dict[str, TradeEncounterEntry | StaticEncounterEntry], is_static: bool):
        for name, data in table.items():
            if not is_static or ((data.inclusion_rule is None) or data.inclusion_rule(world)):
                r: "Region" = world.regions[data.encounter_region]
                l: PokemonBWLocation = PokemonBWLocation(world.player, name, None, r)
                species_id: tuple[int, int] = data.species_id
                species_name: str = world.species_entries_by_id[species_id].species_name
                item: PokemonBWItem = PokemonBWItem(species_name, ItemClassification.progression, None, world.player)
                l.place_locked_item(item)
                l.show_in_spoiler = False
                if is_static:
                    if data.access_rule is not None:
                        l.access_rule = world.rules_dict.get_or_add(data.access_rule)
                else:
                    l.access_rule = get_trade_rule(world.species_entries_by_id[data.wanted_dex_number, 0].species_name)
                r.locations.append(l)

                species_data: "SpeciesEntry" = world.species_entries[species_name]
                catchable_species_data[species_name] = species_data

    if world.options.modify_logic.is_consider_static:
        f(world.static_encounter, True)
    if world.options.modify_logic.is_consider_trades and (world.options.modify_logic.is_consider_static or
                                                          world.options.randomize_wild_pokemon.is_randomize):
        f(world.trade_encounter, False)

    return catchable_species_data
