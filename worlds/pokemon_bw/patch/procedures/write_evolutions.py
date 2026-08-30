import zipfile
from typing import TYPE_CHECKING

from ...ndspy.rom import NintendoDSRom
from ...ndspy.narc import NARC

if TYPE_CHECKING:
    from ...rom import PokemonBWPatch


def write_patch(bw_patch_instance: "PokemonBWPatch", opened_zipfile: zipfile.ZipFile) -> None:
    from ...data.pokemon.evolution_methods import methods

    for species, data in bw_patch_instance.world.species_entries.items():
        if data.write & 1 and (not data.form or data.is_custom_form):
            byt = bytes()
            for evo_tup in data.evolutions:  # TODO
                byt += (methods[evo_tup.method].id.to_bytes(2, "little")
                        + evo_tup.value.to_bytes(2, "little")
                        + evo_tup.species.dex_number.to_bytes(2, "little"))
            byt += b'\0' * (42 - len(byt))
            opened_zipfile.writestr(f"evo/{max(data.dex_number, data.custom_form_file)}", bytes(byt))


def patch(rom: NintendoDSRom, world_package: str, bw_patch_instance: "PokemonBWPatch",
          files_dump: dict[str, bytes | bytearray]) -> None:

    narc = NARC(rom.getFileByName("a/0/1/9"))

    for i in range(1, 668):
        if f"evo/{i}" in bw_patch_instance.files:
            narc.files[i] = bw_patch_instance.files[f"evo/{i}"]
            files_dump[f"a019/{i}"] = narc.files[i]

    rom.setFileByName("a/0/1/9", narc.save())
