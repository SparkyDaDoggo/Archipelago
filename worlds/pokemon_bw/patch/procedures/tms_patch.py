from typing import TYPE_CHECKING

from ...ndspy.rom import NintendoDSRom
from ...ndspy.code import saveOverlayTable

if TYPE_CHECKING:
    from ...rom import PokemonBWPatch


def patch(rom: NintendoDSRom, world_package: str, bw_patch_instance: "PokemonBWPatch",
          files_dump: dict[str, bytes | bytearray]) -> None:
    use_code = b'\x08\xb5\x03\x1c\xfb\xf7\x4e\xfc\x18\x1c\x59\x59\x44\x31\x09\x88\xfb\xf7\x7a\xfc\x08\xbd'
    overlay_table = rom.loadArm9Overlays()
    ov91 = overlay_table[91]
    data = bytearray(ov91.data)
    data[0x8b28:0x8b28+len(use_code)] = use_code
    data[0x1e3e:0x1e3e+4] = b'\x06\xf0\x73\xfe'
    ov91.data = bytes(data)
    rom.files[ov91.fileID] = ov91.save(compress=True)
    files_dump[f"ov91"] = rom.files[ov91.fileID]
    rom.arm9OverlayTable = saveOverlayTable(overlay_table)

