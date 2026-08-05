from typing import TYPE_CHECKING, Callable

from BaseClasses import Location, Region, CollectionState

if TYPE_CHECKING:
    from . import PokemonBWWorld
    from .data import RulesDict, ExtendedRule, AccessRule
    from .generate import SpeciesEntry


class PokemonBWLocation(Location):
    game = "Pokemon Black and White"


def get_location_lookup_table() -> dict[str, int]:
    from .generate.locations import (overworld_items, hidden_items, other, badge_rewards, tm_hm, dexsanity,
                                     dexcountsanity)

    return {
        **overworld_items.lookup(100000),
        **hidden_items.lookup(200000),
        **other.lookup(300000),
        **badge_rewards.lookup(400000),
        **tm_hm.lookup(500000),
        **dexsanity.lookup(600000),
        **dexcountsanity.lookup(602000),
    }


def get_regions(world: "PokemonBWWorld") -> dict[str, Region]:
    from .data.locations import regions
    from .data.locations.encounters import regions as encounter_regions

    return {
        name: Region(name, world.player, world.multiworld)
        for name in regions.region_list
    } | {
        name: Region(name, world.player, world.multiworld)
        for name in encounter_regions.region_list
    }


def create_rule_dict(world: "PokemonBWWorld") -> "RulesDict":
    from .data.locations.rules import extended_rules_list

    def f(r: "ExtendedRule") -> Callable[[CollectionState], bool]:
        return lambda state: r(state, world)

    return {rule: f(rule) for rule in extended_rules_list} | {None: None}


def create_and_place_event_locations(world: "PokemonBWWorld") -> dict[str, "SpeciesEntry"]:
    """Returns a dict of species that are actually catchable in this world."""
    from .generate.events import wild, static, evolutions, goal, species_tables, form_change

    catchable_species_data: dict[str, "SpeciesEntry"] = wild.create(world) | static.create(world)
    evolutions.create(world, catchable_species_data)
    form_change.create(world, catchable_species_data)
    species_tables.populate(world, catchable_species_data)
    goal.create(world)
    return catchable_species_data


def create_and_place_locations(world: "PokemonBWWorld", catchable_species_data: dict[str, "SpeciesEntry"]) -> None:
    from .generate.locations import (overworld_items, hidden_items, other, badge_rewards, tm_hm, dexsanity,
                                     dexcountsanity)

    overworld_items.create(world)
    hidden_items.create(world)
    other.create(world, catchable_species_data)
    badge_rewards.create(world)
    tm_hm.create(world)
    dexsanity.create(world, catchable_species_data)
    dexcountsanity.create(world, catchable_species_data)


def connect_regions(world: "PokemonBWWorld") -> None:
    from .data.locations import region_connections as gameplay_connections
    from .data.locations.encounters import region_connections as encounter_connections

    # Create gameplay region connections
    for name, data in gameplay_connections.connections.items():
        world.regions[data.exiting_region].connect(
            world.regions[data.entering_region], name, world.rules_dict[data.rule]
        )

    def combine_and(connection_rules: tuple["ExtendedRule", ...]) -> "AccessRule":
        def f(state) -> bool:
            for r in connection_rules:
                if not r(state, world):
                    return False
            return True
        return f

    for name, data in encounter_connections.connections.items():
        if (data.inclusion_rule is None) or data.inclusion_rule(world):
            if data.rules not in world.rules_dict:
                # Assuming single rules are already in rules because of extended_rules_list
                world.rules_dict[data.rules] = combine_and(data.rules)
            world.regions[data.exiting_region].connect(
                world.regions[data.entering_region], name, world.rules_dict[data.rules]
            )

    world.multiworld.register_indirect_condition(
        world.regions["N's Castle"], world.get_entrance("Relic Castle B5F castleside")
    )
    world.multiworld.register_indirect_condition(
        world.regions["Nimbasa City"], world.get_entrance("Pinwheel Forest east")
    )
    world.multiworld.register_indirect_condition(
        world.regions["Mistralton Cave Inner"], world.get_entrance("Victory Road cave behind boulder")
    )


