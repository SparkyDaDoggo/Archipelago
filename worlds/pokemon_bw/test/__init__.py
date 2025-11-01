
# Options checklist:

# version:
#   always random
# goal:
#   default ghetsis
#   each other has its own test
# randomize_wild_pokemon:
#   default []
#   one test for all modifiers
#   11 tests for "Randomize" + random selection of other modifiers
# randomize_trainer_pokemon:
#   default []
#   one test for just "Randomize"
#   one test for both
# pokemon_randomization_adjustments:
#   default {"Stats leniency": 10, "Overpowered threshold": 500}
#   other values irrelevant
#   no other parameters so far
# encounter_plando:
#   default []
#   one test for multiple plandos with all different parameter variations
#   one test for two plandos + randomize_wild_pokemon = ["Randomize"]
#   one test for two plandos + randomize_wild_pokemon = ["Randomize", "Ensure all obtainable"]
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
# adjust_levels:
#   default ["Trainer", "Wild"]
#   one test for []
# modify_levels:
#   default {"Trainer value": 100, "Wild value": 100, "Trainer mode": 0, "Wild mode": 0}
#   other values in simple mode only relevant in patching process
#   one test for [] (advanced mode)
#   one test for list of 5 random calculations (advanced mode)
# master_ball_seller:
#   default []
#   one test for one seller and one standard cost
#   one test for two sellers and two standard costs
#   one test for one seller and no cost
#   one test for one seller and two random custom costs
# start_inventory_from_pool:
#   default {}
#   taken from core without modifications
# modify_item_pool:
#   default []
#   one test for all modifiers combined
# modify_logic:
#   default ["Require Dowsing Machine", "Prioritize key item locations"]
#   one test for []
# funny_dialog:
#   default none
#   one test for each other choice
# text_plando:
#   default []
#   one test for multiple lines with all kinds of commands
#   one test for multiple lines + funny dialog
#   one test for multiple lines + efficient dialog
# reusable_tms:
#   too complex to test
