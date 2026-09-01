from . import PokemonBWTestBase, multiply_random_combinations
from ..options import (RandomizeMoveData, RandomizeTypeChart)


@multiply_random_combinations("randomize_move_data", tuple(RandomizeMoveData.valid_keys), 11)
class TestRandomizeMoveData(PokemonBWTestBase):
    pass


class TestRandomizeTypeChartSimpleShuffle(PokemonBWTestBase):
    options = {"randomize_type_chart": ["Shuffle"]}
class TestRandomizeTypeChartSimpleRandomize(PokemonBWTestBase):
    options = {"randomize_type_chart": ["Randomize"]}
@multiply_random_combinations("randomize_type_chart", tuple(RandomizeTypeChart.valid_keys), 5)
class TestRandomizeTypeChart(PokemonBWTestBase):
    pass


class TestMoveDataPlandoVanilla(PokemonBWTestBase):
    options = {"move_data_plando": {
        "Tackle": {
            "power": 120,
            "type": "Dragon",
            "accuracy": 30,
            "category": "Special",
            "pp": 250,
        },
        "ThunderShock": {
            "power": 5,
            "pp": 1,
        },
        "Normal_Ice": {"effectiveness": 4},
        "Psychic_Bug": {"effectiveness": 0},
    }}


class TestMoveDataPlandoRando(PokemonBWTestBase):
    options = {
        "move_data_plando": {
            "Tackle": {
                "power": 120,
                "type": "Dragon",
                "accuracy": 30,
                "category": "Special",
                "pp": 250,
            },
            "ThunderShock": {
                "power": 5,
                "pp": 1,
            },
            "Normal_Ice": {"effectiveness": 4},
            "Psychic_Bug": {"effectiveness": 0},
        },
        "randomize_move_data": [
            "Randomize power",
            "Randomize type",
            "Randomize accuracy",
            "Randomize category",
            "Randomize pp"
        ],
        "randomize_type_chart": ["Randomize"],
    }
