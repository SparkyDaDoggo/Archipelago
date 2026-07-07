from typing import TYPE_CHECKING

from .. import MoveEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def generate_move_data(world: "PokemonBWWorld") -> tuple[dict[str, MoveEntry], dict[tuple[str, str], int]]:
    from ...data.pokemon.moves import by_name
    from .pp import randomize_pp
    from .accuracy import randomize_accuracy
    from .power import randomize_power
    from .type import randomize_type
    from .category import randomize_category
    from .type_chart import randomize_type_chart

    all_moves = {name: MoveEntry(name, data) for name, data in by_name.items()}

    randomize_pp(world, all_moves)
    randomize_accuracy(world, all_moves)
    randomize_power(world, all_moves)
    randomize_type(world, all_moves)
    randomize_category(world, all_moves)
    # randomize_name(world, all_moves)

    chart = randomize_type_chart(world)

    return all_moves, chart
