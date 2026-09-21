from BaseClasses import ItemClassification
from .. import ClassificationMethod


always_progression: ClassificationMethod = lambda world, item: ItemClassification.progression

always_useful: ClassificationMethod = lambda world, item: ItemClassification.useful

always_filler: ClassificationMethod = lambda world, item: ItemClassification.filler

always_trap: ClassificationMethod = lambda world, item: ItemClassification.trap

tm_hm_class: ClassificationMethod = lambda world, item: (
    ItemClassification.progression_deprioritized
    if "tmhm_hunt" in world.options.goal.current_key or item == world.driftveil_random_tm
    else ItemClassification.useful
)

dowsing_machine_logic: ClassificationMethod = lambda world, item: (
    ItemClassification.progression
    if world.options.modify_logic.is_require_dowsing
    else ItemClassification.useful
)
