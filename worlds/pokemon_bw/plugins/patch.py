import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..rom import PokemonBWPatch
    from ..ndspy.rom import NintendoDSRom


def popup(errors: list[str], step: str):
    message = f"Following error{'s' if len(errors) > 1 else ''} appeared during {step}:\n"
    message += "".join(("\n" + error) for error in errors)
    try:
        import ctypes
        message += (f"\n\nThe affected plugin{'s' if len(errors) > 1 else ''} might have only partially been applied.\n"
                    "Click OK to continue or CANCEL to abort patching.")
        if ctypes.windll.user32.MessageBoxW(0, message, "Warning", 1) == 2:
            raise Exception("Patching was aborted by the user after a plugin threw an error")
        logging.warning(message)
    except ImportError:
        raise Exception(message)


def plugins_patch(patch_instance: "PokemonBWPatch", rom: "NintendoDSRom", files_dump: dict[str, bytes | bytearray]):
    from . import load_plugins, patching_done
    from ..ndspy.code import codeCompression

    plugins = load_plugins(patch_instance=patch_instance)
    narcs, ov_arrays = {}, {}
    ov_table = rom.loadArm9Overlays()
    arm7 = bytearray(rom.arm7)
    arm9 = bytearray(codeCompression.decompress(rom.arm9))
    files_dump["arm7"] = arm7
    files_dump["arm9"] = arm9

    plugin_errors = []
    for plugin in plugins:
        try:
            plugin.patching_prepare(rom, files_dump, narcs, ov_table, ov_arrays, arm7, arm9)
        except Exception as e:
            for arg in e.args:
                plugin_errors.append(f"[{plugin.name}] {arg}")
    if plugin_errors:
        popup(plugin_errors, "patch plugin preparing")

    plugin_errors = []
    for plugin in plugins:
        try:
            plugin.patch()
        except Exception as e:
            for arg in e.args:
                plugin_errors.append(f"[{plugin.name}] {arg}")
    if plugin_errors:
        popup(plugin_errors, "patch plugin processing")

    plugin_errors = []
    try:
        patching_done(rom, narcs, ov_table, ov_arrays, arm7, arm9)
    except Exception as e:
        for arg in e.args:
            plugin_errors.append(str(arg))
    if plugin_errors:
        popup(plugin_errors, "patch plugin finalization")
