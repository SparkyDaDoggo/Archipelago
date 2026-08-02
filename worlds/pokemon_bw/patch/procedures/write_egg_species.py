import zipfile
from typing import TYPE_CHECKING

from ...ndspy.rom import NintendoDSRom
from ...ndspy.narc import NARC

if TYPE_CHECKING:
    from ...rom import PokemonBWPatch


def write_patch(bw_patch_instance: "PokemonBWPatch", opened_zipfile: zipfile.ZipFile) -> None:
    from ...data.pokemon.species import by_name

    byt = bytearray(667*2)

    for species, data in bw_patch_instance.world.species_entries.items():
        if data.form and not data.is_custom_form:
            continue

        if data.egg_species is not None:
            file = data.custom_form_file or data.dex_number
            byt[file:file+2] = by_name[data.egg_species].dex_number.to_bytes(2, "little")

    opened_zipfile.writestr("egg_species.bin", bytes(byt))


def patch(rom: NintendoDSRom, world_package: str, bw_patch_instance: "PokemonBWPatch",
          files_dump: dict[str, bytes | bytearray]) -> None:

    narc = NARC(rom.getFileByName("a/0/2/0"))
    loaded = bw_patch_instance.files["egg_species.bin"]

    for i in range(0, 667*2, 2):
        new = loaded[i:i+2]
        if new != b'\0\0':
            narc.files[i//2] = new
            files_dump[f"a020/{i//2}"] = new

    rom.setFileByName("a/0/2/0", narc.save())
