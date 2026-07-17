import zipfile
from typing import TYPE_CHECKING

from ...ndspy.rom import NintendoDSRom
from ...ndspy.narc import NARC

if TYPE_CHECKING:
    from ...rom import PokemonBWPatch


def write_patch(bw_patch_instance: "PokemonBWPatch", opened_zipfile: zipfile.ZipFile) -> None:
    from ...data.pokemon.types import by_name
    from ...data.pokemon.moves import tm_hm

    for species, data in bw_patch_instance.world.species_entries.items():
        if data.form and not data.is_custom_form:
            continue
        byt = bytearray(24)

        if data.write & 0b100:
            byt[:6] = (data.base_hp, data.base_attack, data.base_defense,
                       data.base_speed, data.base_sp_attack, data.base_sp_defense)

        if data.write & 0b1:
            byt[6] = data.evolution_stage

        if data.write & 0b1000:
            byt[7] = data.catch_rate

        if data.write & 0b100000:
            byt[8] = by_name[data.type_1]
            byt[9] = by_name[data.type_2]
        else:
            byt[8] = 0xff
            byt[9] = 0xff

        if data.write & 0b1000000:
            flags = 0
            for tm in data.tm_hm_moves.tm_hm_moves:
                flags |= 1 << tm_hm[tm].index
            byt[10:23] = flags.to_bytes(13, "little")
        else:
            byt[22] = 0x80

        if data.write & 0b10000000:
            byt[23] = data.exp_curve
        else:
            byt[23] = 0xff

        if data.write & 0b11101101:
            opened_zipfile.writestr(f"stats/{max(data.dex_number, data.custom_form_file)}", bytes(byt))


def patch(rom: NintendoDSRom, world_package: str, bw_patch_instance: "PokemonBWPatch",
          files_dump: dict[str, bytes | bytearray]) -> None:

    narc = NARC(rom.getFileByName("a/0/1/6"))

    for i in range(1, 668):
        if f"stats/{i}" in bw_patch_instance.files:
            byt = bytearray(narc.files[i])
            loaded = bw_patch_instance.files[f"stats/{i}"]

            for j in range(6):
                byt[j] = loaded[j] or byt[j]
            byt[9] = loaded[6] or byt[9]
            byt[8] = loaded[7] or byt[8]
            byt[6] = loaded[8] if loaded[8] != 0xff else byt[6]
            byt[7] = loaded[9] if loaded[9] != 0xff else byt[7]
            if not loaded[22] & 0x80:
                byt[0x28:0x35] = loaded[10:23]
            byt[21] = loaded[23] if loaded[23] != 0xff else byt[21]

            narc.files[i] = bytes(byt)
            files_dump[f"a016/{i}"] = narc.files[i]

    rom.setFileByName("a/0/1/6", narc.save())
