from typing import TYPE_CHECKING, Self

from BaseClasses import Location, Region, MultiWorld, CollectionState, Entrance, ItemClassification
from worlds.AutoWorld import LogicMixin
from .data import TrainerData

if TYPE_CHECKING:
    from . import PokemonBWWorld
    from .generate import SpeciesEntry


class PokemonBWLocation(Location):
    game = "Pokemon Black and White"


def get_location_lookup_table() -> dict[str, int]:
    from .generate.locations import (overworld_items, hidden_items, other, badge_rewards, tm_hm)
    from .generate.locations.sanity import (dexsanity, shinysanity, seensanity, shinycountsanity, seencountsanity,
                                            dexcountsanity, formsanity, formcountsanity, shinyformsanity,
                                            shinyformcountsanity)
    from .options.sanity import DEXSANITYSANITY_ENABLED
    ret = {
        **overworld_items.lookup(100000),
        **hidden_items.lookup(200000),
        **other.lookup(300000),
        **badge_rewards.lookup(400000),
        **tm_hm.lookup(500000),
        **dexsanity.lookup(600000),
        **dexcountsanity.lookup(602000),
        **seensanity.lookup(604000),
        **formsanity.lookup(606000),
        **shinysanity.lookup(608000),
    }
    if DEXSANITYSANITY_ENABLED:
        ret |= {
            **seencountsanity.lookup(700000),
            **formcountsanity.lookup(702000),
            **shinycountsanity.lookup(704000),
            **shinyformsanity.lookup(706000),
            **shinyformcountsanity.lookup(708000),
        }
    return ret


def get_regions(world: "PokemonBWWorld") -> dict[str, Region]:
    from .data.locations import regions
    from .data.locations.encounters import regions as encounter_regions

    enc = {}
    for name, data in encounter_regions.region_list.items():
        if not data.seasons:
            for m in data.methods:
                r_name = f"{name} - {m}"
                enc[r_name] = Region(r_name, world.player, world.multiworld)
        else:
            for m in data.spring_methods:
                r_name = f"{name} (Spring) - {m}"
                enc[r_name] = Region(r_name, world.player, world.multiworld)
            for m in data.summer_methods:
                r_name = f"{name} (Summer) - {m}"
                enc[r_name] = Region(r_name, world.player, world.multiworld)
            for m in data.autumn_methods:
                r_name = f"{name} (Autumn) - {m}"
                enc[r_name] = Region(r_name, world.player, world.multiworld)
            for m in data.winter_methods:
                r_name = f"{name} (Winter) - {m}"
                enc[r_name] = Region(r_name, world.player, world.multiworld)

    return {
        name: Region(name, world.player, world.multiworld)
        for name in regions.region_list
    } | enc


def create_and_place_event_locations(world: "PokemonBWWorld") -> tuple[dict[str, "SpeciesEntry"], dict[str, "SpeciesEntry"]]:
    """Returns a dict of species that are actually catchable in this world."""
    from .generate.events import wild, static, evolutions, goal, species_tables, form_change, levels, story, trainers
    from .items import PokemonBWItem
    from .data.items import all_tm_hm
    from .data.pokemon import moves

    # species data dicts
    catchable_species_data: dict[str, "SpeciesEntry"] = wild.create(world) | static.create(world)
    evolutions.create(world, catchable_species_data)
    form_change.create(world, catchable_species_data)
    seeable_species_data: dict[str, "SpeciesEntry"] = trainers.create(world)

    # some niche locations' data
    chosen = world.random.choice(tuple(a for a in catchable_species_data.items() if a[1].tm_hm_moves.tm_hm_moves))
    world.other_locations_species = chosen[0]
    world.studio_castelia_type = world.random.choice(chosen[1].types)
    chosen_tms = list(chosen[1].tm_hm_moves.tm_hm_moves)
    chosen_tms.sort()
    chosen_tm = world.random.choice(chosen_tms)
    for name in all_tm_hm:
        if name.startswith(chosen_tm):
            world.driftveil_random_tm = name
            world.driftveil_random_move_id = world.move_entries[moves.tm_hm[chosen_tm].move].id
            break

    # other events
    levels.create(world)
    species_tables.populate(world, catchable_species_data)
    story.create(world)
    goal.create(world)

    reg = world.regions["Castelia City Castelia Street East Building 1F"]
    loc = PokemonBWLocation(world.player, "[Event] Get shown a Zorua", None, reg)
    it = PokemonBWItem("[Seen] Zorua", ItemClassification.progression, None, world.player)
    loc.place_locked_item(it)
    loc.show_in_spoiler = False
    reg.locations.append(loc)
    seeable_species_data["Zorua"] = world.species_entries["Zorua"]

    for reg in world.regions.values():
        if not len(reg.locations):
            l = PokemonBWLocation(world.player, reg.name + " (sphere)", None, reg)
            item = PokemonBWItem("Nothing", ItemClassification.progression, None, world.player)
            l.place_locked_item(item)
            l.show_in_spoiler = False
            reg.locations.append(l)

    return catchable_species_data, seeable_species_data


