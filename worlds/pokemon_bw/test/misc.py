import random

from . import random_combination, PokemonBWTestBase
from ..options import Goal


all_goals = list(Goal.options)


###################################################
# Goal                                            #
###################################################


class TestGoalChampion(PokemonBWTestBase):
    options = {"goal": "champion"}
class TestGoalCynthia(PokemonBWTestBase):
    options = {"goal": "cynthia"}
class TestGoalCobalion(PokemonBWTestBase):
    options = {"goal": "cobalion"}
class TestGoalTMHMHunt(PokemonBWTestBase):
    options = {"goal": "tmhm_hunt"}
class TestGoalSevenSagesHunt(PokemonBWTestBase):
    options = {"goal": "seven_sages_hunt"}
class TestGoalLegendaryHunt(PokemonBWTestBase):
    options = {"goal": "legendary_hunt"}
class TestGoalPokemonMaster(PokemonBWTestBase):
    options = {"goal": "pokemon_master"}
class TestCombinedGoal(PokemonBWTestBase):
    options = {"goal": random_combination(all_goals)}
    def setUp(self) -> None:
        print("Modifiers: "+", ".join(self.options["goal"]))
        super().setUp()
class TestCombinedGoal1(TestCombinedGoal):
    options = {"goal": random_combination(all_goals)}
class TestCombinedGoal2(TestCombinedGoal):
    options = {"goal": random_combination(all_goals)}
class TestCombinedGoal3(TestCombinedGoal):
    options = {"goal": random_combination(all_goals)}
class TestCombinedGoal4(TestCombinedGoal):
    options = {"goal": random_combination(all_goals)}
class TestCombinedGoal5(TestCombinedGoal):
    options = {"goal": random_combination(all_goals)}


###################################################
# Shuffle Badges                                  #
###################################################


class TestShuffleBadgesVanilla(PokemonBWTestBase):
    options = {"shuffle_badges": "vanilla"}
class TestShuffleBadgesAnything(PokemonBWTestBase):
    options = {"shuffle_badges": "anything"}


###################################################
# Shuffle TM/HM                                   #
###################################################


class TestShuffleTMHMHMWithBadge(PokemonBWTestBase):
    options = {"shuffle_tm_hm": "hm_with_badge"}
class TestShuffleTMHMAnything(PokemonBWTestBase):
    options = {"shuffle_tm_hm": "anything"}


###################################################
# Season Control                                  #
###################################################


class TestSeasonControlChangeable(PokemonBWTestBase):
    options = {"season_control": "changeable"}
class TestSeasonControlRandomized(PokemonBWTestBase):
    options = {"season_control": "randomized"}


###################################################
# Modify Item Pool                                #
###################################################


class TestModifyItemPoolAll(PokemonBWTestBase):
    options = {"modify_item_pool": ["Useless key items", "Useful filler", "Ban bad filler"]}


###################################################
# Modify Logic                                    #
###################################################


class TestModifyLogicNone(PokemonBWTestBase):
    options = {"modify_logic": []}
class TestModifyLogicAll(PokemonBWTestBase):
    options = {"modify_logic": ["Require Dowsing Machine", "Require flash", "Consider evolutions",
                                "Consider static pokemon", "Consider trades", "Consider form change"]}


###################################################
# Adjust Levels                                   #
###################################################


class TestAdjustLevelsNone(PokemonBWTestBase):
    options = {"adjust_levels": []}
class TestAdjustLevelsAll(PokemonBWTestBase):
    options = {"adjust_levels": ["Trainer by distance", "Wild by distance", "Trainer by sphere", "Wild by sphere"]}
class TestAdjustLevelsOnlySphere(PokemonBWTestBase):
    options = {"adjust_levels": ["Trainer by sphere", "Wild by sphere"]}


###################################################
# Modify Levels                                   #
###################################################


def get_random_modify_levels() -> dict[str, int]:
    opt_type = random.choice(("Trainer", "Wild"))
    opt_mode = random.choice(("Multiply", "Add", "Power"))
    if opt_mode == "Multiply":
        opt_value = random.randint(1, 10000)
    elif opt_mode == "Add":
        opt_value = random.randint(-99, 99)
    else:
        opt_value = random.randint(1, 700)
    return {"type": opt_type, "mode": opt_mode, "value": opt_value}


class TestModifyLevelsAdvancedEmpty(PokemonBWTestBase):
    options = {"modify_levels": []}
