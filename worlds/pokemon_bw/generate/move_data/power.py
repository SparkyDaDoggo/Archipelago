from typing import TYPE_CHECKING
from .. import MoveEntry
from ...options.moves import PlandoMoveData

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def randomize_power(world: "PokemonBWWorld", all_moves: dict[str, MoveEntry]):

    mods = world.options.randomize_move_data
    min_acc: int = world.options.move_data_randomization_adjustments["Move power minimum"]
    max_acc: int = world.options.move_data_randomization_adjustments["Move power maximum"]

    for name, plando in world.options.move_data_plando:
        if isinstance(plando, PlandoMoveData):
            plando: PlandoMoveData
            if plando.power:
                data = all_moves[name]
                data.power = plando.power
                data.write |= 1

    if not mods.is_randomize_power and not mods.is_shuffle_power:
        return

    possible = tuple(range(min_acc, max_acc + 1)) if mods.is_randomize_power else tuple(r for r in (
        15, 20, 25, 30, 35, 40, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95,
        100, 110, 120, 130, 140, 150) if min_acc <= r <= max_acc)  # sorting is important!
    if not possible:
        possible = (min_acc, max_acc)

    for data in all_moves.values():
        if data.power in (0, 1):
            continue
        data.write |= 1
        chosen = world.random.randrange(len(possible))
        if mods.is_correlate_power_and_accuracy:
            acc_cor = (max(possible[chosen], 50) - 50) / 50
            power_cor = 1 - (min(data.power, 150) - 5) / 145
            if not acc_cor - 0.2 <= power_cor <= acc_cor + 0.2:
                if power_cor < acc_cor:
                    chosen = world.random.randrange(chosen + 1)
                else:
                    chosen = world.random.randrange(chosen, len(possible))
        if mods.is_correlate_power_and_pp:
            pp_cor = (min(max(possible[chosen], 5), 40) - 5) / 35
            power_cor = 1 - (min(data.power, 150) - 5) / 145
            if not pp_cor - 0.2 <= power_cor <= pp_cor + 0.2:
                if power_cor < pp_cor:
                    chosen = world.random.randrange(chosen + 1)
                else:
                    chosen = world.random.randrange(chosen, len(possible))
        data.power = possible[chosen]
