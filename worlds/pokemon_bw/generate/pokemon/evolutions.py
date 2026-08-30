from typing import TYPE_CHECKING, Iterable
from .. import SpeciesEntry, EvoLine, EvolutionsEntry
from ...data.pokemon.evolution_methods import methods

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def would_loop_deep_search(pre: SpeciesEntry, evo: SpeciesEntry) -> bool:
    pre, evo = pre.all_forms[0], evo.all_forms[0]
    searched: set[SpeciesEntry] = set()
    to_do: list[SpeciesEntry] = [evo]
    while to_do:
        evo = to_do.pop(0)
        searched.add(evo)
        for evo_entry in evo.evolutions:
            evo_spec = evo_entry.species
            if evo_spec == pre:
                return True
            if evo_spec not in searched and evo_spec not in to_do:
                to_do.append(evo_spec)
    return False


def cop(obj: Iterable, bad: Iterable) -> tuple:
    return tuple(oo for oo in ((o if isinstance(o, str) else cop(o, bad)) for o in obj if o not in bad) if oo)


def evo_sort_key(x: EvolutionsEntry) -> tuple[int, int]:
    return methods[x.method].priority, -x.value


def methods_sort_key(x: tuple[str, int]) -> int:
    return -x[1]


def replace_evolutions(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]):

    replace = world.options.replace_evo_methods

    # Assumes the evolutions list is already a copy
    if replace.is_locations:
        for poke_name in ("Nosepass", "Magneton"):
            dat = all_species[poke_name]
            dat.write |= 1
            evos = dat.evolutions
            for i in range(len(evos)):
                if evos[i].method == "Magnetic area":
                    evos[i] = EvolutionsEntry("Stone", 83, evos[i].species)
        dat = all_species["Eevee"]
        dat.write |= 1
        evos = dat.evolutions
        for i in range(len(evos)):
            if evos[i].method == "Level up moss rock":
                evos[i] = EvolutionsEntry("Stone", 85, evos[i].species)
            elif evos[i].method == "Level up ice rock":
                evos[i] = EvolutionsEntry("Stone", 107, evos[i].species)
    if replace.is_friendship:
        for poke_name in ("Swadloon", "Golbat"):
            dat = all_species[poke_name]
            dat.write |= 1
            evos = dat.evolutions
            for i in range(len(evos)):
                if evos[i].method == "Friendship":
                    evos[i] = EvolutionsEntry("Level up", 32, evos[i].species)
        for data in all_species.values():
            evos = data.evolutions
            for i in range(len(evos)):
                if evos[i].method == "Friendship":
                    evos[i] = EvolutionsEntry("Level up", 20, evos[i].species)
                    data.write |= 1
    if replace.is_pid:
        for poke_name in ("Kirlia", "Snorunt"):
            dat = all_species[poke_name]
            dat.write |= 1
            evos = dat.evolutions
            for i in range(len(evos)):
                if evos[i].method in ("Stone female", "Stone male"):
                    evos[i] = EvolutionsEntry("Stone", evos[i].value, evos[i].species)
        for poke_name in ("Burmy (Plant)", "Combee"):
            dat = all_species[poke_name]
            dat.write |= 1
            evos = dat.evolutions
            for i in range(len(evos)):
                if evos[i].method == "Level up (female)":
                    evos[i] = EvolutionsEntry("Level up", evos[i].value, evos[i].species)
        dat = all_species["Burmy (Plant)"]
        dat.write |= 1
        evos = dat.evolutions
        for i in range(len(evos)):
            if evos[i].method == "Level up (male)":
                evos[i] = EvolutionsEntry("Level up with party member", 49, evos[i].species)
        dat = all_species["Wurmple"]
        dat.write |= 1
        evos = dat.evolutions
        for i in range(len(evos)):
            if evos[i].method == "Level up Silcoon":
                evos[i] = EvolutionsEntry("Level up with party member", 12, evos[i].species)
            elif evos[i].method == "Level up Cascoon":
                evos[i] = EvolutionsEntry("Level up with party member", 49, evos[i].species)
    if replace.is_stats:
        dat = all_species["Tyrogue"]
        dat.write |= 1
        evos = dat.evolutions
        for i in range(len(evos)):
            if evos[i].method == "Level up higher defense":
                evos[i] = EvolutionsEntry("Level up item day", 0x002F, evos[i].species)
                evos.append(EvolutionsEntry("Level up item night", 0x002F, evos[i].species))
            elif evos[i].method == "Level up higher attack":
                evos[i] = EvolutionsEntry("Level up item day", 0x002E, evos[i].species)
                evos.append(EvolutionsEntry("Level up item night", 0x002E, evos[i].species))
            elif evos[i].method == "Level up equal physical":
                evos[i] = EvolutionsEntry("Level up item day", 0x0030, evos[i].species)
                evos.append(EvolutionsEntry("Level up item night", 0x0030, evos[i].species))


