from typing import TYPE_CHECKING

from ...locations import PokemonBWLocation
from BaseClasses import ItemClassification
from ...items import PokemonBWItem

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def create(world: "PokemonBWWorld"):
    from ...data.trainers.data import table as trainer_table

    max_in_region: dict[str, int] = {"Hall of Fame": 100}

    for data in world.wild_encounter.values():
        lvl = (data.max_level + data.min_level) // 2
        if data.region not in max_in_region or lvl > max_in_region[data.region]:
            max_in_region[data.region] = lvl
    for tp_data in world.trainer_teams:
        t_data = trainer_table[tp_data.trainer_id - 1]
        if t_data.logic_inc_rule and not t_data.logic_inc_rule(world):
            continue
        reg = t_data.region
        if reg and reg not in max_in_region or tp_data.level > max_in_region[reg]:
            max_in_region[reg] = tp_data.level

    for reg, lvl in max_in_region.items():
        r = world.regions[reg]
        l = PokemonBWLocation(world.player, "[Lvl] " + reg, None, r)
        item = PokemonBWItem(f"[Lvl] {lvl}", ItemClassification.progression, None, world.player)
        l.place_locked_item(item)
        l.show_in_spoiler = False
        r.locations.append(l)
