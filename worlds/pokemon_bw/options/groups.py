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
        RandomizeEggGroups,
        RandomizeEggSpecies,
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
        Dexcountsanity,
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
