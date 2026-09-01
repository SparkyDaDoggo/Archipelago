import random

from . import PokemonBWTestBase


###################################################
# Dexsanity                                       #
###################################################


class TestDexsanityPartial(PokemonBWTestBase):
    options = {"dexsanity": 100}
class TestDexsanityFull(PokemonBWTestBase):
    options = {
        "dexsanity": 649,
        "randomize_wild_pokemon": ["Randomize", "Ensure all obtainable"],
    }
class TestDexsanityPlandoVanilla(PokemonBWTestBase):
    options = {
        "dexsanity": [random.randint(1, 649) for _ in range(98)] + ["10-20", "450-500"],
    }
class TestDexsanityPlandoRandomized(PokemonBWTestBase):
    options = {
        "dexsanity": [random.randint(1, 649) for _ in range(98)] + ["10-20", "450-500"],
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestDexsanityPlandoAllObtainable(PokemonBWTestBase):
    options = {
        "dexsanity": [random.randint(1, 649) for _ in range(98)] + ["10-20", "450-500"],
        "randomize_wild_pokemon": ["Randomize", "Ensure all obtainable"],
    }


###################################################
# Dexcountsanity                                  #
###################################################


class TestDexcountsanityPartialVanilla(PokemonBWTestBase):
    options = {"dexcountsanity": {"Maximum": 100}}
class TestDexcountsanityPartialRando(PokemonBWTestBase):
    options = {
        "dexcountsanity": {"Maximum": 100},
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestDexcountsanityPartialEnsureAll(PokemonBWTestBase):
    options = {
        "dexcountsanity": {"Maximum": 100},
        "randomize_wild_pokemon": ["Ensure all obtainable"],
    }
class TestDexcountsanityFullVanilla(PokemonBWTestBase):
    options = {"dexcountsanity": {"Maximum": 649}}
class TestDexcountsanityFullRando(PokemonBWTestBase):
    options = {
        "dexcountsanity": {"Maximum": 649},
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestDexcountsanityFullEnsureAll(PokemonBWTestBase):
    options = {
        "dexcountsanity": {"Maximum": 649},
        "randomize_wild_pokemon": ["Ensure all obtainable"],
    }
class TestDexcountsanityPartial10StepsVanilla(PokemonBWTestBase):
    options = {"dexcountsanity": {"Maximum": 100, "Steps": 10}}
class TestDexcountsanityPartial10StepsRando(PokemonBWTestBase):
    options = {
        "dexcountsanity": {"Maximum": 100, "Steps": 10},
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestDexcountsanityPartial10StepsEnsureAll(PokemonBWTestBase):
    options = {
        "dexcountsanity": {"Maximum": 100, "Steps": 10},
        "randomize_wild_pokemon": ["Ensure all obtainable"],
    }
class TestDexcountsanityFull10StepsVanilla(PokemonBWTestBase):
    options = {"dexcountsanity": {"Maximum": 649, "Steps": 10}}
class TestDexcountsanityFull10StepsRando(PokemonBWTestBase):
    options = {
        "dexcountsanity": {"Maximum": 649, "Steps": 10},
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestDexcountsanityFull10StepsEnsureAll(PokemonBWTestBase):
    options = {
        "dexcountsanity": {"Maximum": 649, "Steps": 10},
        "randomize_wild_pokemon": ["Ensure all obtainable"],
    }
class TestDexcountsanityPartialLeniency10Vanilla(PokemonBWTestBase):
    options = {"dexcountsanity": {"Maximum": 100, "Leniency": 10}}
class TestDexcountsanityPartialLeniency10Rando(PokemonBWTestBase):
    options = {
        "dexcountsanity": {"Maximum": 100, "Leniency": 10},
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestDexcountsanityPartialLeniency10EnsureAll(PokemonBWTestBase):
    options = {
        "dexcountsanity": {"Maximum": 100, "Leniency": 10},
        "randomize_wild_pokemon": ["Ensure all obtainable"],
    }
class TestDexcountsanityFullLeniency10Vanilla(PokemonBWTestBase):
    options = {"dexcountsanity": {"Maximum": 649, "Leniency": 10}}
class TestDexcountsanityFullLeniency10Rando(PokemonBWTestBase):
    options = {
        "dexcountsanity": {"Maximum": 649, "Leniency": 10},
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestDexcountsanityFullLeniency10EnsureAll(PokemonBWTestBase):
    options = {
        "dexcountsanity": {"Maximum": 649, "Leniency": 10},
        "randomize_wild_pokemon": ["Ensure all obtainable"],
    }
class TestDexcountsanityPartial10StepsLeniency10Vanilla(PokemonBWTestBase):
    options = {"dexcountsanity": {"Maximum": 100, "Steps": 10, "Leniency": 10}}
class TestDexcountsanityPartial10StepsLeniency10Rando(PokemonBWTestBase):
    options = {
        "dexcountsanity": {"Maximum": 100, "Steps": 10, "Leniency": 10},
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestDexcountsanityPartial10StepsLeniency10EnsureAll(PokemonBWTestBase):
    options = {
        "dexcountsanity": {"Maximum": 100, "Steps": 10, "Leniency": 10},
        "randomize_wild_pokemon": ["Ensure all obtainable"],
    }
class TestDexcountsanityFull10StepsLeniency10Vanilla(PokemonBWTestBase):
    options = {"dexcountsanity": {"Maximum": 649, "Steps": 10, "Leniency": 10}}
class TestDexcountsanityFull10StepsLeniency10Rando(PokemonBWTestBase):
    options = {
        "dexcountsanity": {"Maximum": 649, "Steps": 10, "Leniency": 10},
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestDexcountsanityFull10StepsLeniency10EnsureAll(PokemonBWTestBase):
    options = {
        "dexcountsanity": {"Maximum": 649, "Steps": 10, "Leniency": 10},
        "randomize_wild_pokemon": ["Ensure all obtainable"],
    }


###################################################
# Seensanity                                      #
###################################################


class TestSeensanityPartialVanilla(PokemonBWTestBase):
    options = {
        "seensanity": 100,
        "all_pokemon_seen": True,
    }
class TestSeensanityPartialRando(PokemonBWTestBase):
    options = {
        "seensanity": 100,
        "all_pokemon_seen": True,
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestSeensanityPartialEnsureAll(PokemonBWTestBase):
    options = {
        "seensanity": 100,
        "all_pokemon_seen": True,
        "randomize_wild_pokemon": ["Ensure all obtainable"],
    }
class TestSeensanityFullVanilla(PokemonBWTestBase):
    options = {
        "seensanity": 649,
        "all_pokemon_seen": True,
    }
class TestSeensanityFullRando(PokemonBWTestBase):
    options = {
        "seensanity": 649,
        "all_pokemon_seen": True,
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestSeensanityFullEnsureAll(PokemonBWTestBase):
    options = {
        "seensanity": 649,
        "all_pokemon_seen": True,
        "randomize_wild_pokemon": ["Ensure all obtainable"],
    }
class TestSeensanityPlandoVanilla(PokemonBWTestBase):
    options = {
        "seensanity": [random.randint(1, 649) for _ in range(98)] + ["10-20", "450-500"],
        "all_pokemon_seen": True,
    }
class TestSeensanityPlandoRando(PokemonBWTestBase):
    options = {
        "seensanity": [random.randint(1, 649) for _ in range(98)] + ["10-20", "450-500"],
        "all_pokemon_seen": True,
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestSeensanityPlandoEnsureAll(PokemonBWTestBase):
    options = {
        "seensanity": [random.randint(1, 649) for _ in range(98)] + ["10-20", "450-500"],
        "all_pokemon_seen": True,
        "randomize_wild_pokemon": ["Ensure all obtainable"],
    }


###################################################
# Seencountsanity                                 #
###################################################


class TestSeencountsanityPartialVanilla(PokemonBWTestBase):
    options = {
        "seencountsanity": {"Maximum": 100, "Steps": 10, "Leniency": 10},
        "all_pokemon_seen": True,
    }
class TestSeencountsanityPartialRando(PokemonBWTestBase):
    options = {
        "seencountsanity": {"Maximum": 100, "Steps": 10, "Leniency": 10},
        "all_pokemon_seen": True,
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestSeencountsanityPartialEnsureAll(PokemonBWTestBase):
    options = {
        "seencountsanity": {"Maximum": 100, "Steps": 10, "Leniency": 10},
        "all_pokemon_seen": True,
        "randomize_wild_pokemon": ["Ensure all obtainable"],
    }
class TestSeencountsanityFullVanilla(PokemonBWTestBase):
    options = {
        "seencountsanity": {"Maximum": 649, "Steps": 10, "Leniency": 10},
        "all_pokemon_seen": True,
    }
class TestSeencountsanityFullRando(PokemonBWTestBase):
    options = {
        "seencountsanity": {"Maximum": 649, "Steps": 10, "Leniency": 10},
        "all_pokemon_seen": True,
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestSeencountsanityFullEnsureAll(PokemonBWTestBase):
    options = {
        "seencountsanity": {"Maximum": 649, "Steps": 10, "Leniency": 10},
        "all_pokemon_seen": True,
        "randomize_wild_pokemon": ["Ensure all obtainable"],
    }


###################################################
# Shinysanity                                     #
###################################################


class TestShinysanityTrue(PokemonBWTestBase):
    options = {
        "shinysanity": True,
    }
class TestShinysanityPartialVanilla(PokemonBWTestBase):
    options = {
        "shinysanity": 100,
    }
class TestShinysanityPartialRando(PokemonBWTestBase):
    options = {
        "shinysanity": 100,
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestShinysanityPartialEnsureAll(PokemonBWTestBase):
    options = {
        "shinysanity": 100,
        "randomize_wild_pokemon": ["Ensure all obtainable"],
    }
class TestShinysanityFullVanilla(PokemonBWTestBase):
    options = {
        "shinysanity": 649,
    }
class TestShinysanityFullRando(PokemonBWTestBase):
    options = {
        "shinysanity": 649,
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestShinysanityFullEnsureAll(PokemonBWTestBase):
    options = {
        "shinysanity": 649,
        "randomize_wild_pokemon": ["Ensure all obtainable"],
    }
class TestShinysanityPlandoVanilla(PokemonBWTestBase):
    options = {
        "shinysanity": [random.randint(1, 649) for _ in range(98)] + ["10-20", "450-500"],
    }
class TestShinysanityPlandoRando(PokemonBWTestBase):
    options = {
        "shinysanity": [random.randint(1, 649) for _ in range(98)] + ["10-20", "450-500"],
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestShinysanityPlandoEnsureAll(PokemonBWTestBase):
    options = {
        "shinysanity": [random.randint(1, 649) for _ in range(98)] + ["10-20", "450-500"],
        "randomize_wild_pokemon": ["Ensure all obtainable"],
    }


###################################################
# Shinycountsanity                                 #
###################################################


class TestShinycountsanityTrue(PokemonBWTestBase):
    options = {
        "shinycountsanity": True,
    }
class TestShinycountsanityPartialVanilla(PokemonBWTestBase):
    options = {
        "shinycountsanity": {"Maximum": 100, "Steps": 10, "Leniency": 10},
    }
class TestShinycountsanityPartialRando(PokemonBWTestBase):
    options = {
        "shinycountsanity": {"Maximum": 100, "Steps": 10, "Leniency": 10},
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestShinycountsanityPartialEnsureAll(PokemonBWTestBase):
    options = {
        "shinycountsanity": {"Maximum": 100, "Steps": 10, "Leniency": 10},
        "randomize_wild_pokemon": ["Ensure all obtainable"],
    }
class TestShinycountsanityFullVanilla(PokemonBWTestBase):
    options = {
        "shinycountsanity": {"Maximum": 649, "Steps": 10, "Leniency": 10},
    }
class TestShinycountsanityFullRando(PokemonBWTestBase):
    options = {
        "shinycountsanity": {"Maximum": 649, "Steps": 10, "Leniency": 10},
        "randomize_wild_pokemon": ["Randomize"],
    }
class TestShinycountsanityFullEnsureAll(PokemonBWTestBase):
    options = {
        "shinycountsanity": {"Maximum": 649, "Steps": 10, "Leniency": 10},
        "randomize_wild_pokemon": ["Ensure all obtainable"],
    }
