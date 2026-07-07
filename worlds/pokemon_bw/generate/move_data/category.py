from typing import TYPE_CHECKING
from .. import MoveEntry
from ...options.moves import PlandoMoveData

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def randomize_category(world: "PokemonBWWorld", all_moves: dict[str, MoveEntry]):

    mods = world.options.randomize_move_data

    for name, plando in world.options.move_data_plando:
        if isinstance(plando, PlandoMoveData):
            plando: PlandoMoveData
            if plando.category:
                data = all_moves[name]
                data.category = plando.category
                data.write |= 1

    if not mods.is_randomize_category:
        return

    for data in all_moves.values():
        if data.category != "Status":
            data.write |= 1
            data.category = world.random.choice(("Physical", "Special"))
