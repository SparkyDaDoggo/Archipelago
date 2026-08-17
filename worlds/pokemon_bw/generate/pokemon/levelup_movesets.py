from typing import TYPE_CHECKING
from .. import SpeciesEntry
from ...data import LevelUpMovesetData

if TYPE_CHECKING:
    from ... import PokemonBWWorld
    from ...generate import MoveEntry


def sort_by_level(move: tuple[int, str]) -> int:
    return move[0]


def sort_by_power(move: tuple[str, "MoveEntry"]) -> int:
    return move[1].power


def randomize_levelup_movesets(world: "PokemonBWWorld", all_species: dict[str, SpeciesEntry],
                               by_id: dict[tuple[int, int], SpeciesEntry]):
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
                plando_append[species] = new_moves

    all_moves = tuple((n, d) for n, d in world.move_entries.items())
    moves_amount_min = world.options.stats_randomization_adjustments["Levelup moves amount minimum"]
    moves_amount_max = world.options.stats_randomization_adjustments["Levelup moves amount maximum"]

    def roll(data: SpeciesEntry, extra: list[tuple[str, "MoveEntry"]]):
        this_plando = plando_append.get(data.species_name, [])
        if mods.is_keep_amount:
            amount = data.vanilla_moves_count
        else:
            amount = world.random.randint(moves_amount_min, moves_amount_max)
            if extra:
                if not this_plando:
                    amount = min(moves_amount_max, max(amount, len(extra)))
                else:
                    moves_in_plando = tuple(t[1] for t in this_plando)
                    crossed = len(tuple(1 for t in extra if t[0] not in moves_in_plando)) + len(moves_in_plando)
                    amount = min(moves_amount_max, max(crossed, amount))
        if this_plando:
            amount = max(amount, len(this_plando))
        if mods.is_start_with_4 and amount < 4:
            amount = 4
        if this_plando and len(this_plando) == amount and all(t[0] > 1 for t in this_plando):
            amount += 1
        evo_moves = []
        for evo_tup in data.evolutions:
            if evo_tup[0] == "Level up with move":
                evo_move_name = move_by_id[evo_tup[1]]
                if not this_plando or not any(evo_move_name == t[1] for t in this_plando):
                    evo_moves.append(evo_move_name)
        if this_plando and len(this_plando) + len(evo_moves) > amount:
            amount = len(this_plando) + len(evo_moves)

        possible_random = all_moves if not mods.is_keep_types else tuple(
            t for t in all_moves if t[1].type in (*data.types, "Normal")
        )
        chosen_moves, plandod_moves = [(n, world.move_entries[n]) for n in evo_moves], []
        if this_plando:
            plandod_moves += ((t[1], world.move_entries[t[1]]) for t in this_plando)
        if len(plandod_moves) < amount:
            extra_moves = extra[-(amount-len(plandod_moves)-len(chosen_moves)):]
            for evo_move in chosen_moves:
                extra_moves.insert(world.random.randint(0, len(extra_moves)), evo_move)
            chosen_moves = extra_moves
        for i in range(amount - len(plandod_moves) - len(chosen_moves)):
            chosen_moves.insert(world.random.randint(0, len(chosen_moves)), world.random.choice(possible_random))
        if mods.is_progressive_power:
            chosen_0_power_moves = tuple(t for t in chosen_moves if not t[1].power)
            chosen_moves = [t for t in chosen_moves if t[1].power]
            chosen_moves.sort(key=sort_by_power)
            for move_tup in chosen_0_power_moves:
                chosen_moves.insert(world.random.randint(0, len(chosen_moves)), move_tup)

        plandod_levels = [t[0] for t in this_plando]
        chosen_levels = world.random.choices(tuple(range(1, 101)), k=amount-len(plandod_moves))
        chosen_levels.sort()
        plando_1s = len(tuple(1 for i in plandod_levels if i == 1))
        if not plando_1s:
            chosen_levels[0] = 1
        if mods.is_start_with_4:
            chosen_levels[:4-min(4, plando_1s)] = (1, ) * (4 - plando_1s)

        data.level_up_moves.level_up_moves.extend([(chosen_levels[i], chosen_moves[i][0])
                                                   for i in range(amount-len(plandod_moves))] + this_plando)

        if not this_plando:
            data.level_up_moves.level_up_moves.sort(key=sort_by_level)
        if mods.is_follow_evolutions:
            do_evos(data, chosen_moves if not this_plando else [(t[1], world.move_entries[t[1]]) for t in
                                                                data.level_up_moves.level_up_moves])

    def do_evos(data: SpeciesEntry, extra: list[tuple[str, "MoveEntry"]]):
        for evo_tup in data.evolutions:
            for evo_dat in evo_tup[2]:
                if not evo_dat.level_up_moves.level_up_moves:
                    roll(evo_dat, extra)

    for spec, dat in all_species.items():
        if not dat.level_up_moves.level_up_moves and (not dat.form or dat.is_custom_form):
            roll(dat, [])
    for spec, dat in all_species.items():
        if dat.form and not dat.is_custom_form:
            base_data = by_id[dat.dex_number, 0]
            dat.level_up_moves = base_data.level_up_moves
