import random

from test.bases import WorldTestBase

from . import random_combination
from ..options import Goal


class PokemonBWTestBase(WorldTestBase):
    game = "Pokemon Black and White"


all_goals = list(Goal.options)
# all_goals.remove("pokemon_master")


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
# Encounter Plando                                #
###################################################


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


###################################################
# Stats Plando                                    #
###################################################

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
                                     {"species": "Caterpie",
                                      "method": "Stone",
                                      "stone": "Water Stone"}],
                      "override_evolutions": True,
                      "levelup_moveset": [{"move": "Pound",
                                           "level": 1},
                                          {"move": "Earthquake",
                                           "level": 100}],
                      "override_levelup_moveset": True},
        "Squirtle": {"evolutions": [{"species": "Weedle",
                                     "level": 5},
                                    {"species": "Caterpie",
                                     "method": "Stone",
                                     "stone": "Water Stone"}],
                     "override_evolutions": False,
                     "levelup_moveset": [{"move": "Pound",
                                          "level": 10},
                                         {"move": "Earthquake",
                                          "level": 100}],
                     "override_levelup_moveset": False},
    }}


class TestStatsPlandoEvoLevelupMoveRandomized(PokemonBWTestBase):
    options = {"stats_plando": {
        "Bulbasaur": {"evolutions": [{"species": "Weedle"},
                                     {"species": "Caterpie",
                                      "method": "Stone",
                                      "stone": "Water Stone"}],
                      "override_evolutions": True,
                      "levelup_moveset": [{"move": "Pound",
                                           "level": 1},
                                          {"move": "Earthquake",
                                           "level": 100}],
                      "override_levelup_moveset": True},
        "Squirtle": {"evolutions": [{"species": "Weedle",
                                     "level": 5},
                                    {"species": "Caterpie",
                                     "method": "Stone",
                                     "stone": "Water Stone"}],
                     "override_evolutions": False,
                     "levelup_moveset": [{"move": "Pound",
                                          "level": 10},
                                         {"move": "Earthquake",
                                          "level": 100}],
                     "override_levelup_moveset": False},
    }, "randomize_evolutions": ["Randomize"], "randomize_level_up_movesets": ["Randomize"]}


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
        "dexsanity": [random.randint(1, 649) for _ in range(100)],
    }


class TestDexsanityPlandoRandomized(PokemonBWTestBase):
    options = {
        "dexsanity": [random.randint(1, 649) for _ in range(100)],
        "randomize_wild_pokemon": ["Randomize"],
    }


class TestDexsanityPlandoAllObtainable(PokemonBWTestBase):
    options = {
        "dexsanity": [random.randint(1, 649) for _ in range(100)],
        "randomize_wild_pokemon": ["Randomize", "Ensure all obtainable"],
    }


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

