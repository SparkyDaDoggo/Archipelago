from BaseClasses import ItemClassification
from .. import ClassificationMethod


always_progression: ClassificationMethod = lambda world: ItemClassification.progression

always_useful: ClassificationMethod = lambda world: ItemClassification.useful

always_filler: ClassificationMethod = lambda world: ItemClassification.filler

always_trap: ClassificationMethod = lambda world: ItemClassification.trap

tm_hm_hunt: ClassificationMethod = lambda world: (
    ItemClassification.progression_deprioritized
    if world.options.goal == "tmhm_hunt" or (world.options.goal.combined == "pokemon_master"
                                             and (world.options.goal.combined is None
                                                  or "tmhm_hunt" in world.options.goal.combined
                                                  or "pokemon_master" in world.options.goal.combined))
    else ItemClassification.useful
)

dowsing_machine_logic: ClassificationMethod = lambda world: (
    ItemClassification.progression
    if world.options.modify_logic.is_require_dowsing else ItemClassification.useful
)
