from test.bases import WorldTestBase

from . import random_combination
from ..options import RandomizeBaseStats, RandomizeEvolutions, RandomizeCatchRates, RandomizeLevelUpMovesets


class PokemonBWTestBase(WorldTestBase):
    game = "Pokemon Black and White"


stats_mods = tuple(RandomizeBaseStats.valid_keys)
evolution_mods = tuple(RandomizeEvolutions.valid_keys)
catch_rate_mods = tuple(RandomizeCatchRates.valid_keys)
levelup_moves_mods = tuple(RandomizeLevelUpMovesets.valid_keys)


class TestRandomizeBaseStatsSimple(PokemonBWTestBase):
    options = {"randomize_base_stats": ["Randomize"]}
class TestRandomizeBaseStats(PokemonBWTestBase):
    options = {"randomize_base_stats": random_combination(stats_mods)}
    def setUp(self) -> None:
        print("Modifiers: "+", ".join(self.options["randomize_base_stats"]))
        super().setUp()


class TestRandomizeEvolutionsSimple(PokemonBWTestBase):
    options = {"randomize_evolutions": ["Randomize"]}
class TestRandomizeEvolutions(PokemonBWTestBase):
    options = {"randomize_evolutions": random_combination(evolution_mods)}
    def setUp(self) -> None:
        print("Modifiers: "+", ".join(self.options["randomize_evolutions"]))
        super().setUp()


class TestRandomizeCatchRatesSimple(PokemonBWTestBase):
    options = {"randomize_catch_rates": ["Shuffle"]}
class TestRandomizeCatchRates(PokemonBWTestBase):
    options = {"randomize_catch_rates": random_combination(catch_rate_mods)}
    def setUp(self) -> None:
        print("Modifiers: "+", ".join(self.options["randomize_catch_rates"]))
        super().setUp()


class TestRandomizeLevelupMovesSimple(PokemonBWTestBase):
    options = {"randomize_level_up_movesets": ["Randomize"]}
class TestRandomizeLevelupMoves(PokemonBWTestBase):
    options = {"randomize_level_up_movesets": random_combination(levelup_moves_mods)}
    def setUp(self) -> None:
        print("Modifiers: "+", ".join(self.options["randomize_level_up_movesets"]))
        super().setUp()


class TestRandomizeBaseStats1(TestRandomizeBaseStats):
    options = {"randomize_base_stats": random_combination(stats_mods)}
class TestRandomizeBaseStats2(TestRandomizeBaseStats):
    options = {"randomize_base_stats": random_combination(stats_mods)}
class TestRandomizeBaseStats3(TestRandomizeBaseStats):
    options = {"randomize_base_stats": random_combination(stats_mods)}
class TestRandomizeBaseStats4(TestRandomizeBaseStats):
    options = {"randomize_base_stats": random_combination(stats_mods)}
class TestRandomizeBaseStats5(TestRandomizeBaseStats):
    options = {"randomize_base_stats": random_combination(stats_mods)}
class TestRandomizeBaseStats6(TestRandomizeBaseStats):
    options = {"randomize_base_stats": random_combination(stats_mods)}
class TestRandomizeBaseStats7(TestRandomizeBaseStats):
    options = {"randomize_base_stats": random_combination(stats_mods)}
class TestRandomizeBaseStats8(TestRandomizeBaseStats):
    options = {"randomize_base_stats": random_combination(stats_mods)}
class TestRandomizeBaseStats9(TestRandomizeBaseStats):
    options = {"randomize_base_stats": random_combination(stats_mods)}
class TestRandomizeBaseStats10(TestRandomizeBaseStats):
    options = {"randomize_base_stats": random_combination(stats_mods)}


class TestRandomizeEvolutions1(TestRandomizeEvolutions):
    options = {"randomize_evolutions": random_combination(evolution_mods)}
class TestRandomizeEvolutions2(TestRandomizeEvolutions):
    options = {"randomize_evolutions": random_combination(evolution_mods)}
class TestRandomizeEvolutions3(TestRandomizeEvolutions):
    options = {"randomize_evolutions": random_combination(evolution_mods)}
