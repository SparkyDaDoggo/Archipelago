import zipfile
from typing import TYPE_CHECKING

from ...ndspy.rom import NintendoDSRom
from ...ndspy.narc import NARC
from ...options import ModifyLevels

if TYPE_CHECKING:
    from ...rom import PokemonBWPatch


def write_patch(bw_patch_instance: "PokemonBWPatch", opened_zipfile: zipfile.ZipFile) -> None:
    from ...generate.encounter.levels import adjust_wild

    # regarding sphere scaling
    mods = bw_patch_instance.world.options.adjust_levels
    adjust_sphere = mods.is_wild_by_sphere
    tolerance = max((
        0 if mods.is_tolerance_0 else -1,
        20 if mods.is_tolerance_20 else -1,
        50 if mods.is_tolerance_50 else -1,
        100 if mods.is_tolerance_100 else -1,
    ))
    tolerance = 20 if tolerance == -1 else tolerance
    all_distances = bw_patch_instance.world.__class__.distances_by_sphere
    first_level: dict[str, tuple[int, int]] = {}
    if adjust_sphere and not all_distances:
        bw_patch_instance.world.calculate_distances_by_sphere()
    distances = all_distances[bw_patch_instance.world.player]
    max_distance = bw_patch_instance.world.__class__.max_distance_by_sphere

    # regarding modify levels
    mod_value = bw_patch_instance.world.options.modify_levels.value
    if isinstance(mod_value, dict):
        calcs = [{"type": "Wild", "mode": mod_value["Wild mode"], "value": mod_value["Wild value"]},
                 {"type": "Trainer", "mode": mod_value["Trainer mode"], "value": mod_value["Trainer value"]}]
    else:
        calcs: list[dict[str, int | str]] = mod_value
    calcs = [calc for calc in calcs if ModifyLevels.is_modified(calc["mode"], calc["value"])]
    wild_calcs = tuple(calc for calc in calcs if calc["type"] == "Wild")

    slots: list[list[bytearray]] = [
        [bytearray(56*4), bytearray(56*4), bytearray(56*4), bytearray(56*4)]
        for _ in range(112)
    ]

    for file, slot in bw_patch_instance.world.wild_encounter.items():
        new_levels = adjust_wild(slot, distances, first_level, max_distance) if adjust_sphere else (slot.min_level, slot.max_level)
        for calc in wild_calcs:
            new_levels = (ModifyLevels.modify(calc["mode"], calc["value"], new_levels[0]),
                          ModifyLevels.modify(calc["mode"], calc["value"], new_levels[1]))
        new_levels = (max(new_levels[0], slot.min_level * (100 - tolerance) // 100, 1),
                      max(new_levels[1], slot.max_level * (100 - tolerance) // 100, 1))
        if (slot.min_level, slot.max_level) != new_levels:
            slot.min_level, slot.max_level = new_levels
            slot.write |= 1
        arr = slots[file[0]][file[1]]
        # write species if changed
        if slot.write & 2:
            species = slot.species_id
            value = (species[0] + (species[1] * 2048)).to_bytes(2, "little")
            arr[file[2]*4:file[2]*4+2] = value
        # write levels if changed
        if slot.write & 1:
            arr[file[2]*4+2] = slot.min_level
            arr[file[2]*4+3] = slot.max_level

    for file_num in range(112):
        if any(slots[file_num][3]):
            data = slots[file_num][0] + slots[file_num][1] + slots[file_num][2] + slots[file_num][3]
        elif any(slots[file_num][2]):
            data = slots[file_num][0] + slots[file_num][1] + slots[file_num][2]
        elif any(slots[file_num][1]):
            data = slots[file_num][0] + slots[file_num][1]
        elif any(slots[file_num][0]):
            data = slots[file_num][0]
        else:
            data = bytearray(0)
        opened_zipfile.writestr(f"wild/{file_num}", bytes(data))


def patch(rom: NintendoDSRom, world_package: str, bw_patch_instance: "PokemonBWPatch",
          files_dump: dict[str, bytes | bytearray]) -> None:
    from ...data.locations.encounters.areas import map_to_area

    narc = NARC(rom.getFileByName("a/1/2/6"))
    narc_areas = NARC(rom.getFileByName("a/1/7/8"))
    pokemon_areas: list[tuple[bytearray, ...]] = [
        (bytearray(0x3e), bytearray(0x3e), bytearray(0x3e), bytearray(0x3e)) for _ in range(649)
    ]
    area_flags = (1, ) * 12 + (2, ) * 12 + (4, ) * 12 + (8, ) * 5 + (0x10, ) * 5 + (0x20, ) * 5 + (0x40, ) * 5

    for file_num in range(112):

        game_file = bytearray(narc.files[file_num])
        patch_file = bw_patch_instance.get_file(f"wild/{file_num}")
        season_count_game = len(game_file) // (56 * 4 + 8)
        season_count_patch = len(patch_file) // (56 * 4)
        if season_count_patch > season_count_game:
            raise Exception(f"Patch file has more seasons than game file: file {file_num}, "
                            f"{season_count_game} game season, {season_count_patch} patch seasons")

        for season in range(season_count_patch):
            for slot in range(56):
                game_address = (season * (56 * 4 + 8) + 8) + (slot * 4)
                patch_address = (season * 56 * 4) + (slot * 4)
                slot_data: bytes = patch_file[patch_address:patch_address+4]
                if any(slot_data[:2]):
                    game_file[game_address:game_address+2] = slot_data[:2]
                if any(slot_data[2:]):
                    game_file[game_address+2:game_address+4] = slot_data[2:]

        for season in range(season_count_game):
            for slot in range(56):
                game_address = (season * (56 * 4 + 8) + 8) + (slot * 4)
                dex_num = (game_file[game_address] + game_file[game_address+1] * 256) % 2048
                if dex_num:
                    for season_2 in (range(4) if season_count_game == 1 else (season, )):
                        pokemon_areas[dex_num-1][season_2][map_to_area[file_num]] |= area_flags[slot]

        narc.files[file_num] = bytes(game_file)
        files_dump[f"a126/{file_num}"] = bytes(game_file)

    for file_num in range(649):
        for season_array in pokemon_areas[file_num]:
            if not any(season_array):
                season_array[0] = 1
        narc_areas.files[file_num] = b'\1' + b''.join(pokemon_areas[file_num])
        files_dump[f"a178/{file_num}"] = narc_areas.files[file_num]

    rom.setFileByName("a/1/2/6", narc.save())
    rom.setFileByName("a/1/7/8", narc_areas.save())
