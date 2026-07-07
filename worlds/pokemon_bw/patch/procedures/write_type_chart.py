import zipfile
from typing import TYPE_CHECKING

from ...ndspy.rom import NintendoDSRom
from ...ndspy.code import saveOverlayTable

if TYPE_CHECKING:
    from ...rom import PokemonBWPatch


def write_patch(bw_patch_instance: "PokemonBWPatch", opened_zipfile: zipfile.ZipFile) -> None:
    from ...data.pokemon.types import by_name as types_by_name

    byt = bytearray(len(bw_patch_instance.world.type_chart))
    for types, effect in bw_patch_instance.world.type_chart.items():
        byt[types_by_name[types[0]] * len(types_by_name) + types_by_name[types[1]]] = effect

    opened_zipfile.writestr("type_chart.bin", byt)


def patch(rom: NintendoDSRom, world_package: str, bw_patch_instance: "PokemonBWPatch",
          files_dump: dict[str, bytes | bytearray]) -> None:
    loaded = bw_patch_instance.files["type_chart.bin"]
    overlay_table = rom.loadArm9Overlays()
    ov93 = overlay_table[93]
    data = bytearray(ov93.data)
    for i in range(len(loaded)):
        if loaded[i] != 0xff:
            data[0x3a37c+i] = loaded[i]
    ov93.data = bytes(data)
    rom.files[ov93.fileID] = ov93.save(compress=True)
    files_dump[f"ov93"] = rom.files[ov93.fileID]
    rom.arm9OverlayTable = saveOverlayTable(overlay_table)
