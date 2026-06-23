from test.bases import WorldTestBase

from . import random_combination
from ..options import RandomizeWildPokemon, RandomizeTrainerPokemon


class PokemonBWTestBase(WorldTestBase):
    game = "Pokemon Black and White"


wild_mods = tuple(RandomizeWildPokemon.valid_keys)
trainer_mods = tuple(RandomizeTrainerPokemon.valid_keys)


class TestRandomizeWildPokemonSimple(PokemonBWTestBase):
    options = {"randomize_wild_pokemon": ["Randomize"]}
class TestRandomizeWildPokemon(PokemonBWTestBase):
    options = {"randomize_wild_pokemon": random_combination(wild_mods)}
    def setUp(self) -> None:
        print("Modifiers: "+", ".join(self.options["randomize_wild_pokemon"]))
        super().setUp()


class TestRandomizeTrainerPokemonSimple(PokemonBWTestBase):
    options = {"randomize_trainer_pokemon": ["Randomize"]}
class TestRandomizeTrainerPokemon(PokemonBWTestBase):
    options = {"randomize_trainer_pokemon": random_combination(trainer_mods)}
    def setUp(self) -> None:
        print("Modifiers: "+", ".join(self.options["randomize_trainer_pokemon"]))
        super().setUp()


class TestRandomizeWildPokemon1(TestRandomizeWildPokemon):
    options = {"randomize_wild_pokemon": random_combination(wild_mods)}
class TestRandomizeWildPokemon2(TestRandomizeWildPokemon):
    options = {"randomize_wild_pokemon": random_combination(wild_mods)}
class TestRandomizeWildPokemon3(TestRandomizeWildPokemon):
    options = {"randomize_wild_pokemon": random_combination(wild_mods)}
class TestRandomizeWildPokemon4(TestRandomizeWildPokemon):
    options = {"randomize_wild_pokemon": random_combination(wild_mods)}
class TestRandomizeWildPokemon5(TestRandomizeWildPokemon):
    options = {"randomize_wild_pokemon": random_combination(wild_mods)}
class TestRandomizeWildPokemon6(TestRandomizeWildPokemon):
    options = {"randomize_wild_pokemon": random_combination(wild_mods)}
class TestRandomizeWildPokemon7(TestRandomizeWildPokemon):
    options = {"randomize_wild_pokemon": random_combination(wild_mods)}
class TestRandomizeWildPokemon8(TestRandomizeWildPokemon):
    options = {"randomize_wild_pokemon": random_combination(wild_mods)}
class TestRandomizeWildPokemon9(TestRandomizeWildPokemon):
    options = {"randomize_wild_pokemon": random_combination(wild_mods)}
class TestRandomizeWildPokemon10(TestRandomizeWildPokemon):
    options = {"randomize_wild_pokemon": random_combination(wild_mods)}


class TestRandomizeTrainerPokemon1(TestRandomizeTrainerPokemon):
    options = {"randomize_trainer_pokemon": random_combination(trainer_mods)}
class TestRandomizeTrainerPokemon2(TestRandomizeTrainerPokemon):
    options = {"randomize_trainer_pokemon": random_combination(trainer_mods)}
class TestRandomizeTrainerPokemon3(TestRandomizeTrainerPokemon):
    options = {"randomize_trainer_pokemon": random_combination(trainer_mods)}
class TestRandomizeTrainerPokemon4(TestRandomizeTrainerPokemon):
    options = {"randomize_trainer_pokemon": random_combination(trainer_mods)}
class TestRandomizeTrainerPokemon5(TestRandomizeTrainerPokemon):
    options = {"randomize_trainer_pokemon": random_combination(trainer_mods)}
class TestRandomizeTrainerPokemon6(TestRandomizeTrainerPokemon):
    options = {"randomize_trainer_pokemon": random_combination(trainer_mods)}
class TestRandomizeTrainerPokemon7(TestRandomizeTrainerPokemon):
    options = {"randomize_trainer_pokemon": random_combination(trainer_mods)}
class TestRandomizeTrainerPokemon8(TestRandomizeTrainerPokemon):
    options = {"randomize_trainer_pokemon": random_combination(trainer_mods)}
class TestRandomizeTrainerPokemon9(TestRandomizeTrainerPokemon):
    options = {"randomize_trainer_pokemon": random_combination(trainer_mods)}
class TestRandomizeTrainerPokemon10(TestRandomizeTrainerPokemon):
    options = {"randomize_trainer_pokemon": random_combination(trainer_mods)}