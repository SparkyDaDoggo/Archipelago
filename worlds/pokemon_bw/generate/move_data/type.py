from typing import TYPE_CHECKING
from .. import MoveEntry
from ...options.moves import PlandoMoveData

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def randomize_type(world: "PokemonBWWorld", all_moves: dict[str, MoveEntry]):
    from ...data.pokemon.types import by_name

    mods = world.options.randomize_move_data
    normal_chance: int = world.options.move_data_randomization_adjustments["Normal type probability"]

    for name, plando in world.options.move_data_plando:
        if isinstance(plando, PlandoMoveData):
            plando: PlandoMoveData
            if plando.type:
                data = all_moves[name]
                data.type = plando.type
                data.write |= 1

    if not mods.is_randomize_type:
        return

    other_types = tuple(t for t in by_name if t != "Normal")

    for data in all_moves.values():
        data.write |= 1
        if world.random.randrange(100) < normal_chance:
            data.type = "Normal"
        else:
            data.type = world.random.choice(other_types)