def create_and_place_locations(world: "PokemonBWWorld", catchable_species_data: dict[str, "SpeciesEntry"],
                               seeable_species_data: dict[str, "SpeciesEntry"]) -> None:
    from .generate.locations import overworld_items, hidden_items, other, badge_rewards, tm_hm
    from .generate.locations.sanity import (dexsanity, shinysanity, seensanity, shinycountsanity, seencountsanity,
                                            dexcountsanity, formsanity, formcountsanity, shinyformsanity,
                                            shinyformcountsanity)

    overworld_items.create(world)
    hidden_items.create(world)
    other.create(world)
    badge_rewards.create(world)
    tm_hm.create(world)
    dexsanity.create(world, catchable_species_data)
    dexcountsanity.create(world, catchable_species_data)
    seensanity.create(world, catchable_species_data, seeable_species_data)
    seencountsanity.create(world, catchable_species_data, seeable_species_data)
    formsanity.create(world, catchable_species_data, seeable_species_data)
    formcountsanity.create(world, catchable_species_data, seeable_species_data)
    shinysanity.create(world, catchable_species_data)
    shinycountsanity.create(world, catchable_species_data)
    shinyformsanity.create(world, catchable_species_data)
    shinyformcountsanity.create(world, catchable_species_data)


def connect_regions(world: "PokemonBWWorld") -> None:
    from .data.locations import region_connections as gameplay_connections, rules
    from .data.locations.encounters import region_connections as encounter_connections
    from .data import AndExtRules as AND

    for connection in gameplay_connections.connections:
        reg1 = world.regions[connection.region_1]
        reg2 = world.regions[connection.region_2]
        rule1 = world.rules_dict.get_or_add(connection.rule)
        rule2 = rule1 if connection.rule_2 is False else world.rules_dict.get_or_add(connection.rule_2)
        name = None
        if connection.entrance_name:
            name = connection.entrance_name.replace("##", connection.region_1).replace("#2#", connection.region_2)
        reg1.connect(reg2, name, rule1)
        if not connection.one_way:
            reg2.connect(reg1, name + "[back]" if name else None, rule2)

    by_season = {
        "Spring": rules.can_set_spring,
        "Summer": rules.can_set_summer,
        "Autumn": rules.can_set_autumn,
        "Winter": rules.can_set_winter,
    }
    for data in encounter_connections.connections:
        current_rules = []
        if "S" in data.entering_region[2]:
            current_rules.append(rules.can_use_surf)
        if "F" in data.entering_region[2]:
            current_rules.append(rules.can_fish)
        if "R" in data.entering_region[2]:
            current_rules.append(rules.has_trio_badge)
        if data.entering_region[1]:
            current_rules.append(by_season[data.entering_region[1]])
        reg = world.regions[data.build_name()]
        for parent in data.exiting_regions:
            world.regions[parent].connect(reg, rule=world.rules_dict.get_or_add(AND(*current_rules)))

    distances: dict[str, int] = {}
    current_regions = [world.regions["Menu"]]
    next_regions = []
    current_distance = 0
    while current_regions:
        for reg in current_regions:
            if reg.name not in distances:
                distances[reg.name] = current_distance
                for ex in reg.exits:
                    ex: Entrance
                    next_regions.append(ex.connected_region)
        current_distance += 1
        current_regions = next_regions
        next_regions = []
    world.region_distances = distances
    world.max_distance = current_distance - 1


