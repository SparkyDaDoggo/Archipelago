import zipfile
from typing import TYPE_CHECKING

from ...ndspy.code import saveOverlayTable
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

    overlay_table = rom.loadArm9Overlays()
    ov21 = overlay_table[21]
    data = bytearray(ov21.data)
    if any(loaded[29*2:30*2]) or any(loaded[32*2:35*2]):
        data[0x3ba1c:0x3ba1c+4] = b'\0\0\0\0'  # Nidoran
    if any(loaded[313*2:315*2]):
        data[0x3ba24:0x3ba24+4] = b'\0\0\0\0'  # Volbeat/Illumise
    if any(loaded[489*2:490*2]):
        data[0x3ba2c:0x3ba2c+4] = b'\0\0\0\0'  # Manaphy/Phione
    if any(index in loaded for index in (b'\x2a\x01', b'\x68\x01', b'\xb7\x01', b'\xb6\x01', b'\xbe\x01',
                                         b'\xca\x01', b'\x96\x01', b'\xb8\x01', b'\xb1\x01')):
        data[0x3ba34:0x3ba34+4] = b'\0\0\0\0'  # Baby stages
    if any(loaded[422*2:424*2]):
        data[0x3ba44:0x3ba44+4] = b'\0\0\0\0'  # Shellos/Gastrodon
    if any(loaded[412*2:414*2]):
        data[0x3ba4c:0x3ba4c+4] = b'\0\0\0\0'  # Burmy/Wormadam
    if any(loaded[550*2:551*2]):
        data[0x3ba54:0x3ba54+4] = b'\0\0\0\0'  # Basculin
    ov21.data = bytes(data)
    rom.files[ov21.fileID] = ov21.save(compress=True)
    files_dump[f"ov21"] = rom.files[ov21.fileID]
    rom.arm9OverlayTable = saveOverlayTable(overlay_table)