class TestModifyLevelsAdvancedRandom(PokemonBWTestBase):
    options = {"modify_levels": [
        get_random_modify_levels()
        for _ in range(5)
    ]}


###################################################
# Modify Encounter Rates                          #
###################################################


class TestModifyEncounterRatesTryNormalized(PokemonBWTestBase):
    options = {"modify_encounter_rates": "try_normalized"}
class TestModifyEncounterRatesTryNormalizedAlt(PokemonBWTestBase):
    options = {"modify_encounter_rates": "try_normalized_alt"}
class TestModifyEncounterRatesInvasive(PokemonBWTestBase):
    options = {"modify_encounter_rates": "invasive"}
class TestModifyEncounterRatesOnePerMethod(PokemonBWTestBase):
    options = {"modify_encounter_rates": "one_per_method"}
class TestModifyEncounterRatesDexsanityFriendly(PokemonBWTestBase):
    options = {"modify_encounter_rates": "dexsanity_friendly"}
class TestModifyEncounterRatesRandomized12(PokemonBWTestBase):
    options = {"modify_encounter_rates": "randomized_12"}
class TestModifyEncounterRatesCustom(PokemonBWTestBase):
    options = {"modify_encounter_rates": {
        "Grass": [12, 23, 4, 6, 18, 1, 6, 5, 5, 7, 7, 6],
        "Fishing": [21, 19, 22, 18, 20],
    }}


###################################################
# All Pokémon Seen                                #
###################################################


class TestAllPokemonSeenTrue(PokemonBWTestBase):
    options = {"all_pokemon_seen": True}


###################################################
# Replace Evo Methods                             #
###################################################


class TestReplaceEvoMethodsAll(PokemonBWTestBase):
    options = {"replace_evo_methods": ["Locations", "Friendship", "PID", "Stats"]}


###################################################
# Master Ball Seller                              #
###################################################


class TestMasterBallSellerOneCost(PokemonBWTestBase):
    options = {"master_ball_seller": ["Ns Castle", "Cost 1000"]}
class TestMasterBallSellerTwoCosts(PokemonBWTestBase):
    options = {"master_ball_seller": ["PC", "Cherens Mom", "Cost Free", "Cost 10000"]}
class TestMasterBallSellerNoCost(PokemonBWTestBase):
    options = {"master_ball_seller": ["Undella Mansion seller"]}
class TestMasterBallSellerCustomCosts(PokemonBWTestBase):
    options = {"master_ball_seller": [
        "Ns Castle",
        f"Cost {random.randint(0, 30000)}",
        f"Cost {random.randint(0, 30000)}"
    ]}


###################################################
# Funny Dialog                                    #
###################################################


class TestFunnyDialogFunny(PokemonBWTestBase):
    options = {"funny_dialog": "funny"}
class TestFunnyDialogEfficient(PokemonBWTestBase):
    options = {"funny_dialog": "efficient"}


###################################################
# Text Plando                                     #
###################################################


class TestTextPlandoSimple(PokemonBWTestBase):
    options = {"text_plando": [
        {"at": "system 12 0 1", "text": "Test 123[Terminate]", "percentage": 12},
        {"at": "story 0 0 1", "text": "Test[c_100_#1_0][NextLine]123[Terminate]", "percentage": 100},
        {"at": "system 12 0 1", "text": "Test[End][NextLine]123[NextLine]123[Scroll][NextLine]lol[Terminate]"},
    ]}
class TestTextPlandoWithFunny(PokemonBWTestBase):
    options = {
        "text_plando": [
            {"at": "system 12 0 1", "text": "Test 123[Terminate]", "percentage": 12},
            {"at": "story 0 0 1", "text": "Test[c_100_#1_0][NextLine]123[Terminate]", "percentage": 100},
            {"at": "system 12 0 1", "text": "Test[End][NextLine]123[NextLine]123[Scroll][NextLine]lol[Terminate]"},
        ],
        "funny_dialog": "funny",
    }
class TestTextPlandoWithEfficient(PokemonBWTestBase):
    options = {
        "text_plando": [
            {"at": "system 12 0 1", "text": "Test 123[Terminate]", "percentage": 12},
            {"at": "story 0 0 1", "text": "Test[c_100_#1_0][NextLine]123[Terminate]", "percentage": 100},
            {"at": "system 12 0 1", "text": "Test[End][NextLine]123[NextLine]123[Scroll][NextLine]lol[Terminate]"},
        ],
        "funny_dialog": "efficient",
    }
