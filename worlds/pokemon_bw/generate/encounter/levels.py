from typing import TYPE_CHECKING

from ...data import TrainerData
from ...options import ModifyLevels
from ... import EncounterEntry, TrainerPokemonEntry

if TYPE_CHECKING:
    from ... import PokemonBWWorld


def adjust_wild(slot: EncounterEntry, distances: dict[str, int],
                first_level: dict[str, tuple[int, int]], max_distance: int) -> tuple[int, int]:
    dist = distances[slot.region]
    if slot.region not in first_level:
        lvl, _ = first_level[slot.region] = (48 * dist // max_distance, slot.max_level)
    else:
        first, first_orig = first_level[slot.region]
        lvl = first * slot.max_level // first_orig
    return max(min(int(lvl * slot.min_max_fraction) + 2, 100), 1), max(min(lvl + 2, 100), 1)


def adjust_trainer(t_entry: TrainerPokemonEntry, t_data: TrainerData, distances: dict[str, int],
                   first_level: dict[str, tuple[int, int]], max_distance: int) -> int:
    # 52 is what the first pokémon of Ghetsis will get, such that his last pokémon will be 54.
    # furthest distance first level is 50, trainers will get a +2 bonus.
    # N's team in his throne room has a higher trainer id than Ghetsis,
    #  which means Ghetsis' Cofagrigus is expected to be what sets the first level.
    dist = distances[t_data.region]
    if t_data.region not in first_level:
        lvl, _ = first_level[t_data.region] = (47 * dist // max_distance, t_entry.level)
    else:
        first, first_orig = first_level[t_data.region]
        lvl = first * t_entry.level // first_orig
    return max(min(lvl + 5, 100), 1)


def adjust_and_modify(world: "PokemonBWWorld"):
    from ...data.trainers.data import table as trainer_table

    wild_adjust = world.options.adjust_levels.is_wild_by_distance
    trainer_adjust = world.options.adjust_levels.is_trainer_by_distance
    mod_value = world.options.modify_levels.value
    if isinstance(mod_value, dict):
        calcs = [{"type": "Wild", "mode": mod_value["Wild mode"], "value": mod_value["Wild value"]},
                 {"type": "Trainer", "mode": mod_value["Trainer mode"], "value": mod_value["Trainer value"]}]
    else:
        calcs: list[dict[str, int | str]] = mod_value
    calcs = [calc for calc in calcs if ModifyLevels.is_modified(calc["mode"], calc["value"])]
    wild_calcs, trainer_calcs = (tuple(calc for calc in calcs if calc["type"] == "Wild"),
                                 tuple(calc for calc in calcs if calc["type"] == "Trainer"))

    if any((wild_adjust, trainer_adjust, wild_calcs, trainer_calcs)):

        distances = world.region_distances
        max_distance = max(distances.values())

        first_level: dict[str, tuple[int, int]] = {}
        if wild_adjust or wild_calcs:
            for data in world.wild_encounter.values():
                new_level = adjust_wild(data, distances, first_level, max_distance) if wild_adjust else (data.min_level, data.max_level)
                for calc in wild_calcs:
                    new_level = (ModifyLevels.modify(calc["mode"], calc["value"], new_level[0]),
                                 ModifyLevels.modify(calc["mode"], calc["value"], new_level[1]))
                if (data.min_level, data.max_level) != new_level:
                    data.min_level, data.max_level = new_level
                    data.write |= 1

        if trainer_adjust or trainer_calcs:
            for t_entry in world.trainer_teams:
                t_data = trainer_table[t_entry.trainer_id - 1]
                if t_data.do_not_adjust:
                    continue
                new_level = adjust_trainer(t_entry, t_data, distances, first_level, max_distance) if trainer_adjust else t_entry.level
                for calc in trainer_calcs:
                    new_level = ModifyLevels.modify(calc["mode"], calc["value"], new_level)
                if new_level != t_entry.level:
                    t_entry.level = new_level
                    t_entry.write |= 1
