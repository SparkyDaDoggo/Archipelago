import random
from typing import Iterable, Callable, Type, Any, TYPE_CHECKING

from test.bases import WorldTestBase

if TYPE_CHECKING:
    from .. import PokemonBWWorld


class PokemonBWTestBase(WorldTestBase):
    game = "Pokemon Black and White"
    world: "PokemonBWWorld"


def multiply_random_combinations(option: str, mods: tuple, count: int, additional: dict[str, Any] = None) -> Callable:
    combs = tuple(random_combination(mods) for _ in range(count))
    additional = additional or {}

    def decorator(cls: Type[WorldTestBase]) -> type:
        def create_test(index: int) -> Callable:
            def _test(self: cls):
                self.options = {option: combs[index]} | additional
                for name, value in WorldTestBase.__dict__.items():
                    if not (isinstance(value, Callable) and name[:5] in "test_mod_"):
                        continue
                    with self.subTest(name, game=self.game, seed=self.multiworld.seed):
                        self.world_setup()
                        value(self)

            return _test

        def setUp(self: cls) -> None:
            print("Modifiers: " + ", ".join(self.options[option]))

        cls.auto_construct = False
        cls.setUp = setUp
        for i in range(count):
            setattr(cls, f"test_combination_{i}", create_test(i))
        return cls

    return decorator


def random_combination(mods: Iterable[str]) -> list[str]:
    ret = []
    for i in mods:
        if random.random() < 0.5:
            ret.append(i)
    return ret


# Options checklist:

# version:
#   always random
# goal:
#   default ghetsis
#   one test for each other
#   6 tests with random combinations
# randomize_wild_pokemon:
#   default []
#   one test for just randomize
#   11 tests for random selection of modifiers
# randomize_trainer_pokemon:
#   default []
#   one test for just randomize
#   11 tests for random selection of modifiers
# pokemon_randomization_adjustments:
#   no tests
# encounter_plando:
#   default []
#   one test for multiple plandos with all different parameter variations
#   one test for two plandos + randomize_wild_pokemon = ["Randomize"]
#   one test for two plandos + randomize_wild_pokemon = ["Randomize", "Ensure all obtainable"]
# wild_randomization_blacklist:
#   no tests
# trainer_randomization_blacklist:
#   no tests
# randomize_base_stats:
#   default []
#   one test for just randomize
#   11 tests for random selection of modifiers
# randomize_evolutions:
#   default []
#   one test for just randomize
#   11 tests for random selection of modifiers
# randomize_types:
#   default []
#   one test for just randomize
#   11 tests for random selection of modifiers
# randomize_level_up_movesets:
#   default []
#   one test for just randomize
#   11 tests for random selection of modifiers
# randomize_tm_hm_compatibility:
#   default []
#   one test for just randomize
#   11 tests for random selection of modifiers
# randomize_catch_rates:
#   default []
#   one test for just shuffle
#   11 tests for random selection of modifiers
# randomize_egg_groups:
#   default []
#   one test for just randomize
#   11 tests for random selection of modifiers
# randomize_egg_species:
#   default []
#   one test for just randomize
#   11 tests for random selection of modifiers
# stats_randomization_adjustments:
#   no tests
# stats_plando:
#   default []
#   One test for partial base stats and catch rates
#   One test each for rando/vanilla override/append evolutions + levelup moveset
# randomize_move_data:
#   default []
#   20 tests for random selection of modifiers
# randomize_type_chart:
#   default []
#   one test for just shuffle
#   one test for just randomize
#   5 tests for random selection of modifiers
# move_data_randomization_adjustments:
#   no tests
# move_data_plando:
#   default []
#   One test each for rando/vanilla 2x move data and 2x type chart
# shuffle_badges:
#   default shuffle
#   each other has its own test
# shuffle_tm_hm:
#   default shuffle
#   each other has its own test
# dexsanity:
#   default 0
#   one test for 100
#   one test for 649 + randomize_wild_pokemon = ["Randomize", "Ensure all obtainable"]
#   one test for list with 100 random dex numbers (with ranges) without wild randomization
#   one test for list with 100 random dex numbers (with ranges) with wild randomization
#   one test for list with 100 random dex numbers (with ranges) with wild randomization + ensure all obtainable
# dexcountsanity:
#   default maximum=0
#   One test each for full/partial, every/10 steps, no/10 leniency, vanilla/rando/all wilds
# seensanity:
#   default 0
#   One test each for full/partial, vanilla/rando/all wilds + all_pokemon_seen
#   One test each for random list of 100 (with ranges) with vanilla/rando/all wilds + all_pokemon_seen
# seencountsanity:
#   default maximum=0
#   One test each for full/partial, 10 steps, 10 leniency, vanilla/rando/all wilds + all_pokemon_seen
# shinysanity:
#   default False
#   One test for True
#   One test each for full/partial, vanilla/rando/all wilds
#   One test each for random list of 100 (with ranges) with vanilla/rando/all wilds
# shinycountsanity:
#   default False
#   One test for True
#   One test each for full/partial, 10 steps, 10 leniency, vanilla/rando/all wilds
# season_control:
#   default vanilla
#   each other has its own test
# modify_item_pool:
#   default []
#   one test for all modifiers combined
# modify_logic:
#   one test for []
#   one test for all included
# filler_items_blacklist:
#   no tests
# adjust_levels:
#   default ["Trainer by distance", "Wild by distance"]
#   one test for []
#   one test for ["Trainer by distance", "Wild by distance", "Trainer by sphere", "Wild by sphere"]
#   one test for ["Trainer by sphere", "Wild by sphere"]
# modify_levels:
#   default {"Trainer value": 100, "Wild value": 100, "Trainer mode": 0, "Wild mode": 0}
#   other values in simple mode only relevant in patching process
#   one test for [] (advanced mode)
#   one test for list of 5 random calculations (advanced mode)
# modify_encounter_rates:
#   default vanilla
#   one test for each other choice
#   one test for custom rates with not all methods filled
# experience_multiplier:
#   irrelevant for generator
# all_pokemon_seen:
#   default false
#   one test for true
# replace_evo_methods:
#   default []
#   one test for all included
# master_ball_seller:
#   default []
#   one test for one seller and one standard cost
#   one test for two sellers and two standard costs
#   one test for one seller and no cost
#   one test for one seller and two random custom costs
# start_inventory_from_pool:
#   no tests
# funny_dialog:
#   default none
#   one test for each other choice
# text_plando:
#   default []
#   one test for multiple lines with all kinds of commands
#   one test for multiple lines + funny dialog
#   one test for multiple lines + efficient dialog
# plugin_options:
#   irrelevant to generator
# reusable_tms:
#   too complex to test
