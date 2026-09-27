import zipfile
from typing import TYPE_CHECKING

from .. import lz11
from ...ndspy.code import saveOverlayTable
from ...ndspy.rom import NintendoDSRom
from ...ndspy.narc import NARC

if TYPE_CHECKING:
    from ...rom import PokemonBWPatch


def write_patch(bw_patch_instance: "PokemonBWPatch", opened_zipfile: zipfile.ZipFile) -> None:
    from ...data.pokemon.types import by_name

    left = bw_patch_instance.world.static_encounter["Left Starter"]
    middle = bw_patch_instance.world.static_encounter["Middle Starter"]
    right = bw_patch_instance.world.static_encounter["Right Starter"]
    data = bytearray(12)
    if left.write & 0b1:
        data[0:2] = left.species_id[0].to_bytes(2, "little")
    if left.write & 0b10:
        data[2] = left.level
    if middle.write & 0b1:
        data[3:5] = middle.species_id[0].to_bytes(2, "little")
    if middle.write & 0b10:
        data[5] = middle.level
    if right.write & 0b1:
        data[6:8] = right.species_id[0].to_bytes(2, "little")
    if right.write & 0b10:
        data[8] = right.level
    data[9] = by_name[bw_patch_instance.world.species_entries_by_id[left.species_id].types[0]]
    data[10] = by_name[bw_patch_instance.world.species_entries_by_id[middle.species_id].types[0]]
    data[11] = by_name[bw_patch_instance.world.species_entries_by_id[right.species_id].types[0]]

    opened_zipfile.writestr("statics/starters", bytes(data))


def patch(rom: NintendoDSRom, world_package: str, bw_patch_instance: "PokemonBWPatch",
          files_dump: dict[str, bytes | bytearray]) -> None:

    dest_narc = NARC(rom.getFileByName("a/2/0/5"))
    src_narc = NARC(rom.getFileByName("a/0/0/4"))
    starters_data = bw_patch_instance.files.get("statics/starters", b'\0' * 12)
    left = int.from_bytes(starters_data[0:2], "little")
    middle = int.from_bytes(starters_data[3:5], "little")
    right = int.from_bytes(starters_data[6:8], "little")

    files_dump["a205/0"] = dest_narc.files[0] = src_narc.files[left * 20 + 18]
    files_dump["a205/2"] = dest_narc.files[2] = src_narc.files[middle * 20 + 18]
    files_dump["a205/4"] = dest_narc.files[4] = src_narc.files[right * 20 + 18]
    files_dump["a205/12"] = dest_narc.files[12] = lz11.decomp(src_narc.files[left * 20], 0)
    files_dump["a205/13"] = dest_narc.files[13] = lz11.decomp(src_narc.files[middle * 20], 0)
    files_dump["a205/14"] = dest_narc.files[14] = lz11.decomp(src_narc.files[right * 20], 0)

    rom.setFileByName("a/2/0/5", dest_narc.save())

    overlay_table = rom.loadArm9Overlays()
    ov223 = overlay_table[223]
    ov223_data = bytearray(ov223.data)

    ov223_data[0x3170:0x3172] = starters_data[0:2]
    ov223_data[0x3172:0x3174] = starters_data[3:5]
    ov223_data[0x3174:0x3176] = starters_data[6:8]

    ov223.data = bytes(ov223_data)
    rom.files[ov223.fileID] = ov223.save(compress=True)
    files_dump["ov223"] = rom.files[ov223.fileID]
    rom.arm9OverlayTable = saveOverlayTable(overlay_table)
