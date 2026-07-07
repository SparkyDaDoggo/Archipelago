from typing import TYPE_CHECKING
from .. import MoveEntry
from ...options.moves import PlandoMoveData

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def randomize_pp(world: "PokemonBWWorld", all_moves: dict[str, MoveEntry]):

    mods = world.options.randomize_move_data
    min_count: int = world.options.move_data_randomization_adjustments["PP minimum"]
    max_count: int = world.options.move_data_randomization_adjustments["PP maximum"]

    for name, plando in world.options.move_data_plando:
        if isinstance(plando, PlandoMoveData):
            plando: PlandoMoveData
            if plando.pp:
                data = all_moves[name]
                data.pp = plando.pp
                data.write |= 1

    if not mods.is_randomize_pp and not mods.is_shuffle_pp:
        return

    possible = tuple(range(min_count, max_count + 1)) if mods.is_randomize_pp else tuple(r for r in (
        5, 10, 15, 20, 25, 30, 35, 40) if min_count <= r <= max_count)  # sorting is important!
    if not possible:
        possible = (min_count, max_count)

    for data in all_moves.values():
        data.write |= 1
        chosen = world.random.randrange(len(possible))
        if not (mods.is_shuffle_power or mods.is_randomize_power) and mods.is_correlate_power_and_pp:
            power_cor = (min(data.power, 150) - 5) / 145
            pp_cor = 1 - (min(max(possible[chosen], 5), 40) - 5) / 35
            if not power_cor - 0.2 <= pp_cor <= power_cor + 0.2:
                if pp_cor < power_cor:
                    chosen = world.random.randrange(chosen + 1)
                else:
                    chosen = world.random.randrange(chosen, len(possible))
        if not (mods.is_shuffle_accuracy or mods.is_randomize_accuracy) and mods.is_correlate_pp_and_accuracy:
            acc_cor = (max(data.accuracy, 50) - 50) / 50
            pp_cor = 1 - (min(max(possible[chosen], 5), 40) - 5) / 35
            if not acc_cor - 0.2 <= pp_cor <= acc_cor + 0.2:
                if pp_cor < acc_cor:
                    chosen = world.random.randrange(chosen + 1)
                else:
                    chosen = world.random.randrange(chosen, len(possible))
        data.pp = possible[chosen]
