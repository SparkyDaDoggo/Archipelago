from . import multiply_random_combinations, PokemonBWTestBase
from ..options import (RandomizeBaseStats, RandomizeEvolutions, RandomizeCatchRates, RandomizeLevelUpMovesets,
                       RandomizeTypes, RandomizeTMHMCompatibility, RandomizeEggGroups, RandomizeEggSpecies)


class TestRandomizeBaseStatsSimple(PokemonBWTestBase):
    options = {"randomize_base_stats": ["Randomize"]}
@multiply_random_combinations("randomize_base_stats", tuple(RandomizeBaseStats.valid_keys), 3)
class TestRandomizeBaseStats(PokemonBWTestBase):
    pass


class TestRandomizeEvolutionsSimple(PokemonBWTestBase):
    options = {"randomize_evolutions": ["Randomize"]}
@multiply_random_combinations("randomize_evolutions", tuple(RandomizeEvolutions.valid_keys), 11)
class TestRandomizeEvolutions(PokemonBWTestBase):
    pass


class TestRandomizeCatchRatesSimple(PokemonBWTestBase):
    options = {"randomize_catch_rates": ["Shuffle"]}
@multiply_random_combinations("randomize_catch_rates", tuple(RandomizeCatchRates.valid_keys), 4)
class TestRandomizeCatchRates(PokemonBWTestBase):
    pass


class TestRandomizeLevelupMovesSimple(PokemonBWTestBase):
    options = {"randomize_level_up_movesets": ["Randomize"]}
@multiply_random_combinations("randomize_level_up_movesets", tuple(RandomizeLevelUpMovesets.valid_keys), 7)
class TestRandomizeLevelupMoves(PokemonBWTestBase):
    pass


class TestRandomizeTypesSimple(PokemonBWTestBase):
    options = {"randomize_types": ["Randomize"]}
@multiply_random_combinations("randomize_types", tuple(RandomizeTypes.valid_keys), 7)
class TestRandomizeTypes(PokemonBWTestBase):
    pass


class TestRandomizeTMHMCompatSimple(PokemonBWTestBase):
    options = {"randomize_tm_hm_compatibility": ["Randomize"]}
@multiply_random_combinations("randomize_tm_hm_compatibility", tuple(RandomizeTMHMCompatibility.valid_keys), 5)
class TestRandomizeTMHMCompat(PokemonBWTestBase):
    pass


class TestRandomizeEggGroupsSimple(PokemonBWTestBase):
    options = {"randomize_egg_groups": ["Randomize"]}
@multiply_random_combinations("randomize_egg_groups", tuple(RandomizeEggGroups.valid_keys), 7)
class TestRandomizeEggGroups(PokemonBWTestBase):
    pass


class TestRandomizeEggSpeciesSimple(PokemonBWTestBase):
    options = {"randomize_egg_species": ["Randomize"]}
@multiply_random_combinations("randomize_egg_species", tuple(RandomizeEggSpecies.valid_keys), 5)
class TestRandomizeEggSpecies(PokemonBWTestBase):
    pass


class TestStatsPlandoBaseStatsCatchRate(PokemonBWTestBase):
    options = {"stats_plando": {
        "Bulbasaur": {"base_hp": 120,
                      "base_attack": 10,
                      "base_sp_defense": 200,
                      "catch_rate": 220},
        "Squirtle": {"base_defense": 120,
                     "base_sp_attack": 10,
                     "base_speed": 200},
    }}
class TestStatsPlandoEvoLevelupMoveVanilla(PokemonBWTestBase):
    options = {"stats_plando": {
        "Bulbasaur": {"evolutions": [{"species": "Weedle"},
                                     {"species": "Caterpie", "method": "Stone", "stone": "Water Stone"}],
                      "override_evolutions": True,
                      "levelup_moveset": [{"move": "Pound", "level": 1},
                                          {"move": "Earthquake", "level": 100}],
                      "override_levelup_moveset": True},
        "Squirtle": {"evolutions": [{"species": "Weedle", "level": 5},
                                    {"species": "Caterpie", "method": "Stone", "stone": "Water Stone"}],
                     "override_evolutions": False,
                     "levelup_moveset": [{"move": "Pound", "level": 10},
                                         {"move": "Earthquake", "level": 100}],
                     "override_levelup_moveset": False},
    }}
class TestStatsPlandoEvoLevelupMoveRandomized(PokemonBWTestBase):
    options = {"stats_plando": {
        "Bulbasaur": {"evolutions": [{"species": "Weedle"},
                                     {"species": "Caterpie", "method": "Stone", "stone": "Water Stone"}],
                      "override_evolutions": True,
                      "levelup_moveset": [{"move": "Pound", "level": 1},
                                          {"move": "Earthquake", "level": 100}],
                      "override_levelup_moveset": True},
        "Squirtle": {"evolutions": [{"species": "Weedle", "level": 5},
                                    {"species": "Caterpie", "method": "Stone", "stone": "Water Stone"}],
                     "override_evolutions": False,
                     "levelup_moveset": [{"move": "Pound", "level": 10},
                                         {"move": "Earthquake", "level": 100}],
                     "override_levelup_moveset": False},
    }, "randomize_evolutions": ["Randomize"], "randomize_level_up_movesets": ["Randomize"]}