class TestRandomizeEvolutions4(TestRandomizeEvolutions):
    options = {"randomize_evolutions": random_combination(evolution_mods)}
class TestRandomizeEvolutions5(TestRandomizeEvolutions):
    options = {"randomize_evolutions": random_combination(evolution_mods)}
class TestRandomizeEvolutions6(TestRandomizeEvolutions):
    options = {"randomize_evolutions": random_combination(evolution_mods)}
class TestRandomizeEvolutions7(TestRandomizeEvolutions):
    options = {"randomize_evolutions": random_combination(evolution_mods)}
class TestRandomizeEvolutions8(TestRandomizeEvolutions):
    options = {"randomize_evolutions": random_combination(evolution_mods)}
class TestRandomizeEvolutions9(TestRandomizeEvolutions):
    options = {"randomize_evolutions": random_combination(evolution_mods)}
class TestRandomizeEvolutions10(TestRandomizeEvolutions):
    options = {"randomize_evolutions": random_combination(evolution_mods)}


class TestRandomizeCatchRates1(TestRandomizeCatchRates):
    options = {"randomize_catch_rates": random_combination(catch_rate_mods)}
class TestRandomizeCatchRates2(TestRandomizeCatchRates):
    options = {"randomize_catch_rates": random_combination(catch_rate_mods)}
class TestRandomizeCatchRates3(TestRandomizeCatchRates):
    options = {"randomize_catch_rates": random_combination(catch_rate_mods)}
class TestRandomizeCatchRates4(TestRandomizeCatchRates):
    options = {"randomize_catch_rates": random_combination(catch_rate_mods)}
class TestRandomizeCatchRates5(TestRandomizeCatchRates):
    options = {"randomize_catch_rates": random_combination(catch_rate_mods)}
class TestRandomizeCatchRates6(TestRandomizeCatchRates):
    options = {"randomize_catch_rates": random_combination(catch_rate_mods)}
class TestRandomizeCatchRates7(TestRandomizeCatchRates):
    options = {"randomize_catch_rates": random_combination(catch_rate_mods)}
class TestRandomizeCatchRates8(TestRandomizeCatchRates):
    options = {"randomize_catch_rates": random_combination(catch_rate_mods)}
class TestRandomizeCatchRates9(TestRandomizeCatchRates):
    options = {"randomize_catch_rates": random_combination(catch_rate_mods)}
class TestRandomizeCatchRates10(TestRandomizeCatchRates):
    options = {"randomize_catch_rates": random_combination(catch_rate_mods)}


class TestRandomizeLevelupMoves1(TestRandomizeLevelupMoves):
    options = {"randomize_level_up_movesets": random_combination(levelup_moves_mods)}
class TestRandomizeLevelupMoves2(TestRandomizeLevelupMoves):
    options = {"randomize_level_up_movesets": random_combination(levelup_moves_mods)}
class TestRandomizeLevelupMoves3(TestRandomizeLevelupMoves):
    options = {"randomize_level_up_movesets": random_combination(levelup_moves_mods)}
class TestRandomizeLevelupMoves4(TestRandomizeLevelupMoves):
    options = {"randomize_level_up_movesets": random_combination(levelup_moves_mods)}
class TestRandomizeLevelupMoves5(TestRandomizeLevelupMoves):
    options = {"randomize_level_up_movesets": random_combination(levelup_moves_mods)}
class TestRandomizeLevelupMoves6(TestRandomizeLevelupMoves):
    options = {"randomize_level_up_movesets": random_combination(levelup_moves_mods)}
class TestRandomizeLevelupMoves7(TestRandomizeLevelupMoves):
    options = {"randomize_level_up_movesets": random_combination(levelup_moves_mods)}
class TestRandomizeLevelupMoves8(TestRandomizeLevelupMoves):
    options = {"randomize_level_up_movesets": random_combination(levelup_moves_mods)}
class TestRandomizeLevelupMoves9(TestRandomizeLevelupMoves):
    options = {"randomize_level_up_movesets": random_combination(levelup_moves_mods)}
class TestRandomizeLevelupMoves10(TestRandomizeLevelupMoves):
    options = {"randomize_level_up_movesets": random_combination(levelup_moves_mods)}
