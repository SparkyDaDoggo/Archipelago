from . import multiply_random_combinations, PokemonBWTestBase, requires_modifier
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

    @requires_modifier("Keep levels and amount", "randomize_level_up_movesets")
    def mod_keep_levels_amount(self):
        from ..data.pokemon.movesets_level_up import table

        correct_amounts = 0
        correct_levels = 0
        last_bad: tuple = None, None
        for name, data in self.world.catchable_species_data.items():
            if len(data.level_up_moves.level_up_moves) == len(table[name].level_up_moves):
                correct_amounts += 1
            else:
                last_bad = name, data
            levels = set(slot[0] for slot in table[name].level_up_moves)
            for slot in data.level_up_moves.level_up_moves:
                if slot[0] not in levels:
                    last_bad = name, data
                    break
            else:
                correct_levels += 1
        c_amount = correct_amounts / len(table)
        c_levels = correct_levels / len(table)
        if c_amount >= 0.9 <= c_levels:
            print(f"Keep levels and amount modifier passed with "
                  f"{c_amount * 100}% correct move counts and {c_levels * 100}% correct levels")
        else:
            self.fail(f"Keep levels and amount modifier failed with "
                      f"{c_amount * 100}% correct move counts and {c_levels * 100}% correct levels.\n"
                      f"Last bad species:\n"
                      f"Original moveset: {table[last_bad[0]].level_up_moves}\n"
                      f"Randomized moveset: {last_bad[1].level_up_moves.level_up_moves}")


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
