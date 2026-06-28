import random
from typing import Iterable


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
# randomize_catch_rates:
#   default []
#   one test for just shuffle
#   11 tests for random selection of modifiers
# randomize_level_up_movesets:
#   default []
#   one test for just randomize
#   11 tests for random selection of modifiers
# randomize_tm_hm_compatibility:
#   default []
#   one test for just randomize
#   11 tests for random selection of modifiers
# stats_randomization_adjustments:
#   no tests
# stats_plando:
#   default []
#   One test for partial base stats and catch rates
#   One test each for rando/vanilla override/append evolutions + levelup moveset
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
#   one test for list with 100 random dex numbers without wild randomization
#   one test for list with 100 random dex numbers with wild randomization
#   one test for list with 100 random dex numbers with wild randomization + ensure all obtainable
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
#   default ["Trainer", "Wild"]
#   one test for []
# modify_levels:
#   default {"Trainer value": 100, "Wild value": 100, "Trainer mode": 0, "Wild mode": 0}
#   other values in simple mode only relevant in patching process
#   one test for [] (advanced mode)
#   one test for list of 5 random calculations (advanced mode)
# modify_encounter_rates:
#   default vanilla
#   one test for each other choice each
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
