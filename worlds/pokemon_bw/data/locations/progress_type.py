from BaseClasses import LocationProgressType
from .. import ProgressTypeMethod


always_priority: ProgressTypeMethod = lambda world: LocationProgressType.PRIORITY

always_default: ProgressTypeMethod = lambda world: LocationProgressType.DEFAULT

always_excluded: ProgressTypeMethod = lambda world: LocationProgressType.EXCLUDED

season_dependant: ProgressTypeMethod = lambda world: (
    LocationProgressType.DEFAULT
    if world.options.season_control != "vanilla"
    else LocationProgressType.EXCLUDED
)

wild_rando_dependant: ProgressTypeMethod = lambda world: (
    LocationProgressType.DEFAULT
    if world.options.randomize_wild_pokemon.is_randomize
    else LocationProgressType.EXCLUDED
)

deerling_dependant: ProgressTypeMethod = lambda world: season_dependant(world) or wild_rando_dependant(world)

key_item_location: ProgressTypeMethod = always_default