def randomize_evolutions(world: "PokemonBWWorld", by_id: dict[tuple[int, int], SpeciesEntry]):
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
        _target_data.pre_evolutions[_data] = True

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

    def _get_random_target(_curr_targets: set[SpeciesEntry], _dat: SpeciesEntry) -> SpeciesEntry | None:
        picked = world.random.randrange(1, 650) - 1
        end = picked if picked else 649
        while picked != end:
            picked = picked % 649 + 1
            picked_data = by_id[picked, 0]
            if _dat == picked_data:  # no self-evolution for now, assumes _dat is always base form
                continue
            if mods.is_common_type and _dat.types[0] not in picked_data.types and _dat.types[1] not in picked_data.types:
                continue
            if mods.is_follow_type:
                if _dat.evo_line and picked_data.evo_line:
                    if _dat.evo_line.search().type != picked_data.evo_line.search().type:
                        continue
                elif _dat.evo_line:
                    if _dat.evo_line.search().type not in picked_data.types:
                        continue
                elif picked_data.evo_line:
                    if picked_data.evo_line.search().type not in _dat.types:
                        continue
                elif _dat.types[0] not in picked_data.types and _dat.types[1] not in picked_data.types:
                    continue
            if not mods.is_multiple_pre and picked_data.pre_evolutions and _dat not in picked_data.pre_evolutions:
                # **_dat in picked_data.pre_evolutions** can happen to get alternative methods for the same evo species
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

    def _paired_vanilla_method_list(_dat: SpeciesEntry) -> list[tuple[str, int]]:
        method_list: list[tuple[str, int]] = []
        for evo in data.evolutions_copy:
            if evo[0] in ("Level up item night", "Level up Shedinja"):
                continue
            if mods.is_pair_50_50 and evo[0] == "Level up Cascoon":
                continue
            if mods.is_pair_stats and evo[0] in ("Level up higher attack", "Level up equal physical"):
                continue
            if data.gender_ratio in (0, 255):
                if evo[0] == "Level up (female)":
                    evo = ("Level up", evo[1], evo[2])
                if evo[0] == "Stone female":
                    evo = ("Stone", evo[1], evo[2])
            if data.gender_ratio in (254, 255):
                if evo[0] == "Level up (male)":
                    evo = ("Level up with party member", 49, evo[2])
                if evo[0] == "Stone male":
                    evo = ("Stone", evo[1], evo[2])
            method_list.append((resolve_paired(evo[0]), evo[1]))
        return method_list

    def _get_methods_list(_dat: SpeciesEntry) -> list[tuple[str, int]]:
        method_list: list[tuple[str, int]] = []
        method_slots = 0  # Some methods need multiple slots, e.g. Level up item always needing day and night variants
        bad = set()  # only for "in set" comparisons

        if len(_dat.evolutions) == 7:
            return method_list

        if mods.is_every_level:
            method_list = [("Level up", 2)]
            if not mods.is_more_less_branches or not mods.is_random_methods:
                return method_list
            method_slots += 1
            bad += evolution_methods.level_methods

        if _dat.gender_ratio in (254, 255):
            bad += ("Level up (male)", "Stone male")
        if _dat.gender_ratio in (0, 255):
            bad += ("Level up (female)", "Stone female")
        if _dat.evolutions:
            plando_methods = tuple(resolve_paired(evo_entry.method) for evo_entry in _dat.evolutions)
            method_slots += len(_dat.evolutions)
            if any(lvlm in plando_methods for lvlm in evolution_methods.level_methods):
                bad += evolution_methods.level_methods
            for oom in evolution_methods.only_once_methods:
                if oom in plando_methods:
                    bad.add(oom)

        if method_slots == 7:
            return method_list

        if not mods.is_more_less_branches or not mods.is_random_methods:
            from_vanilla = _paired_vanilla_method_list(_dat)
            if mods.is_random_methods:
                branches_already = len(method_list) + len(set(pl for pl in _dat.evolutions if pl.species))
                branches_vanilla = len(tuple(v for v in from_vanilla if v[0] != "Level up item night"))
                if branches_already < branches_vanilla:
                    _rand_methods = cop(random_method, bad)
                    tries = 0
                    while tries < 10 and method_slots < 7 and branches_already < branches_vanilla:
                        picked_method = random_choice_nested(world.random, _rand_methods)
                        picked_slots = evolution_methods.paired_method_slots.get(picked_method, 1)
                        branches_picked = picked_slots if picked_method != "_Level up item" else 1
                        if method_slots + picked_slots > 7 or branches_already + branches_picked > branches_vanilla:
                            tries += 1
                            continue
                        method_list.append((picked_method, -1))
                        method_slots += picked_slots
                        branches_already += branches_picked
                        if not evolution_methods.methods[picked_method].allow_multiple:
                            _rand_methods = cop(_rand_methods, (picked_method, ))
                        break
            else:
                from_vanilla = cop(from_vanilla, bad)
                for vm in from_vanilla:
                    slots = evolution_methods.paired_method_slots.get(vm, 1)
                    if method_slots + slots <= 7:
                        method_list.append(vm)
        else:
            _rand_methods = cop(random_method, bad)
            tries = 0
            while tries < 10 and method_slots < 7 and world.random.random() < 0.75:
                picked_method = random_choice_nested(world.random, _rand_methods)
                picked_slots = evolution_methods.paired_method_slots.get(picked_method, 1)
                if method_slots + picked_slots > 7:
                    tries += 1
                    continue
                method_list.append((picked_method, -1))
                method_slots += picked_slots
                if not evolution_methods.methods[picked_method].allow_multiple:
                    _rand_methods = cop(_rand_methods, (picked_method,))
                break

        method_list.sort(key=methods_sort_key)
        return method_list

    split = world.random.randrange(1, 650)
    for dex_num in (*range(split, 650), *range(1, split)):
        data = by_id[dex_num, 0]  # for evo rando, we will always just copy base to all forms, even custom ones
        if data.write & 2:  # skip those overridden by plando
            continue
        curr_evo_targets = set()  # ONLY LOOKUP
        available_stones = None
        available_items = None
        available_moves = None
        available_member = None
        for method, value in reversed(_get_methods_list(data)):
            target_data = _get_random_target(curr_evo_targets, data)
            if target_data is None:
                break
            match method:
                case c if c in ("Level up", "Level up higher defense", "Level up higher attack",
                                "Level up equal physical", "Level up Silcoon", "Level up Cascoon",
                                "Level up (female)", "Level up (male)"):
                    lvl = min(value if value != -1 else int(world.random.triangular(2, max_level + 0.9, 2)), max_level)
                    data.evolutions.append(EvolutionsEntry(method, lvl, target_data))
                case c if c in ("Stone", "Stone male", "Stone female"):
                    if value != -1:
                        item_id = value
                    else:
                        if available_stones is None:
                            available_stones = list(evolution_methods.stone_items)
                            world.random.shuffle(available_stones)
                        item_id = available_stones.pop()
                    data.evolutions.append(EvolutionsEntry(method, item_id, target_data))
                case c if c in ("Friendship", "Magnetic area", "Level up moss rock", "Level up ice rock"):
                    data.evolutions.append(EvolutionsEntry(method, 0, target_data))
                case "Level up with move":
                    if value != -1:
                        move_id = value
                    else:
                        if available_moves is None:
                            available_moves = list(data.level_up_moves.level_up_moves)
                            world.random.shuffle(available_moves)
                        move_id = world.move_entries[available_moves.pop()[1]].id
                    data.evolutions.append(EvolutionsEntry(method, move_id, target_data))
                case "Level up with party member":
                    if value != -1:
                        wanted_dex = value
                    else:
                        if available_member is None:
                            available_member = list(range(1, 650))
                            world.random.shuffle(available_member)
                        wanted_dex = available_member.pop()
                    data.evolutions.append(EvolutionsEntry(method, wanted_dex, target_data))
                case "_Level up item":
                    if value != -1:
                        item_id = value
                    else:
                        if available_items is None:
                            available_items = list(evolution_methods.hold_items)
                            world.random.shuffle(available_items)
                        item_id = available_items.pop()
                    data.evolutions.append(EvolutionsEntry("Level up item night", item_id, target_data))
                    data.evolutions.append(EvolutionsEntry("Level up item day", item_id, target_data))
                case "_Level up split":
                    target2_data = _get_random_target(curr_evo_targets, data) or target_data
                    lvl = min(value if value != -1 else int(world.random.triangular(2, max_level + 0.9, 2)), max_level)
                    data.evolutions.append(EvolutionsEntry("Level up Shedinja", lvl, target_data))
                    data.evolutions.append(EvolutionsEntry("Level up Ninjask", lvl, target2_data))
                    update_evo_stuff(data, target2_data, curr_evo_targets)
                case "_Level up PID":
                    target2_data = _get_random_target(curr_evo_targets, data) or target_data
                    lvl = min(value if value != -1 else int(world.random.triangular(2, max_level + 0.9, 2)), max_level)
                    data.evolutions.append(EvolutionsEntry("Level up Cascoon", lvl, target_data))
                    data.evolutions.append(EvolutionsEntry("Level up Silcoon", lvl, target2_data))
                    update_evo_stuff(data, target2_data, curr_evo_targets)
                case "_Level up stats":
                    target2_data = _get_random_target(curr_evo_targets, data) or target_data
                    target3_data = _get_random_target(curr_evo_targets, data) or target_data
                    lvl = min(value if value != -1 else int(world.random.triangular(2, max_level + 0.9, 2)), max_level)
                    data.evolutions.append(EvolutionsEntry("Level up equal physical", lvl, target3_data))
                    data.evolutions.append(EvolutionsEntry("Level up higher attack", lvl, target2_data))
                    data.evolutions.append(EvolutionsEntry("Level up higher defense", lvl, target_data))
                    update_evo_stuff(data, target2_data, curr_evo_targets)
                    update_evo_stuff(data, target3_data, curr_evo_targets)
            update_evo_stuff(data, target_data, curr_evo_targets)


