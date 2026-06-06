import zipfile
from typing import TYPE_CHECKING

from ...ndspy.rom import NintendoDSRom
from ...ndspy.narc import NARC

if TYPE_CHECKING:
    from ...rom import PokemonBWPatch


def write_patch(bw_patch_instance: "PokemonBWPatch", opened_zipfile: zipfile.ZipFile) -> None:

    for species, data in bw_patch_instance.world.species_entries.items():
        if data.form and not data.is_custom_form:
            continue
        byt = bytearray(8)
        if data.write & 0b100:
            byt[:6] = (data.base_hp, data.base_attack, data.base_defense,
                       data.base_speed, data.base_sp_attack, data.base_sp_defense)
        if data.write & 0b1:
            byt[6] = data.evolution_stage
        if data.write & 0b1000:
            byt[7] = data.catch_rate
        if data.write & 0b101:
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
            byt[9] = byt[6] or byt[9]
            byt[8] = byt[7] or byt[8]

            narc.files[i] = bytes(byt)
            files_dump[f"a016/{i}"] = narc.files[i]

    rom.setFileByName("a/0/1/6", narc.save())
