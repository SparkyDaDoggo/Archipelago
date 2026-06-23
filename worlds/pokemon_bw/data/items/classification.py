from BaseClasses import ItemClassification
from .. import ClassificationMethod


always_progression: ClassificationMethod = lambda world, item: ItemClassification.progression

always_useful: ClassificationMethod = lambda world, item: ItemClassification.useful

always_filler: ClassificationMethod = lambda world, item: ItemClassification.filler

always_trap: ClassificationMethod = lambda world, item: ItemClassification.trap

tm_hm_hunt: ClassificationMethod = lambda world, item: (
    ItemClassification.progression_deprioritized
    if (world.options.goal == "tmhm_hunt"
        or (world.options.goal == "pokemon_master"
            and (not world.options.goal.combined
                 or "tmhm_hunt" in world.options.goal.combined
                 or "pokemon_master" in world.options.goal.combined))
        or item == world.driftveil_random_tm)
    else ItemClassification.useful
)

dowsing_machine_logic: ClassificationMethod = lambda world, item: (
    ItemClassification.progression
    if world.options.modify_logic.is_require_dowsing else ItemClassification.useful
)