def fix_curves_stages_order(by_id: dict[tuple[int, int], SpeciesEntry]):

    if not any(entry.write & 1 for entry in by_id.values()):
        return

    for data in by_id.values():
        # fix evos order
        if not data.form:  # all forms contain a reference to the same evo list
            data.evolutions.sort(key=evo_sort_key)
        # fix virtual forms
        checked: set[SpeciesEntry] = {f for f in data.all_forms if f}
        for form in range(1, min(len(data.all_forms), 6)):
            if data.all_forms[form] is None:
                continue
            to_do: list[SpeciesEntry] = [f for f in data.all_forms if f]
            while to_do:
                current = to_do.pop()
                checked.add(current)
                for evo_entry in current.evolutions:
                    evo_spec = evo_entry.species.by_form(form)
                    if evo_spec not in checked and evo_spec not in to_do:
                        to_do.append(evo_spec)
        # fix exp curves
        data.evolution_stage = 0  # Setting evo_stage to 0 here, because evo_stage loop needs to check for it being set by pre-evo
        if data.write & 0b10000000:  # Already fixed by another evo line member
            continue
        if not data.evo_line:  # either single stage, or not randomized but plando on other species
            continue
        all_members = []
        curve_counts = [0] * 8
        for dex in data.evo_line.search().members:
            member_data = by_id[dex, 0]  # Only use base form, since non-base forms always have the same curve
            all_members.extend(member_data.all_forms)
            curve_counts[member_data.exp_curve] += 1
        top_curve = max((curve_counts[i], i) for i in range(8))[1]
        for member_data in all_members:
            member_data.exp_curve = top_curve
            member_data.write |= 0b10000000
    for data in by_id.values():
        # fix evo stages
        if data.evolution_stage:  # if by_id is sorted by form number, this should also filter forms, which wouldn't be a problem anyway
            continue
        stage = 1 + bool(data.pre_evolutions)
        to_do: list[tuple[SpeciesEntry, int]] = [(data, stage)]
        while to_do:
            data, stage = to_do.pop(0)
            for f in data.all_forms:
                f.evolution_stage = stage
            for evo_entry in data.evolutions:
                evo_data = evo_entry.species
                if evo_data.evolution_stage >= stage:
                    continue
                to_do.append((evo_data, min(stage + 1, 3)))
