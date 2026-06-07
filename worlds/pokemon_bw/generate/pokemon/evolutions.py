from typing import TYPE_CHECKING, Callable, Iterable
from .. import SpeciesEntry, EvoLine

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def replace_evolutions(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]):

    replace = world.options.replace_evo_methods

    # Assumes the evolutions list is already a copy
    if replace.is_locations:
        for poke_name in ("Nosepass", "Magneton"):
            dat = all_species[poke_name]
            dat.write |= 1
            evos = dat.evolutions
            for i in range(len(evos)):
                if evos[i][0] == "Magnetic area":
                    evos[i] = ("Stone", 83, evos[i][2])
        dat = all_species["Eevee"]
        dat.write |= 1
        evos = dat.evolutions
        for i in range(len(evos)):
            if evos[i][0] == "Level up moss rock":
                evos[i] = ("Stone", 85, evos[i][2])
            elif evos[i][0] == "Level up ice rock":
                evos[i] = ("Stone", 107, evos[i][2])
    if replace.is_friendship:
        for poke_name in ("Swadloon", "Golbat"):
            dat = all_species[poke_name]
            dat.write |= 1
            evos = dat.evolutions
            for i in range(len(evos)):
                if evos[i][0] == "Friendship":
                    evos[i] = ("Level up", 32, evos[i][2])
        for data in all_species.values():
            evos = data.evolutions
            for i in range(len(evos)):
                if replace.is_friendship and evos[i][0] == "Friendship":
                    evos[i] = ("Level up", 20, evos[i][2])
                    data.write |= 1
    if replace.is_pid:
        for poke_name in ("Kirlia", "Snorunt"):
            dat = all_species[poke_name]
            dat.write |= 1
            evos = dat.evolutions
            for i in range(len(evos)):
                if evos[i][0] in ("Stone female", "Stone male"):
                    evos[i] = ("Stone", evos[i][1], evos[i][2])
        for poke_name in ("Burmy (Plant)", "Burmy (Sandy)", "Burmy (Trash)", "Combee"):
            dat = all_species[poke_name]
            dat.write |= 1
            evos = dat.evolutions
            for i in range(len(evos)):
                if evos[i][0] == "Level up (female)":
                    evos[i] = ("Level up", evos[i][1], evos[i][2])
        for poke_name in ("Burmy (Plant)", "Burmy (Sandy)", "Burmy (Trash)"):
            dat = all_species[poke_name]
            dat.write |= 1
            evos = dat.evolutions
            for i in range(len(evos)):
                if evos[i][0] == "Level up (male)":
                    evos[i] = ("Level up with party member", 49, evos[i][2])
        dat = all_species["Wurmple"]
        dat.write |= 1
        evos = dat.evolutions
        for i in range(len(evos)):
            if evos[i][0] == "Level up Silcoon":
                evos[i] = ("Level up with party member", 12, evos[i][2])
            elif evos[i][0] == "Level up Cascoon":
                evos[i] = ("Level up with party member", 49, evos[i][2])
    if replace.is_stats:
        dat = all_species["Tyrogue"]
        dat.write |= 1
        evos = dat.evolutions
        for i in range(len(evos)):
            if evos[i][0] == "Level up higher defense":
                evos[i] = ("Level up item day", 0x002F, evos[i][2])
                evos.append(("Level up item night", 0x002F, evos[i][2]))
            elif evos[i][0] == "Level up higher attack":
                evos[i] = ("Level up item day", 0x002E, evos[i][2])
                evos.append(("Level up item night", 0x002E, evos[i][2]))
            elif evos[i][0] == "Level up equal physical":
                evos[i] = ("Level up item day", 0x0030, evos[i][2])
                evos.append(("Level up item night", 0x0030, evos[i][2]))


