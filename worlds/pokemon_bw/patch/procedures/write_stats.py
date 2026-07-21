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

        byt = bytearray(data.write.to_bytes(2, "little"))

        if data.write & 0b1:
            byt.append(data.evolution_stage)
        if data.write & 0b100:
            byt.extend(data.base_stats)
        if data.write & 0b1000:
            byt.append(data.catch_rate)
        if data.write & 0b100000:
            byt.append(by_name[data.types[0]])
            byt.append(by_name[data.types[1]])
        if data.write & 0b1000000:
            flags = 0
            for tm in data.tm_hm_moves.tm_hm_moves:
                flags |= 1 << tm_hm[tm].index
            byt.extend(flags.to_bytes(13, "little"))
        if data.write & 0b10000000:
            byt.append(data.exp_curve)

        if data.write & 0b11101101:
            opened_zipfile.writestr(f"stats/{max(data.dex_number, data.custom_form_file)}", bytes(byt))


def patch(rom: NintendoDSRom, world_package: str, bw_patch_instance: "PokemonBWPatch",
          files_dump: dict[str, bytes | bytearray]) -> None:

    narc = NARC(rom.getFileByName("a/0/1/6"))
    loaded: bytes

    def read_one() -> int:
        nonlocal loaded
        _val = loaded[0]
        loaded = loaded[1:]
        return _val

    def read(_count: int) -> bytes:
        nonlocal loaded
        _val = loaded[:_count]
        loaded = loaded[_count:]
        return _val

    for i in range(1, 668):
        if f"stats/{i}" in bw_patch_instance.files:
            byt = bytearray(narc.files[i])
            loaded = bw_patch_instance.files[f"stats/{i}"]

            flags = int.from_bytes(read(2), "little")
            if flags & 0b1:
                byt[9] = read_one()
            if flags & 0b100:
                for j in range(6):
                    byt[j] = read_one() or byt[j]
            if flags & 0b1000:
                byt[8] = read_one()
            if flags & 0b100000:
                byt[6] = read_one()
                byt[7] = read_one()
            if flags & 0b1000000:
                byt[0x28:0x35] = read(13)
            if flags & 0b10000000:
                byt[21] = read_one()

            narc.files[i] = bytes(byt)
            files_dump[f"a016/{i}"] = narc.files[i]

    rom.setFileByName("a/0/1/6", narc.save())