def cleanup_regions(regions: dict[str, Region]) -> None:
    # Mainly intended wild encounter regions that aren't connected because of vanilla seasons
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
    from .data.pokemon.pokedex import by_number
    from .data.locations.sanity import formsanity, shinyformsanity
    from .data.trainers.data import table as trainer_table
    from .data.pokemon.species import by_name

    # {dex: ({wild/static places}, [(trade, wanted dex), ...], [pre-evo dex], string so far, seen string so far, [trainers])}
    places_for_location: dict[int, tuple[
        set[str], list[tuple[str, int]], list[SpeciesEntry], StrVar, StrVar, set[TrainerData]
    ]] = {}
    logic_mods = world.options.modify_logic

    # Wild encounter
    for entry in world.wild_encounter.values():
        dex = entry.species_id[0]
        if dex not in places_for_location:
            places_for_location[dex] = set(), [], [], StrVar(), StrVar(), set()
        places_for_location[dex][0].add(entry.region)

    # Static encounter
    if logic_mods.is_consider_static:
        for static_slot, entry in world.static_encounter.items():
            catching_place = static_slot[:static_slot.rfind("Encounter")]
            dex = entry.species_id[0]
            if dex not in places_for_location:
                places_for_location[dex] = set(), [], [], StrVar(), StrVar(), set()
            places_for_location[dex][0].add(catching_place)

    # Trade encounter
    if logic_mods.is_consider_trades and (logic_mods.is_consider_static or
                                          world.options.randomize_wild_pokemon.is_randomize):
        for trade_slot, entry in world.trade_encounter.items():
            catching_place = trade_slot[:trade_slot.rindex('Encounter')]
            dex = entry.species_id[0]
            wanted_dex = entry.wanted_dex_number
            if dex not in places_for_location:
                places_for_location[dex] = set(), [], [], StrVar(), StrVar(), set()
            places_for_location[dex][1].append((catching_place, wanted_dex))

    # Evolutions
    if logic_mods.is_consider_evos and not world.options.randomize_evolutions.is_every_level:
        for species, data in world.species_entries.items():
            for evo in data.evolutions:
                evo_dex = evo.species.dex_number
                if evo_dex not in places_for_location:
                    places_for_location[evo_dex] = set(), [], [], StrVar(), StrVar(), set()
                places_for_location[evo_dex][2].append(data)

    # Trainer teams
    if logic_mods.is_consider_trainers:
        for trainer_poke in world.trainer_teams:
            trainer = trainer_table[trainer_poke.trainer_id - 1]
            if trainer.logic_inc_rule and not trainer.logic_inc_rule(world):
                continue
            dex = by_name[trainer_poke.species].dex_number
            if dex not in places_for_location:
                places_for_location[dex] = set(), [], [], StrVar(), StrVar(), set()
            places_for_location[dex][5].add(trainer)

    def build_string(_dex: int, _seen=False) -> str:
        if places_for_location[_dex][3 + _seen].value:
            return places_for_location[_dex][3 + _seen].value
        _buffer = list(places_for_location[_dex][0])
        _buffer.sort()
        if _seen:
            _buffer += sorted(f"{_t.trainer_class} {_t.name} ({_t.region})" for _t in places_for_location[_dex][5])
        for _loc, _wanted_dex in places_for_location[_dex][1]:
            _wanted_name = by_number[_wanted_dex]
            if _wanted_dex in places_for_location and sum(len(_s) for _s in _buffer) < 100:
                _buffer.append(f"{_loc} (wants {_wanted_name}, found at {build_string(_wanted_dex)})")
            else:
                _buffer.append(f"{_loc} (wants {_wanted_name})")
        for _pre_evo in places_for_location[_dex][2]:
            if _pre_evo.dex_number in places_for_location and sum(len(_s) for _s in _buffer) < 100:
                _buffer.append(f"Evolving {_pre_evo.dex_name} (found at {build_string(_pre_evo.dex_number)})")
            else:
                _buffer.append(f"Evolving {_pre_evo.dex_name}")
        _built = ", ".join(_buffer)
        places_for_location[_dex][3 + _seen].value = _built
        return _built

    for dex in places_for_location:
        if dex in world.dexsanity_numbers["dexsanity"]:
            loc_id = world.location_name_to_id[f"Pokédex - {by_number[dex]}"]
            hint_data[world.player][loc_id] = build_string(dex)
        if dex in world.dexsanity_numbers["seensanity"]:
            name = by_number[dex]
            a_an = "an" if name[0] in "AEIOU" and name != "Uxie" else "a"
            loc_id = world.location_name_to_id[f"Pokédex - See {a_an} {name}"]
            hint_data[world.player][loc_id] = build_string(dex, True)
        if dex in world.dexsanity_numbers["shinysanity"]:
            loc_id = world.location_name_to_id[f"Pokédex - Find a shiny {by_number[dex]}"]
            hint_data[world.player][loc_id] = build_string(dex)

    for loc_name, loc_data in formsanity.table.items():
        if loc_data.species_id[0] in places_for_location:
            loc_id = world.location_name_to_id[loc_name]
            hint_data[world.player][loc_id] = build_string(loc_data.species_id[0], True)

    for loc_name, loc_data in shinyformsanity.table.items():
        if loc_data.species_id[0] in places_for_location:
            loc_id = world.location_name_to_id[loc_name]
            hint_data[world.player][loc_id] = build_string(loc_data.species_id[0])

    deerling_npc_id = world.location_name_to_id["Route 6 - Item from scientist for all Deerling forms"]
    hint_data[world.player][deerling_npc_id] = build_string(585)


def temporary_debugging(world: "PokemonBWWorld"):
    pass


class PokemonBWMixin(LogicMixin):
    pokemon_bw_lvl: dict[int, list[int]]

    def init_mixin(self, multiworld: MultiWorld) -> None:
        self.pokemon_bw_lvl = {player: [0] * 21 for player in multiworld.get_game_players("Pokemon Black and White")}

    def copy_mixin(self, new_state: CollectionState | Self) -> CollectionState:
        new_state.pokemon_bw_lvl = {player: levels.copy() for player, levels in self.pokemon_bw_lvl.items()}
        return new_state
