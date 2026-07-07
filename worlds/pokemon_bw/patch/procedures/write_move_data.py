import zipfile
from typing import TYPE_CHECKING

from ...ndspy.rom import NintendoDSRom
from ...ndspy.narc import NARC

if TYPE_CHECKING:
    from ...rom import PokemonBWPatch


def write_patch(bw_patch_instance: "PokemonBWPatch", opened_zipfile: zipfile.ZipFile) -> None:
    from ...data.pokemon.types import by_name as types_by_name

    category = {"Status": 0, "Physical": 1, "Special": 2}

    for move, data in bw_patch_instance.world.move_entries.items():
        if data.write & 1:
            byt = bytes((types_by_name[data.type],
                         category[data.category],
                         data.power,
                         data.accuracy,
                         data.pp))
            opened_zipfile.writestr(f"move_data/{data.id}", byt)


def patch(rom: NintendoDSRom, world_package: str, bw_patch_instance: "PokemonBWPatch",
          files_dump: dict[str, bytes | bytearray]) -> None:

    narc = NARC(rom.getFileByName("a/0/2/1"))

    for i in range(1, 560):
        if f"move_data/{i}" in bw_patch_instance.files:
            byt = bytearray(narc.files[i])
            loaded = bw_patch_instance.files[f"move_data/{i}"]

            byt[0] = loaded[0]
            byt[2:6] = loaded[1:5]

            narc.files[i] = bytes(byt)
            files_dump[f"a021/{i}"] = narc.files[i]

    rom.setFileByName("a/0/2/1", narc.save())
