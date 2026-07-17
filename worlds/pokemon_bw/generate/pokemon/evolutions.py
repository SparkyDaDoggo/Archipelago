from typing import TYPE_CHECKING, Iterable
from .. import SpeciesEntry, EvoLine

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def would_loop_deep_search(start: SpeciesEntry, current: SpeciesEntry,
                           searched: dict[SpeciesEntry, bool] = None) -> bool:
    if searched is None:
        searched = {start: True}
    searched[current] = True
    for evo in current.evolutions:
        for evo_dat in evo[2]:
            if evo_dat == start:
                return True
            if evo_dat in searched:
                continue
            if would_loop_deep_search(start, evo_dat, searched):
                return True
    return False


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


def randomize_evolutions(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry],
                         by_id: dict[tuple[int, int], SpeciesEntry]):
    from ...data.pokemon import evolution_methods
    from ...items import random_choice_nested

    mods = world.options.randomize_evolutions
    replace = world.options.replace_evo_methods

    if not mods.is_randomize:
        return

    def update_evo_stuff(_data: SpeciesEntry, _target_data: SpeciesEntry, _curr_targets: set):
        _curr_targets.add(_target_data.dex_number)
        if _data == _target_data:
            return
        if _data.evo_line and _target_data.evo_line:
            if _data.evo_line.search() != _target_data.evo_line.search():
                _data.evo_line.merge(_target_data.evo_line)
        elif _data.evo_line:
            _data.evo_line.search().members.add(_target_data.dex_number)
            _target_data.evo_line = _data.evo_line
        elif _target_data.evo_line:
            _target_data.evo_line.search().members.add(_data.dex_number)
            _data.evo_line = _target_data.evo_line
        else:
            evo_line = EvoLine()
            evo_line.type = _data.types[0] if _data.types[0] in _target_data.types else _data.types[1]
            evo_line.members = {_data.dex_number, _target_data.dex_number}
            _data.evo_line = _target_data.evo_line = evo_line

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

    def with_customs_data(_dat: SpeciesEntry) -> tuple[SpeciesEntry, ...]:
        all_data = (_dat, )
        for form in range(6):
            if (_dat.dex_number, form) not in by_id:
                break
            form_dat = by_id[_dat.dex_number, form]
            if form and not form_dat.is_custom_form:
                continue
            all_data += (form_dat, )
        return all_data

    levelup_weight = world.options.stats_randomization_adjustments["Level up evo weight"]
    max_level = world.options.stats_randomization_adjustments["Maximum evo level"]
    if mods.is_random_methods and levelup_weight != -1:
        random_method = ("Level up", ) * levelup_weight + ((
            "Stone" if replace.is_pid else (("Stone", ) * 38 + ("Stone male", "Stone female")),
            "_Level up item",
            ("_Level up split", "_Level up item", "Stone"),
            ("Level up with move", "_Level up item", "Stone"),
            ("Level up with party member", "_Level up item", "Stone", "_Level up item", "Stone"),
        ) + (
            ("Friendship", ) if not replace.is_friendship else ("Level up", )
        ) + (
            (("Magnetic area", "Level up moss rock",
              "Level up ice rock"), ) if not replace.is_locations else ("Level up", )
        ) + (
            (("Level up higher defense", "Level up higher attack", "Level up equal physical")
             if not mods.is_pair_stats else "_Level up stats", ) if not replace.is_stats else ("Level up", )
        ) + (
            (("Level up Silcoon", "Level up Cascoon") if not mods.is_pair_50_50 else "_Level up PID",
             ("Level up (female)", "Level up (male)")) if not replace.is_pid else ("Level up", )
        ), )
    else:
        random_method = ("Level up",)

    def _get_random_target(_curr_targets: set, _dat: SpeciesEntry) -> SpeciesEntry | None:
        picked = world.random.randrange(1, 650) - 1
        end = picked - 1 if picked > 1 else 649
        while picked != end:
            picked = picked % 649 + 1
            picked_data = by_id[(picked, 0)]
            if _dat.species_name == picked_data.species_name:  # no self-evolution for now
                continue
            if mods.is_common_type and _dat.types[0] not in picked_data.types and _dat.types[1] not in picked_data.types:
                continue
            if mods.is_follow_type:
                if _dat.evo_line and picked_data.evo_line:
                    _dat.evo_line = _dat.evo_line.search()
                    picked_data.evo_line = picked_data.evo_line.search()
                    if _dat.evo_line.type != picked_data.evo_line.type:
                        continue
                elif _dat.evo_line:
                    _dat.evo_line = _dat.evo_line.search()
                    if _dat.evo_line.type not in picked_data.types:
                        continue
                elif picked_data.evo_line:
                    picked_data.evo_line = picked_data.evo_line.search()
                    if picked_data.evo_line.type not in _dat.types:
                        continue
                elif _dat.types[0] not in picked_data.types and _dat.types[1] not in picked_data.types:
                    continue
            if not mods.is_multiple_pre and picked_data.pre_evolutions and _dat not in picked_data.pre_evolutions:
                continue
            if (
                not mods.is_looping_lines and  # looping lines allowed, no further checks
                _dat.evo_line and  # pre-evo has no evo-line, cannot loop
                picked_data.evo_line and  # picked target has no evo-line, cannot loop
                picked_data.dex_number not in _curr_targets and  # if in curr_targets, then it's just an alternative method
                would_loop_deep_search(_dat, picked_data)
            ):
                continue
            if mods.is_increasing_stats and sum(_dat.base_stats) > sum(picked_data.base_stats):
                continue
            return picked_data
        return None

    split = world.random.randrange(1, 650)
    for dex_num in (*range(split, 650), *range(1, split)):
        data = by_id[dex_num, 0]  # for evo rando, we will always just copy base to all forms, even custom ones
        if data.write & 2:  # skip those overridden by plando
            continue
        method_list: list[tuple[str, int]] = []
        method_slots = 0  # Some methods need multiple slots, e.g. Level up item always needing day and night variants

        if not mods.is_random_methods:
            restricted_methods = []
            for evo in data.evolutions_copy:
                method = resolve_paired(evo[0])
                if method not in restricted_methods:
                    restricted_methods.append(method)
        else:
            restricted_methods = random_method

        bad = (() + (("Level up (male)", "Stone male") if data.gender_ratio in (254, 255) else ())
               + (("Level up (female)", "Stone female") if data.gender_ratio in (0, 255) else ()))

        def cop(obj: Iterable) -> Iterable:
            return tuple(oo for oo in ((o if isinstance(o, str) else cop(o)) for o in obj if o not in bad) if oo)

        restricted_methods = cop(restricted_methods) or ("Level up", )

        if mods.is_every_level:
            method_list.append(("Level up", 2))
            method_slots += 1
            if mods.is_more_less_branches:
                tries = 0
                while method_slots < 7 and world.random.random() < 0.5 and tries < 3:
                    method = random_choice_nested(world.random, restricted_methods)
                    add_method_slots = evolution_methods.paired_method_slots.get(method, 1)
                    if method_slots + add_method_slots <= 7:
                        method_list.insert(0, (method, -1))
                        method_slots += add_method_slots
                    else:
                        tries += 1
        elif mods.is_more_less_branches:
            tries = 0
            while method_slots < 7 and world.random.random() < 0.75 and tries < 3:
                method = random_choice_nested(world.random, restricted_methods)
                add_method_slots = evolution_methods.paired_method_slots.get(method, 1)
                if method_slots + add_method_slots <= 7:
                    method_list.insert(0, (method, -1))
                    method_slots += add_method_slots
                else:
                    tries += 1
        else:
            for evo in data.evolutions_copy:
                if evo[0] in ("Level up item night", "Level up Shedinja"):
                    continue
                if mods.is_pair_50_50 and evo[0] == "Level up Cascoon":
                    continue
                if mods.is_pair_stats and evo[0] in ("Level up higher attack", "Level up equal physical"):
                    continue
                if data.gender_ratio in (0, 255) and evo[0] in ("Level up (female)", "Stone female"):
                    continue
                if data.gender_ratio in (254, 255) and evo[0] in ("Level up (male)", "Stone male"):
                    continue
                tries = 0
                while tries < 3:
                    method = resolve_paired(evo[0]) if not mods.is_random_methods else random_choice_nested(world.random, restricted_methods)
                    add_method_slots = evolution_methods.paired_method_slots.get(method, 1)
                    if method_slots + add_method_slots <= 7:
                        method_list.insert(0, (method, evo[1] if not mods.is_random_methods else -1))
                        method_slots += evolution_methods.paired_method_slots.get(method, 1)
                        break
                    else:
                        tries += 1

        curr_evo_targets = set()  # ONLY LOOKUP
        curr_max_lvl = 1
        for method, value in reversed(method_list):
            target_data = _get_random_target(curr_evo_targets, data)
            if target_data is None:
                continue

            match method:
                case c if c in ("Level up", "Level up higher defense", "Level up higher attack",
                                "Level up equal physical", "Level up Silcoon", "Level up Cascoon",
                                "Level up (female)", "Level up (male)"):
                    lvl = min(value if value != -1 else int(world.random.triangular(
                        curr_max_lvl+1, max_level + 0.9, curr_max_lvl + (max_level - curr_max_lvl + 1) // 4)), max_level)
                    curr_max_lvl = lvl
                    data.evolutions.insert(0, (method, lvl, with_customs_data(target_data)))
                case c if c in ("Stone", "Stone male", "Stone female"):
                    item_id = value if value != -1 else world.random.choice(evolution_methods.stone_items)
                    data.evolutions.insert(0, (method, item_id, with_customs_data(target_data)))
                case c if c in ("Friendship", "Magnetic area", "Level up moss rock", "Level up ice rock"):
                    data.evolutions.insert(0, (method, 0, with_customs_data(target_data)))
                case "Level up with move":
                    move_id = value if value != -1 else world.move_entries[world.random.choice(data.level_up_moves.level_up_moves)[1]].id
                    data.evolutions.insert(0, (method, move_id, with_customs_data(target_data)))
                case "Level up with party member":
                    wanted_dex = value if value != -1 else world.random.randrange(1, 650)
                    data.evolutions.insert(0, (method, wanted_dex, with_customs_data(target_data)))
                case "_Level up item":
                    item_id = value if value != -1 else world.random.choice(evolution_methods.hold_items)
                    data.evolutions.insert(0, ("Level up item night", item_id, with_customs_data(target_data)))
                    data.evolutions.insert(0, ("Level up item day", item_id, with_customs_data(target_data)))
                case "_Level up split":
                    target2_data = _get_random_target(curr_evo_targets, data) or target_data
                    lvl = min(value if value != -1 else int(world.random.triangular(
                        curr_max_lvl+1, max_level + 0.9, curr_max_lvl + (max_level - curr_max_lvl + 1) // 4)), max_level)
                    curr_max_lvl = lvl
                    data.evolutions.insert(0, ("Level up Shedinja", lvl, with_customs_data(target_data)))
                    data.evolutions.insert(0, ("Level up Ninjask", lvl, with_customs_data(target2_data)))
                    update_evo_stuff(data, target2_data, curr_evo_targets)
                case "_Level up PID":
                    target2_data = _get_random_target(curr_evo_targets, data) or target_data
                    lvl = min(value if value != -1 else int(world.random.triangular(
                        curr_max_lvl+1, max_level + 0.9, curr_max_lvl + (max_level - curr_max_lvl + 1) // 4)), max_level)
                    curr_max_lvl = lvl
                    data.evolutions.insert(0, ("Level up Cascoon", lvl, with_customs_data(target_data)))
                    data.evolutions.insert(0, ("Level up Silcoon", lvl, with_customs_data(target2_data)))
                    update_evo_stuff(data, target2_data, curr_evo_targets)
                case "_Level up stats":
                    target2_data = _get_random_target(curr_evo_targets, data) or target_data
                    target3_data = _get_random_target(curr_evo_targets, data) or target_data
                    lvl = min(value if value != -1 else int(world.random.triangular(
                        curr_max_lvl+1, max_level + 0.9, curr_max_lvl + (max_level - curr_max_lvl + 1) // 4)), max_level)
                    curr_max_lvl = lvl
                    data.evolutions.insert(0, ("Level up equal physical", lvl, with_customs_data(target3_data)))
                    data.evolutions.insert(0, ("Level up higher attack", lvl, with_customs_data(target2_data)))
                    data.evolutions.insert(0, ("Level up higher defense", lvl, with_customs_data(target_data)))
                    update_evo_stuff(data, target2_data, curr_evo_targets)
                    update_evo_stuff(data, target3_data, curr_evo_targets)

            update_evo_stuff(data, target_data, curr_evo_targets)

    for data in all_species.values():
        if not data.form or data.write & 2:
            continue
        base_data = by_id[data.dex_number, 0]
        data.evolutions, data.evo_line = base_data.evolutions.copy(), base_data.evo_line


def fix_curves_stages(by_id: dict[tuple[int, int], SpeciesEntry]):

    if not any(entry.write & 1 for entry in by_id.values()):
        return

    def do_evo_stages(_dat: SpeciesEntry, _stage: int):
        for evo_tup in data.evolutions:
            for evo_data in evo_tup[2]:
                if evo_data.evolution_stage >= _stage:
                    continue
                evo_data.evolution_stage = _stage
                do_evo_stages(evo_data, min(_stage+1, 3))

    for data in by_id.values():
        data.evolution_stage = 0
        if data.write & 0b10000000:
            continue
        if not data.evo_line:  # either single stage, or not randomized but plando on other species
            continue
        all_members = []
        curve_counts = [0] * 8
        for dex in data.evo_line.search().members:
            for i in range(6):
                if (dex, i) not in by_id:
                    break
                member_data = by_id[(dex, i)]
                all_members.append(member_data)
                curve_counts[member_data.exp_curve] += 1
                member_data.write |= 0b10000000
        top_curve = max((curve_counts[i], i) for i in range(8))[1]
        for member_data in all_members:
            member_data.exp_curve = top_curve
    for data in by_id.values():
        if data.evolution_stage or (data.form and not data.is_custom_form):
            continue
        stage = 1 + bool(data.pre_evolutions)
        data.evolution_stage = stage
        do_evo_stages(data, stage+2)
    for data in by_id.values():
        if not data.form or data.is_custom_form:
            continue
        base_data = by_id[data.dex_number, 0]
        data.evolution_stage = base_data.evolution_stage
