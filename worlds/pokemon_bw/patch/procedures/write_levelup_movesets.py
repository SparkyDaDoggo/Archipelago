import zipfile
from typing import TYPE_CHECKING

from ...ndspy.rom import NintendoDSRom
from ...ndspy.narc import NARC

if TYPE_CHECKING:
    from ...rom import PokemonBWPatch


def write_patch(bw_patch_instance: "PokemonBWPatch", opened_zipfile: zipfile.ZipFile) -> None:
    from ...data.pokemon.moves import by_name

    for species, data in bw_patch_instance.world.species_entries.items():
        if data.form and not data.is_custom_form:
            continue
        if not data.write & 0b10000:
            continue
        byt = bytearray()
        for tup in data.level_up_moves.level_up_moves:
            byt += by_name[tup[1]].id.to_bytes(2, "little")
            byt += tup[0].to_bytes(2, "little")
        byt += b'\xff\xff\xff\xff'
        opened_zipfile.writestr(f"levelup_moves/{max(data.dex_number, data.custom_form_file)}", bytes(byt))


def patch(rom: NintendoDSRom, world_package: str, bw_patch_instance: "PokemonBWPatch",
          files_dump: dict[str, bytes | bytearray]) -> None:

    narc = NARC(rom.getFileByName("a/0/1/8"))

    for i in range(1, 668):
        if f"levelup_moves/{i}" in bw_patch_instance.files:
            narc.files[i] = bw_patch_instance.files[f"levelup_moves/{i}"]
            files_dump[f"a018/{i}"] = narc.files[i]

    rom.setFileByName("a/0/1/8", narc.save())