def cleanup_regions(regions: dict[str, Region]) -> None:
    to_remove = []
    for name, region in regions.items():
        if len(region.entrances) == 0 and region.name != "Menu":
            to_remove.append(name)
    for name in to_remove:
        regions.pop(name)


def count_to_be_filled_locations(regions: dict[str, Region]) -> int:
    count = 0
    for region in regions.values():
        for location in region.locations:
            if location.item is None:
                count += 1
    return count


class StrVar:
    value: str | None = None

    def __init__(self, value: str | None = None):
        self.value = value


def extend_species_hints(world: "PokemonBWWorld", hint_data: dict[int, dict[int, str]]) -> None:
    from .data.locations.encounters.region_connections import connection_by_region
    from .data.pokemon.pokedex import by_number

    # {dex: ({wild/static places}, [(trade, wanted dex), ...], [pre-evo dex])}
    places_for_location: dict[int, tuple[set[str], list[tuple[str, int]], list[int], StrVar]] = {}

    # Wild encounter
    for slot, entry in world.wild_encounter.items():
        catching_place = connection_by_region[slot[:slot.rindex(" ")]]
        dex = entry.species_id[0]
        if dex not in places_for_location:
            places_for_location[dex] = set(), [], [], StrVar()
        places_for_location[dex][0].add(catching_place)

    # Static encounter
    if world.options.modify_logic.is_consider_static:
        for static_slot, entry in world.static_encounter.items():
            catching_place = static_slot[:static_slot.rfind("Encounter")]
            dex = entry.species_id[0]
            if dex not in places_for_location:
                places_for_location[dex] = set(), [], [], StrVar()
            places_for_location[dex][0].add(catching_place)

    # Trade encounter
    if world.options.modify_logic.is_consider_trades and (world.options.modify_logic.is_consider_static
                                                          or world.options.randomize_wild_pokemon.is_randomize):
        for trade_slot, entry in world.trade_encounter.items():
            catching_place = trade_slot[:trade_slot.rindex('Encounter')]
            dex = entry.species_id[0]
            wanted_dex = entry.wanted_dex_number
            if dex not in places_for_location:
                places_for_location[dex] = set(), [], [], StrVar()
            places_for_location[dex][1].append((catching_place, wanted_dex))

    # Evolutions
    if world.options.modify_logic.is_consider_evos:
        for species, data in world.species_entries.items():
            for evo in data.evolutions:
                pre_evo_dex = data.dex_number
                if evo[2] not in places_for_location:
                    places_for_location[evo[2]] = set(), [], [], StrVar()
                places_for_location[evo[2]][2].append(pre_evo_dex)

    def build_string(_dex: int, _depth=0) -> str:
        if places_for_location[_dex][3].value:
            return places_for_location[_dex][3].value
        _buffer = list(places_for_location[_dex][0])
        _buffer.sort()
        for _loc, _wanted_dex in places_for_location[_dex][1]:
            _wanted_name = by_number[_wanted_dex]
            if _wanted_dex in places_for_location and _depth < 3:
                _buffer.append(f"{_loc} (wants {_wanted_name}, found at {build_string(_wanted_dex, _depth+1)})")
            else:
                _buffer.append(f"{_loc} (wants {_wanted_name})")
        for _pre_evo_dex in places_for_location[_dex][2]:
            _pre_evo_name = by_number[_pre_evo_dex]
            if _pre_evo_dex in places_for_location and _depth < 3:
                _buffer.append(f"Evolving {_pre_evo_name} (found at {build_string(_pre_evo_dex, _depth+1)})")
            else:
                _buffer.append(f"Evolving {_pre_evo_name}")
        _built = ", ".join(_buffer)
        places_for_location[_dex][3].value = _built
        return _built

    for dex in places_for_location:
        loc_id = world.location_name_to_id[f"Pokédex - {by_number[dex]}"]
        hint_data[world.player][loc_id] = build_string(dex)

    deerling_npc_id = world.location_name_to_id["Route 6 - Item from scientist for all Deerling forms"]
    hint_data[world.player][deerling_npc_id] = build_string(585)
