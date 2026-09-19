import zipfile
from typing import TYPE_CHECKING

from ...ndspy.rom import NintendoDSRom
from ...ndspy.narc import NARC
from ...options import ModifyLevels

if TYPE_CHECKING:
    from ...rom import PokemonBWPatch


def write_species(bw_patch_instance: "PokemonBWPatch", opened_zipfile: zipfile.ZipFile) -> None:
    from ...data.pokemon.species import by_name
    from ...data.trainers.data import table as trainer_table
    from ...generate.encounter.levels import adjust_trainer

    # regarding sphere scaling
    mods = bw_patch_instance.world.options.adjust_levels
    adjust_sphere = mods.is_trainer_by_sphere
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
    distances = all_distances.get(bw_patch_instance.world.player, {})
    max_distance = bw_patch_instance.world.__class__.max_distance_by_sphere

    # regarding modify levels
    mod_value = bw_patch_instance.world.options.modify_levels.value
    if isinstance(mod_value, dict):
        calcs = [{"type": "Wild", "mode": mod_value["Wild mode"], "value": mod_value["Wild value"]},
                 {"type": "Trainer", "mode": mod_value["Trainer mode"], "value": mod_value["Trainer value"]}]
    else:
        calcs: list[dict[str, int | str]] = mod_value
    calcs = [calc for calc in calcs if ModifyLevels.is_modified(calc["mode"], calc["value"])]
    trainer_calcs = tuple(calc for calc in calcs if calc["type"] == "Trainer")

    slots: list[bytearray] = [
        bytearray(6*4)
        for _ in range(616)
    ]

    for pokemon in bw_patch_instance.world.trainer_teams:
        t_data = trainer_table[pokemon.trainer_id - 1]
        if t_data.do_not_adjust:
            continue
        new_level = adjust_trainer(pokemon, t_data, distances, first_level, max_distance) if adjust_sphere else pokemon.level
        for calc in trainer_calcs:
            new_level = ModifyLevels.modify(calc["mode"], calc["value"], new_level)
        new_level = max(new_level, pokemon.level * (100 - tolerance) // 100, 1)
        if new_level != pokemon.level:
            pokemon.level = new_level
            pokemon.write |= 1
        if not pokemon.write:
            continue
        address = 4 * pokemon.team_number
        species_data = by_name[pokemon.species]
        # write species if changed
        if pokemon.write & 2:
            slots[pokemon.trainer_id][address:address+2] = species_data.dex_number.to_bytes(2, "little")
            slots[pokemon.trainer_id][address+2] = species_data.form
        # write level if changed
        if pokemon.write & 1:
            slots[pokemon.trainer_id][address+3] = pokemon.level

    for file in range(1, 616):
        data = bytes(slots[file])
        while data[-4:] == b'\0\0\0\0':
            data = data[:-4]
        opened_zipfile.writestr(f"trainer/{file}_pokemon", data)


def patch_species(rom: NintendoDSRom, world_package: str, bw_patch_instance: "PokemonBWPatch",
                  files_dump: dict[str, bytes | bytearray]) -> None:

    trainer_narc = NARC(rom.getFileByName("a/0/9/2"))
    pokemon_narc = NARC(rom.getFileByName("a/0/9/3"))

    for file_num in range(1, 616):

        trainer_file = bytearray(trainer_narc.files[file_num])
        pokemon_file = bytearray(pokemon_narc.files[file_num])
        patch_file = bw_patch_instance.get_file(f"trainer/{file_num}_pokemon")
        unique_moves = trainer_file[0] % 2 == 1
        held_items = trainer_file[0] >= 2
        entry_length = 8 + (8 if unique_moves else 0) + (2 if held_items else 0)
        remove_unique_moves = False

        for team_slot in range(len(patch_file)//4):

            patch_address = team_slot * 4
            file_address = team_slot * entry_length + 4
            if any(patch_file[patch_address:patch_address+3]):
                pokemon_file[file_address:file_address+3] = patch_file[patch_address:patch_address+3]
                if unique_moves:
                    remove_unique_moves = True
            if patch_file[patch_address+3]:
                pokemon_file[file_address-2] = patch_file[patch_address+3]

        if remove_unique_moves:
            trainer_file[0] &= 254
            trainer_narc.files[file_num] = bytes(trainer_file)
            files_dump[f"a092/{file_num}"] = bytes(trainer_file)
            new_pokemon_file = b''
            for team_slot in range(len(pokemon_file)//entry_length):
                file_address = team_slot * entry_length
                new_pokemon_file += pokemon_file[file_address:file_address+entry_length-8]
            pokemon_narc.files[file_num] = bytes(new_pokemon_file)
        else:
            pokemon_narc.files[file_num] = bytes(pokemon_file)
        files_dump[f"a093/{file_num}"] = pokemon_narc.files[file_num]

    rom.setFileByName("a/0/9/2", trainer_narc.save())
    rom.setFileByName("a/0/9/3", pokemon_narc.save())
