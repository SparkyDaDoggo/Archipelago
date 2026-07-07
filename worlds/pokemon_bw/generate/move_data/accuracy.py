from typing import TYPE_CHECKING
from .. import MoveEntry
from ...options.moves import PlandoMoveData

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def randomize_accuracy(world: "PokemonBWWorld", all_moves: dict[str, MoveEntry]):

    mods = world.options.randomize_move_data
    min_acc: int = world.options.move_data_randomization_adjustments["Accuracy minimum"]
    max_acc: int = world.options.move_data_randomization_adjustments["Accuracy maximum"]

    for name, plando in world.options.move_data_plando:
        if isinstance(plando, PlandoMoveData):
            plando: PlandoMoveData
            if plando.accuracy:
                data = all_moves[name]
                data.accuracy = plando.accuracy
                data.write |= 1

    if not mods.is_randomize_accuracy and not mods.is_shuffle_accuracy:
        return

    possible = tuple(range(min_acc, max_acc + 1)) if mods.is_randomize_accuracy else tuple(r for r in (
        50, 60, 70, 80, 90, 95, 100) if min_acc <= r <= max_acc)  # sorting is important!
    if not possible:
        possible = (min_acc, max_acc)

    for data in all_moves.values():
        if data.accuracy == 101:
            continue
        data.write |= 1
        chosen = world.random.randrange(len(possible))
        if not (mods.is_shuffle_power or mods.is_randomize_power) and mods.is_correlate_power_and_accuracy:
            power_cor = (min(data.power, 150) - 5) / 145
            acc_cor = 1 - (max(possible[chosen], 50) - 50) / 50
            if not power_cor - 0.2 <= acc_cor <= power_cor + 0.2:
                if acc_cor < power_cor:
                    chosen = world.random.randrange(chosen + 1)
                else:
                    chosen = world.random.randrange(chosen, len(possible))
        if mods.is_correlate_pp_and_accuracy:
            acc_cor = 1 - (max(data.accuracy, 50) - 50) / 50
            pp_cor = (min(max(possible[chosen], 5), 40) - 5) / 35
            if not pp_cor - 0.2 <= acc_cor <= pp_cor + 0.2:
                if acc_cor < pp_cor:
                    chosen = world.random.randrange(chosen + 1)
                else:
                    chosen = world.random.randrange(chosen, len(possible))
        data.accuracy = possible[chosen]
