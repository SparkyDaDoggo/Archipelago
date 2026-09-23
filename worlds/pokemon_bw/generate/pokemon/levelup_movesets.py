from dataclasses import dataclass
from typing import TYPE_CHECKING
from .. import SpeciesEntry
from ...data import LevelUpMovesetData
from ...generate import MoveEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld


@dataclass
class LvlupSlot:
    level: int
    move: str
    data: MoveEntry | None = None


def sort_by_level(move: tuple[int, str]) -> int:
    return move[0]


def sort_slot_by_level(slot: LvlupSlot) -> int:
    return slot.level


def sort_by_power(move: tuple[str, "MoveEntry"]) -> int:
    return move[1].power


def randomize_levelup_movesets(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry]):
    from ...data.pokemon.moves import by_id as move_by_id

    mods = world.options.randomize_level_up_movesets

    if not mods.is_randomize:
        for species, plando_stat in world.options.stats_plando:
            if plando_stat.levelup_moveset is not False:
                dat = all_species[species]
                new_moves = [(plando_move.level, plando_move.move) for plando_move in plando_stat.levelup_moveset]
                if not plando_stat.override_levelup_moveset:
                    new_moves += dat.level_up_moves.level_up_moves
                new_moves.sort(key=sort_by_level)
                dat.level_up_moves = LevelUpMovesetData(new_moves)
                dat.write |= 0b10000
        return

    for species, dat in all_species.items():
        dat.level_up_moves = LevelUpMovesetData([])
        dat.write |= 0b10000

    plando_append = {}
    for species, plando_stat in world.options.stats_plando:
        if plando_stat.levelup_moveset is not False:
            dat = all_species[species]
            new_moves = [(plando_move.level, plando_move.move) for plando_move in plando_stat.levelup_moveset]
            if plando_stat.override_levelup_moveset:
                dat.level_up_moves = LevelUpMovesetData(new_moves)
            else:
                plando_append[species] = [LvlupSlot(m[0], m[1]) for m in new_moves]

    all_moves = tuple((n, d) for n, d in world.move_entries.items() if not d.locked)
    moves_amount_min = world.options.stats_randomization_adjustments["Levelup moves amount minimum"]
    moves_amount_max = world.options.stats_randomization_adjustments["Levelup moves amount maximum"]

    def roll(data: SpeciesEntry, extra: list[tuple[str, "MoveEntry"]]):
        final_list: list[LvlupSlot] = []
        amount = data.vanilla_moves_count if mods.is_keep_levels_and_amount \
            else world.random.randrange(moves_amount_min, moves_amount_max + 1)
        random_to_distribute = [LvlupSlot(0, "") for _ in range(amount)]

        this_plando = plando_append.get(data.species_name, [])  # Fully required
        evo_moves = []  # Fully required, but any level
        for evo_tup in data.evolutions:
            if evo_tup.method == "Level up with move":
                evo_move_name = move_by_id[evo_tup.value]
                if not this_plando or not any(evo_move_name == t.move for t in this_plando):
                    evo_moves.append(LvlupSlot(0, evo_move_name))
        extra_to_distribute = [LvlupSlot(0, m[0], m[1]) for m in extra
                               if not any(m[0] == t.move for t in this_plando)]  # Not more than rolled amount
        world.random.shuffle(extra_to_distribute)

        # Force plando-append and moves needed for evo
        if this_plando or evo_moves:
            final_list += this_plando + evo_moves
            random_to_distribute = random_to_distribute[:-len(this_plando)-len(evo_moves)]
        # Add pre-evo moves if there is still some room for them, if enabled
        if extra_to_distribute:
            extra_to_distribute = extra_to_distribute[:len(random_to_distribute)]
            final_list += extra_to_distribute
            random_to_distribute = random_to_distribute[:-len(extra_to_distribute)]
        final_list += random_to_distribute

        final_no_level = []
        # Sort all slots without a level out into their own list
        for i in reversed(range(len(final_list))):
            if not final_list[i].level:
                final_no_level.append(final_list.pop(i))
        # Count how many level 1's are needed
        start_count = 4 if mods.is_start_with_4 else 1
        for slot in final_list:
            if slot.level == 1:
                start_count -= 1
                if not start_count:
                    break
        # Bump slot count if there are less level-less slots than needed
        if len(final_no_level) < start_count:
            final_no_level += (LvlupSlot(0, "") for _ in range(start_count - len(final_no_level)))
        # Fill needed level 1 slots
        for _ in range(start_count):
            slot = final_no_level.pop()
            slot.level = 1
            final_list.append(slot)
        # Fill with vanilla levels, if enabled
        if mods.is_keep_levels_and_amount and final_no_level:
            current_levels = set(s.level for s in final_list)  # Only for lookup!
            for lvl in data.vanilla_move_levels:
                if lvl not in current_levels:
                    slot = final_no_level.pop()
                    slot.level = lvl
                    final_list.append(slot)
                    if not final_no_level:
                        break
        # Fill all remaining level-less slots
        for slot in final_no_level:
            slot.level = world.random.randrange(1, 101)
            final_list.append(slot)
        final_list.sort(key=sort_slot_by_level)

        # Fill remaining missing moves randomly
        possible_moves = all_moves if not mods.is_match_types else tuple(
            t for t in all_moves if t[1].type in (*data.types, "Normal")
        )
        for slot in final_list:
            if not slot.move:
                slot.move, slot.data = world.random.choice(possible_moves)
            elif not slot.data:
                slot.data = world.move_entries[slot.move]
        # Redistribute moves for progressive power, if enabled
        if mods.is_progressive_power:
            moves_to_distribute = []
            # Split moves from levels, while keeping plando moves
            for slot in final_list:
                if slot not in this_plando:
                    moves_to_distribute.append((slot.move, slot.data))
                    slot.move, slot.data = "", None
            # Custom sorting algorithm because I want to keep 0 power moves scattered
            current_high = 0
            for i in range(len(moves_to_distribute)):
                power = moves_to_distribute[i][1].power
                if not power:
                    continue
                if power >= current_high:
                    current_high = moves_to_distribute[i][1].power
                else:
                    for j in reversed(range(i)):
                        power2 = moves_to_distribute[j][1].power
                        if power2 and power2 <= power:
                            moves_to_distribute.insert(j+1, moves_to_distribute.pop(i))
                            break
            # Reinsert now-sorted moves
            for slot in final_list:
                if not slot.move:
                    slot.move, slot.data = moves_to_distribute.pop(0)

        data.level_up_moves.level_up_moves.extend([(slot.level, slot.move) for slot in final_list])

        if mods.is_follow_evolutions:
            do_evos(data, [(slot.move, slot.data) for slot in final_list])

    def do_evos(data: SpeciesEntry, extra: list[tuple[str, "MoveEntry"]]):
        for evo_tup in data.evolutions:
            evo_spec = evo_tup.species.by_form(data.form)
            if evo_spec.form and not evo_spec.is_custom_form:
                evo_spec = evo_spec.all_forms[0]
            if not evo_spec.level_up_moves.level_up_moves:
                roll(evo_spec, extra)

    if mods.is_follow_evolutions:
        for spec, dat in all_species.items():
            if not dat.level_up_moves.level_up_moves and (not dat.form or dat.is_custom_form):
                if not dat.pre_evolutions:
                    roll(dat, [])
                else:
                    done_candidates = {dat}  # Only for lookup!
                    base_candidates = list(spec for spec in dat.pre_evolutions if spec != dat)
                    dat2 = dat
                    while base_candidates:
                        dat2 = base_candidates.pop(0)
                        if dat2 in done_candidates:
                            continue
                        if not dat2.pre_evolutions:
                            break
                        done_candidates.add(dat2)
                        base_candidates.extend(spec for spec in dat2.pre_evolutions if spec not in done_candidates)
                    roll(dat2, [])
    else:
        for spec, dat in all_species.items():
            if not dat.level_up_moves.level_up_moves and (not dat.form or dat.is_custom_form):
                roll(dat, [])
