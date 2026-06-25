from typing import Callable

from test.bases import WorldTestBase

from . import random_combination
from ..options import RandomizeBaseStats, RandomizeEvolutions, RandomizeCatchRates, RandomizeLevelUpMovesets


def multiply_random_combinations(option: str, mods: tuple, count: int) -> Callable:
    combs = tuple(random_combination(mods) for _ in range(count))

    def decorator(cls: type) -> type:
        def extra(index: int, val: Callable) -> Callable:
            def e(self):
                cls.options = {option: combs[index]}
                val(self)

            return e

        cls.options = {option: random_combination(mods)}
        for name, value in WorldTestBase.__dict__.items():
            name: str
            if isinstance(value, Callable) and name.startswith("test_"):
                for i in range(count):
                    setattr(cls, f"test_{i}_" + name[5:], extra(i, value))
        return cls

    return decorator


class PokemonBWTestBase(WorldTestBase):
    game = "Pokemon Black and White"


stats_mods = tuple(RandomizeBaseStats.valid_keys)
evolution_mods = tuple(RandomizeEvolutions.valid_keys)
catch_rate_mods = tuple(RandomizeCatchRates.valid_keys)
levelup_moves_mods = tuple(RandomizeLevelUpMovesets.valid_keys)


class TestRandomizeBaseStatsSimple(PokemonBWTestBase):
    options = {"randomize_base_stats": ["Randomize"]}


@multiply_random_combinations("randomize_base_stats", stats_mods, 4)
class TestRandomizeBaseStats(PokemonBWTestBase):
    # options = {"randomize_base_stats": random_combination(stats_mods)}
    def setUp(self) -> None:
        print("Modifiers: "+", ".join(self.options["randomize_base_stats"]))
        super().setUp()


class TestRandomizeEvolutionsSimple(PokemonBWTestBase):
    options = {"randomize_evolutions": ["Randomize"]}


@multiply_random_combinations("randomize_evolutions", evolution_mods, 10)
class TestRandomizeEvolutions(PokemonBWTestBase):
    # options = {"randomize_evolutions": random_combination(evolution_mods)}
    def setUp(self) -> None:
        print("Modifiers: "+", ".join(self.options["randomize_evolutions"]))
        super().setUp()


class TestRandomizeCatchRatesSimple(PokemonBWTestBase):
    options = {"randomize_catch_rates": ["Shuffle"]}


@multiply_random_combinations("randomize_catch_rates", catch_rate_mods, 4)
class TestRandomizeCatchRates(PokemonBWTestBase):
    # options = {"randomize_catch_rates": random_combination(catch_rate_mods)}
    def setUp(self) -> None:
        print("Modifiers: "+", ".join(self.options["randomize_catch_rates"]))
        super().setUp()


class TestRandomizeLevelupMovesSimple(PokemonBWTestBase):
    options = {"randomize_level_up_movesets": ["Randomize"]}


@multiply_random_combinations("randomize_level_up_movesets", levelup_moves_mods, 10)
class TestRandomizeLevelupMoves(PokemonBWTestBase):
    # options = {"randomize_level_up_movesets": random_combination(levelup_moves_mods)}
    def setUp(self) -> None:
        print("Modifiers: "+", ".join(self.options["randomize_level_up_movesets"]))
        super().setUp()
