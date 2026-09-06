import zipfile
from typing import TYPE_CHECKING

from ...ndspy.rom import NintendoDSRom
from ...ndspy.narc import NARC

if TYPE_CHECKING:
    from ...rom import PokemonBWPatch


def write_species(bw_patch_instance: "PokemonBWPatch", opened_zipfile: zipfile.ZipFile) -> None:
    from ...data.pokemon.species import by_name
    from ...data.trainers.data import table as trainer_table

    adjust_sphere = bw_patch_instance.world.options.adjust_levels.is_trainer_by_sphere
    all_distances = bw_patch_instance.world.__class__.distances_by_sphere
    first_level: dict[str, tuple[int, int]] = {}
    if adjust_sphere and not all_distances:
        bw_patch_instance.world.calculate_distances_by_sphere()
    distances = all_distances[bw_patch_instance.world.player]
    max_distance = bw_patch_instance.world.__class__.max_distance_by_sphere

    slots: list[bytearray] = [
        bytearray(6*4)
        for _ in range(616)
    ]

    for pokemon in bw_patch_instance.world.trainer_teams:
        if not pokemon.write:
            continue
        # adjust by sphere if enabled
        if adjust_sphere:
            # see generate/encounter/levels.py for an explanation
            t_data = trainer_table[pokemon.trainer_id - 1]
            if t_data.do_not_adjust:
                continue
            reg_name = t_data.region
            dist = distances[reg_name]
            if reg_name not in first_level:
                lvl, _ = first_level[reg_name] = (50 * dist // max_distance, pokemon.level)
            else:
                first, first_orig = first_level[reg_name]
                lvl = first * pokemon.level // first_orig
            # ... * 4 // 5 in order to allow a little bit of lowering the level, level 0 is prevented by min(lvl + 2, 100)
            new_level = max(min(lvl + 2, 100), pokemon.level * 4 // 5 + 1)
            if new_level != pokemon.level:
                pokemon.level = new_level
                pokemon.write |= 1
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
