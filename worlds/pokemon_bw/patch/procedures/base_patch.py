import io
from typing import TYPE_CHECKING
from zipfile import ZipFile

from ...ndspy import codeCompression
from ...ndspy.code import saveOverlayTable
from ...ndspy.rom import NintendoDSRom
from ...ndspy.narc import NARC
import pkgutil

from .. import otpp

if TYPE_CHECKING:
    from ...rom import PokemonBWPatch


def patch(rom: NintendoDSRom, world_package: str, bw_patch_instance: "PokemonBWPatch",
          files_dump: dict[str, bytes | bytearray]) -> None:
    from ...data import version

    player_name = bw_patch_instance.player_name.encode()
    if len(player_name) > 32:
        # player name is too long for available space in the rom's header, so make user put in manually instead
        player_name = b''
    pad = rom.pad088[:0x15] + bytes(version.rom()) + player_name
    rom.pad088 = pad + bytes(0x38 - len(pad))

    # open patch files zip and create dict of patch procedures
    base_otpp_zip = pkgutil.get_data(world_package, "patch/base_otpp.zip")
    buffer = io.BytesIO(base_otpp_zip)
    procedures: dict[str, list[tuple[int, bytes]]] = {}
    with ZipFile(buffer, "r") as opened_zip:
        # go through all patch files
        for zip_info in opened_zip.filelist:
            filename = zip_info.filename
            # only data/a files are handled for now
            if "data" in filename:
                if not zip_info.is_dir():
                    # get strings and indexes
                    filename_path_list = filename.split("/")
                    narc_filename = "/".join(filename_path_list[1:-1])  # remove "data" and in-narc index
                    narc_index = int(filename_path_list[-1])
                    # add procedure to dict
                    if narc_filename not in procedures:
                        procedures[narc_filename] = [(narc_index, opened_zip.read(filename))]
                    else:
                        procedures[narc_filename].append((narc_index, opened_zip.read(filename)))
            else:
                raise Exception(f"Base patch file not in data subfolder: {filename}")
    # apply patches to each narc
    for narc_filename, proc_list in procedures.items():
        # load correct narc
        source_narc = NARC(rom.getFileByName(narc_filename))
        # apply each patch to corresponding file inside narc
        for proc in proc_list:
            source_narc.files[proc[0]] = otpp.patch(source_narc.files[proc[0]], proc[1])
        # write patched narc to rom
        rom.setFileByName(narc_filename, source_narc.save())

    # ###########################################################################
    # Unpack overlays and arm9/arm7
    # ###########################################################################
    overlay_table = rom.loadArm9Overlays()
    arm9 = bytearray(codeCompression.decompress(rom.arm9))
    arm7 = bytearray(rom.arm7)

    # Apply forgettable HMs patch
    # arm9[0x1d310] = 0

    # Shiny rate branch
    if rom.name[8:9] == b'W':
        arm9[0x13f0c:0x13f14] = b'\x00\xb5\x92\xf3\x77\xf8\x00\xbd'
    else:
        arm9[0x13ef0:0x13ef8] = b'\x00\xb5\x92\xf3\x75\xf8\x00\xbd'

    # Enable missing auto fly flags
    ov10 = overlay_table[10]
    ov10_data = bytearray(ov10.data)
    ov10_data[0x1beca] = 3  # Nacrene City
    ov10_data[0x1bef2] = 3  # Nimbasa City
    ov10_data[0x1bf06] = 3  # Driftveil City
    ov10_data[0x1bf42] = 3  # Opelucid City
    ov10.data = bytes(ov10_data)
    rom.files[ov10.fileID] = ov10.save(compress=True)
    files_dump["ov10"] = rom.files[ov10.fileID]

    # Apply portable AP menu
    ov21 = overlay_table[21]
    ov21_data = bytearray(ov21.data)
    ov21_data[0x241e:0x241e+4] = b'\x1f\xf2\x6f\xfe'
    ov21_data[0x1eda:0x1eda+4] = b'\x20\xf2\x19\xf9'
    ov21.data = bytes(ov21_data)
    rom.files[ov21.fileID] = ov21.save(compress=True)
    files_dump["ov21"] = rom.files[ov21.fileID]

    # Gracidea without event flag
    ov91 = overlay_table[91]
    ov91_data = bytearray(ov91.data)
    ov91_data[0x7ac0:0x7ac0+2] = b'\x02\xe0'
    ov91.data = bytes(ov91_data)
    rom.files[ov91.fileID] = ov91.save(compress=True)
    files_dump["ov91"] = rom.files[ov91.fileID]

    # Apply Exp multiplier patch
    exp_code = (b'\x05\x49\x09\x68\x03\x48\x09\x5a\x7e\x43\xa8\x59\x01\x31'
                b'\x48\x43\xa8\x51\x70\x47\xa4\x0b\x02\x00\x24\x00\x00\x02')
    ov93 = overlay_table[93]
    ov93_data = bytearray(ov93.data)
    ov93_data[0x1542c:0x1542c+4] = b'\x28\xf0\xea\xfa'
    ov93_data[0x3da04:0x3da04+len(exp_code)] = exp_code
    ov93.data = bytes(ov93_data)
    rom.files[ov93.fileID] = ov93.save(compress=True)
    files_dump["ov93"] = rom.files[ov93.fileID]

    # arm7 expansion, tailored to white version
    expansion = bytearray(pkgutil.get_data(world_package, "patch/arm7_expansion.bin"))
    if rom.name[8:9] != b'W':  # Fix portable AP menu branch links to arm9 for black version
        expansion[0x24] = 0x6c
        expansion[0x34] = 0x64
    arm7.extend(bytes((0x2a000 if rom.name[8:9] == b'W' else 0x29fe0) - len(rom.arm7)))
    arm7.extend(expansion)

    # ###########################################################################
    # Repack overlays and arm9/arm7
    # ###########################################################################
    rom.arm9OverlayTable = saveOverlayTable(overlay_table)
    arm9 = bytearray(codeCompression.compress(arm9, True))
    arm9[0xfc4:0xfc7] = (len(arm9) + 0x4000).to_bytes(3, "little")
    rom.arm9 = bytes(arm9)
    rom.arm7 = bytes(arm7)
    files_dump["arm9"] = rom.arm9
    files_dump["arm7"] = rom.arm7
