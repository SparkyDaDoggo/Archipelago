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
    from . import load_plugins

    plugins = load_plugins(patch_instance=patch_instance)

    plugin_errors = []
    for plugin in plugins:
        try:
            plugin.patching_prepare(rom, files_dump)
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
    for plugin in plugins:
        try:
            plugin.patching_done()
        except Exception as e:
            for arg in e.args:
                plugin_errors.append(f"[{plugin.name}] {arg}")
    if plugin_errors:
        popup(plugin_errors, "patch plugin finalization")
