from . import multiply_random_combinations, PokemonBWTestBase
from ..options import RandomizeWildPokemon, RandomizeTrainerPokemon
from ..data.pokemon.species import by_name


class TestRandomizeWildPokemonSimple(PokemonBWTestBase):
    options = {"randomize_wild_pokemon": ["Randomize"]}
@multiply_random_combinations("randomize_wild_pokemon", tuple(RandomizeWildPokemon.valid_keys), 11)
class TestRandomizeWildPokemon(PokemonBWTestBase):

    def mod_ensure_all_obtainable(self):
        if "Ensure all obtainable" not in self.options["randomize_wild_pokemon"]:
            return
        with self.subTest("Game", game=self.game, seed=self.multiworld.seed):
            for name in by_name:
                self.assertIn(name, self.world.catchable_species_data,
                              f"Species {name} appears to not be catchable anywhere")


class TestRandomizeTrainerPokemonSimple(PokemonBWTestBase):
    options = {"randomize_trainer_pokemon": ["Randomize"]}
@multiply_random_combinations("randomize_trainer_pokemon", tuple(RandomizeTrainerPokemon.valid_keys), 10)
class TestRandomizeTrainerPokemon(PokemonBWTestBase):
    pass


class TestEncounterPlandoEmpty(PokemonBWTestBase):
    options = {"encounter_plando": []}
class TestEncounterPlandoAllParameters(PokemonBWTestBase):
    options = {
        "encounter_plando": [
            {
                "map": "Route 1",
                "method": "Grass",
                "species": "Kyogre",
            },
            {
                "map": "Route 8",
                "seasons": "Summer",
                "method": "Surfing",
                "slots": 1,
                "species": ["Charmander", "Squirtle", "Bulbasaur"],
            },
            {
                "map": "Icirrus City",
                "seasons": ["Summer", "Winter"],
                "method": "Surfing",
                "slots": [1, 3, 4],
                "species": "Blastoise",
            },
            {
                "map": "Route 16",
                "method": "Grass",
                "species": "None",
            },
        ],
    }
class TestEncounterPlandoRandomize(PokemonBWTestBase):
    options = {
        "encounter_plando": [
            {
                "map": "Route 1",
                "method": "Grass",
                "species": "Kyogre",
            },
            {
                "map": "Route 2",
                "method": "Rustling grass",
                "species": "Groudon",
            },
        ],
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestEncounterPlandoRandomizeAllObtainable(PokemonBWTestBase):
    options = {
        "encounter_plando": [
            {
                "map": "Route 1",
                "method": "Grass",
                "species": "Kyogre",
            },
            {
                "map": "Route 2",
                "method": "Rustling grass",
                "species": "Groudon",
            },
        ],
        "randomize_wild_pokemon": ["Randomize", "Ensure all obtainable"],
    }
