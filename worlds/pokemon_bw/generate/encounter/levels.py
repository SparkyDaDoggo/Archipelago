from typing import TYPE_CHECKING

from ...options import ModifyLevels

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def adjust_and_modify(world: "PokemonBWWorld"):
    from ...data.trainers.data import table as trainer_table

    if world.options.adjust_levels.is_wild_by_distance or world.options.adjust_levels.is_trainer_by_distance:

        distances = world.region_distances
        max_distance = max(distances.values())

        # 52 is what the first pokémon of Ghetsis will get, such that his last pokémon will be 54
        # furthest distance first level is 50, trainers will get a +2 bonus
        # N's team in his throne room has a higher trainer id than Ghetsis,
        #  which means Ghetsis' Cofagrigus is expected to be what sets the first level
        first_level: dict[str, tuple[int, int]] = {}
        if world.options.adjust_levels.is_wild_by_distance:
            for data in world.wild_encounter.values():
                dist = distances[data.region]
                if data.region not in first_level:
                    lvl, _ = first_level[data.region] = (50 * dist // max_distance, data.max_level)
                else:
                    first, first_orig = first_level[data.region]
                    lvl = first * data.max_level // first_orig
                new_level = max(min(lvl * data.min_level // data.max_level, 100), 1), max(min(lvl, 100), 1)
                if new_level[0] != data.min_level or new_level[1] != data.max_level:
                    data.min_level, data.max_level = new_level
                    data.write |= 1

        if world.options.adjust_levels.is_trainer_by_distance:
            for t_entry in world.trainer_teams:
                t_data = trainer_table[t_entry.trainer_id - 1]
                if t_data.do_not_adjust:
                    continue
                reg_name = t_data.region
                dist = distances[reg_name]
                if reg_name not in first_level:
                    lvl, _ = first_level[reg_name] = (50 * dist // max_distance, t_entry.level)
                else:
                    first, first_orig = first_level[reg_name]
                    lvl = first * t_entry.level // first_orig
                new_level = max(min(lvl + 2, 100), 1)
                if new_level != t_entry.level:
                    t_entry.level = new_level
                    t_entry.write |= 1

    mod_value = world.options.modify_levels.value
    if isinstance(mod_value, dict):
        calcs = [{"type": "Wild", "mode": mod_value["Wild mode"], "value": mod_value["Wild value"]},
                 {"type": "Trainer", "mode": mod_value["Trainer mode"], "value": mod_value["Trainer value"]}]
    else:
        calcs: list[dict[str, int | str]] = mod_value
    calcs = [calc for calc in calcs if ModifyLevels.is_modified(calc["mode"], calc["value"])]
    wild_calcs, trainer_calcs = (tuple(calc for calc in calcs if calc["type"] == "Wild"),
                                 tuple(calc for calc in calcs if calc["type"] == "Trainer"))

    if wild_calcs:
        for data in world.wild_encounter.values():
            new_level = data.min_level, data.max_level
            for calc in wild_calcs:
                new_level = (ModifyLevels.modify(calc["mode"], calc["value"], new_level[0]),
                             ModifyLevels.modify(calc["mode"], calc["value"], new_level[1]))
            if new_level[0] != data.min_level or new_level[1] != data.max_level:
                data.min_level, data.max_level = new_level
                data.write |= 1

    if trainer_calcs:
        for t_entry in world.trainer_teams:
            new_level = t_entry.level
            for calc in trainer_calcs:
                new_level = ModifyLevels.modify(calc["mode"], calc["value"], new_level)
            if new_level != t_entry.level:
                t_entry.level = new_level
                t_entry.write |= 1