def randomize_evolutions(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]):
    from ...data.pokemon import species as species_tables, evolution_methods, moves as move_tables, movesets_level_up
    from ...items import random_choice_nested

    mods = world.options.randomize_evolutions
    replace = world.options.replace_evo_methods
    stats_total: Callable[[SpeciesEntry], int] = lambda _d: (
        _d.base_hp + _d.base_attack + _d.base_defense +
        _d.base_sp_attack + _d.base_sp_defense + _d.base_speed
    )

    if not mods.is_randomize:
        return

    def update_evo_stuff(_data: SpeciesEntry, _target_data: SpeciesEntry, _curr_targets: set):
        _curr_targets.add(_target_data.dex_number)
        if _data.evo_line and _target_data.evo_line:
            if _data.evo_line.search() != _target_data.evo_line.search():
                _data.evo_line.merge(_target_data.evo_line)
            update_evo_stage(_target_data, _data.evolution_stage + 1)
        elif _data.evo_line:
            _data.evo_line.search().members.add(_target_data.dex_number)
            _target_data.evo_line = _data.evo_line
        elif _target_data.evo_line:
            _target_data.evo_line.search().members.add(_data.dex_number)
            _data.evo_line = _target_data.evo_line
            _data.evolution_stage = 1
            update_evo_stage(_target_data, 2)
        else:
            evo_line = EvoLine()
            evo_line.type = _data.type_1 if _data.type_1 in (_target_data.type_1, _target_data.type_2) else _data.type_2
            evo_line.members = {_data.dex_number, _target_data.dex_number}
            _data.evo_line = _target_data.evo_line = evo_line
            _data.evolution_stage, _target_data.evolution_stage = 1, 2

    def update_evo_stage(_data: SpeciesEntry, stage: int):
        if _data.evolution_stage < stage:
            _data.evolution_stage = stage
            if stage < 3:
                for _evo in _data.evolutions:
                    update_evo_stage(all_species[species_tables.by_id[(_evo[2], 0)]], stage + 1)

    def resolve_paired(_met: str) -> str:
        if _met in ("Level up item day", "Level up item night"):
            return "_Level up item"
        elif _met in ("Level up Ninjask", "Level up Shedinja"):
            return "_Level up split"
        elif mods.is_pair_50_50 and _met in ("Level up Silcoon", "Level up Cascoon"):
            return "_Level up PID"
        elif mods.is_pair_stats and _met in ("Level up higher defense", "Level up higher attack", "Level up equal physical"):
            return "_Level up stats"
        else:
            return _met

    levelup_weight = world.options.stats_randomization_adjustments["Level up evo weight"]
    max_level = world.options.stats_randomization_adjustments["Maximum evo level"]
    if mods.is_random_methods and levelup_weight != -1:
        random_method = ("Level up", ) * levelup_weight + ((
            "Stone" if replace.is_pid else ("Stone", ) * 38 + ("Stone male", "Stone female"),
            "_Level up item",
            ("_Level up split", "_Level up item", "Stone"),
            ("Level up with move", "_Level up item", "Stone"),
            ("Level up with party member", "_Level up item", "Stone", "_Level up item", "Stone"),
        ) + (
            ("Friendship", ) if not replace.is_friendship else ()
        ) + (
            (("Magnetic area", "Level up moss rock", "Level up ice rock"), ) if not replace.is_locations else ()
        ) + (
            (("Level up higher defense", "Level up higher attack", "Level up equal physical")
             if not mods.is_pair_stats else "_Level up stats", ) if not replace.is_stats else ()
        ) + (
            (("Level up Silcoon", "Level up Cascoon") if not mods.is_pair_50_50 else "_Level up PID",
             ("Level up (female)", "Level up (male)")) if not replace.is_pid else ()
        ), )
    else:
        random_method = ("Level up",)

    for data in all_species.values():
        if not data.write & 2:
            if not data.evo_line:
                data.evolution_stage = 0
            data.evolutions = []
            data.write |= 1

    def _get_random_target(_curr_targets: set, this: str, _dat: SpeciesEntry) -> tuple[str | None, SpeciesEntry | None]:
        picked = world.random.randrange(1, 650) - 1
        end = picked - 1
        while picked != end:
            picked = picked % 649 + 1
            picked_name = species_tables.by_id[(picked, 0)]
            picked_data = all_species[picked_name]
            picked_types = (picked_data.type_1, picked_data.type_2)
            if this == picked_name:
                continue
            if mods.is_common_type and _dat.type_1 not in picked_types and _dat.type_2 not in picked_types:
                continue
            if mods.is_follow_type:
                _dat.evo_line = _dat.evo_line.search()
                picked_data.evo_line = picked_data.evo_line.search()
                if _dat.evo_line and picked_data.evo_line:
                    if _dat.evo_line.type != picked_data.evo_line.type:
                        continue
                elif _dat.evo_line:
                    if _dat.evo_line.type not in picked_types:
                        continue
                elif picked_data.evo_line:
                    if picked_data.evo_line.type not in (_dat.type_1, _dat.type_2):
                        continue
                elif _dat.type_1 not in picked_types and _dat.type_2 not in picked_types:
                    continue
            if not mods.is_multiple_pre and picked_data.evolution_stage >= 2:
                continue
            if not mods.is_looping_lines and _dat.evo_line and this in _dat.evo_line and picked_data.dex_number not in _curr_targets:
                continue
            if mods.is_increasing_stats and stats_total(_dat) > stats_total(picked_data):
                continue
            return picked_name, picked_data
        return None, None

    split = world.random.randrange(1, 650)
    for dex_num in (*range(split, 650), *range(split)):
        name = species_tables.by_id[(dex_num, 0)]
        data = all_species[name]
        if data.write & 2:
            continue
        method_list: list[tuple[str, int]] = []
        method_slots = 0  # Some methods need multiple slots, e.g. Level up item always needing day and night variants

        if not mods.is_random_methods:
            restricted_methods = []
            for evo in data.evolutions:
                method = resolve_paired(evo[0])
                if method not in restricted_methods:
                    restricted_methods.append(method)
        else:
            restricted_methods = random_method

        if data.gender_ratio in (0, 254, 255):
            bad = (() + (("Level up (male)", "Stone male") if data.gender_ratio in (254, 255) else ())
                   + (("Level up (female)", "Stone female") if data.gender_ratio in (0, 255) else ()))

            def cop(obj: Iterable) -> Iterable:
                return tuple((o if isinstance(o, str) else cop(o)) for o in obj if o and (o not in bad))

            restricted_methods = cop(restricted_methods) or ("Level up", )

        if mods.is_every_level:
            method_list.append(("Level up", 2))
            method_slots += 1
            if mods.is_more_less_branches:
                while method_slots < 7 and world.random.random() < 0.5:
                    method = random_choice_nested(world.random, restricted_methods)
                    method_list.insert(0, (method, -1))
                    method_slots += evolution_methods.paired_method_slots.get(method, 1)
        elif mods.is_more_less_branches:
            while method_slots < 7 and world.random.random() < 0.75:
                method = random_choice_nested(world.random, restricted_methods)
                method_list.insert(0, (method, -1))
                method_slots += evolution_methods.paired_method_slots.get(method, 1)
        else:
            for evo in data.evolutions:
                if evo[0] in ("Level up item night", "Level up Shedinja") or (
                    mods.is_pair_stats and evo[0] in ("Level up higher attack", "Level up equal physical")
                ) or (mods.is_pair_50_50 and evo[0] == "Level up Cascoon"):
                    continue
                if data.gender_ratio in (0, 255) and evo[0] in ("Level up (female)", "Stone female"):
                    continue
                if data.gender_ratio in (254, 255) and evo[0] in ("Level up (male)", "Stone male"):
                    continue
                method = resolve_paired(evo[0]) if not mods.is_random_methods else random_choice_nested(world.random, restricted_methods)
                method_list.insert(0, (method, evo[1]))
                method_slots += evolution_methods.paired_method_slots.get(method, 1)

        curr_evo_targets = set()  # ONLY LOOKUP
        curr_max_lvl = 1
        for method, value in reversed(method_list):
            target_name, target_data = _get_random_target(curr_evo_targets, name, data)
            if target_name is None:
                continue

            match method:
                case c if c in ("Level up", "Level up higher defense", "Level up higher attack",
                                "Level up equal physical", "Level up Silcoon", "Level up Cascoon",
                                "Level up (female)", "Level up (male)"):
                    lvl = min(value if value != -1 else int(world.random.triangular(
                        curr_max_lvl+1, max_level + 0.9, curr_max_lvl + (max_level - curr_max_lvl + 1) // 4)), max_level)
                    curr_max_lvl = lvl
                    data.evolutions.insert(0, (method, lvl, target_data.dex_number))
                case c if c in ("Stone", "Stone male", "Stone female"):
                    item_id = value if value != -1 else world.random.choice(evolution_methods.stone_items)
                    data.evolutions.insert(0, (method, item_id, target_data.dex_number))
                case c if c in ("Friendship", "Magnetic area", "Level up moss rock", "Level up ice rock"):
                    data.evolutions.insert(0, (method, 0, target_data.dex_number))
                case "Level up with move":
                    move_id = value if value != -1 else move_tables.by_name[world.random.choice(movesets_level_up.table[name].level_up_moves)[1]]
                    data.evolutions.insert(0, ("Level up with move", move_id, target_data.dex_number))
                case "Level up with party member":
                    wanted_dex = value if value != -1 else world.random.randrange(1, 650)
                    data.evolutions.insert(0, ("Level up with move", wanted_dex, target_data.dex_number))
                case "_Level up item":
                    item_id = value if value != -1 else world.random.choice(evolution_methods.hold_items)
                    data.evolutions.insert(0, ("Level up item night", item_id, target_data.dex_number))
                    data.evolutions.insert(0, ("Level up item day", item_id, target_data.dex_number))
                case "_Level up split":
                    target2_name, target2_data = _get_random_target(curr_evo_targets, name, data)
                    if target2_name is None:
                        target2_name, target2_data = target_name, target_data
                    lvl = min(value if value != -1 else int(world.random.triangular(
                        curr_max_lvl+1, max_level + 0.9, curr_max_lvl + (max_level - curr_max_lvl + 1) // 4)), max_level)
                    curr_max_lvl = lvl
                    data.evolutions.insert(0, ("Level up Shedinja", lvl, target_data.dex_number))
                    data.evolutions.insert(0, ("Level up Ninjask", lvl, target2_data.dex_number))
                    update_evo_stuff(data, target2_data, curr_evo_targets)
                case "_Level up PID":
                    target2_name, target2_data = _get_random_target(curr_evo_targets, name, data)
                    if target2_name is None:
                        target2_name, target2_data = target_name, target_data
                    lvl = min(value if value != -1 else int(world.random.triangular(
                        curr_max_lvl+1, max_level + 0.9, curr_max_lvl + (max_level - curr_max_lvl + 1) // 4)), max_level)
                    curr_max_lvl = lvl
                    data.evolutions.insert(0, ("Level up Cascoon", lvl, target_data.dex_number))
                    data.evolutions.insert(0, ("Level up Silcoon", lvl, target2_data.dex_number))
                    update_evo_stuff(data, target2_data, curr_evo_targets)
                case "_Level up stats":
                    target2_name, target2_data = _get_random_target(curr_evo_targets, name, data)
                    if target2_name is None:
                        target2_name, target2_data = target_name, target_data
                    target3_name, target3_data = _get_random_target(curr_evo_targets, name, data)
                    if target3_name is None:
                        target3_name, target3_data = target_name, target_data
                    lvl = min(value if value != -1 else int(world.random.triangular(
                        curr_max_lvl+1, max_level + 0.9, curr_max_lvl + (max_level - curr_max_lvl + 1) // 4)), max_level)
                    curr_max_lvl = lvl
                    data.evolutions.insert(0, ("Level up equal physical", lvl, target3_data.dex_number))
                    data.evolutions.insert(0, ("Level up higher attack", lvl, target2_data.dex_number))
                    data.evolutions.insert(0, ("Level up higher defense", lvl, target_data.dex_number))
                    update_evo_stuff(data, target2_data, curr_evo_targets)
                    update_evo_stuff(data, target3_data, curr_evo_targets)

            update_evo_stuff(data, target_data, curr_evo_targets)

    for data in all_species.values():
        if not data.form or data.write & 2:
            continue
        base_data = all_species[species_tables.by_id[(data.dex_number, 0)]]
        data.evolutions, data.evolution_stage, data.evo_line \
            = base_data.evolutions.copy(), base_data.evolution_stage, base_data.evo_line
