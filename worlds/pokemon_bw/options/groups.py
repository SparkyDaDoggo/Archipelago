from Options import OptionGroup
from . import *

option_groups = [
    OptionGroup("Encounter", [
        RandomizeWildPokemon,
        RandomizeTrainerPokemon,
        PokemonRandomizationAdjustments,
        EncounterPlando,
        WildRandomizationBlacklist,
        TrainerRandomizationBlacklist,
    ]),
    OptionGroup("Stats", [
        RandomizeBaseStats,
        RandomizeEvolutions,
        RandomizeTypes,
        RandomizeCatchRates,
        RandomizeLevelUpMovesets,
        RandomizeTMHMCompatibility,
        StatsRandomizationAdjustments,
        StatsPlando,
    ]),
    OptionGroup("Move Data", [
        RandomizeMoveData,
        RandomizeTypeChart,
        MoveDataRandomizationAdjustments,
        MoveDataPlando,
    ]),
    OptionGroup("Items, locations, and progression", [
        ShuffleBadgeRewards,
        ShuffleTMRewards,
        Dexsanity,
        SeasonControl,
        ModifyItemPool,
        ModifyLogic,
        FillerItemsBlacklist,
    ]),
    OptionGroup("Miscellaneous", [
        AdjustLevels,
        ModifyLevels,
        ModifyEncounterRates,
        ExpMultiplier,
        AllPokemonSeen,
        ReplaceEvoMethods,
        MasterBallSeller,
        # StartInventoryPool, not allowed in new option group
        FunnyDialog,
        PokemonBWTextPlando,
        PluginOptions,
        ReusableTMs,
    ]),
]
