import logging
from typing import TYPE_CHECKING
from zipfile import ZipFile

if TYPE_CHECKING:
    from .. import PokemonBWWorld
    from ..items import PokemonBWItem
    from ..generate import SpeciesEntry


def popup(errors: list[str], hook: str):
    message = (f"Following error{'s' if len(errors) > 1 else ''} appeared during "
               f"running plugins in {hook}:\n")
    message += "".join(("\n" + error) for error in errors)
    try:
        import ctypes
        message += (f"\n\nThe affected plugin{'s' if len(errors) > 1 else ''} might have only partially been applied.\n"
                    "Click OK to continue or CANCEL to abort multiworld generation.")
        if ctypes.windll.user32.MessageBoxW(0, message, "Warning", 1) == 2:
            raise Exception("Multiworld generation was aborted by the user after a plugin threw an error")
        logging.warning(message)
    except ImportError:
        raise Exception(message)


def plugins_generate_early(world: "PokemonBWWorld"):
    plugin_errors = []
    for plugin in world.plugins:
        try:
            plugin.generate_early()
        except Exception as e:
            for arg in e.args:
                plugin_errors.append(f"[{plugin.name}] {arg}")
    if plugin_errors:
        popup(plugin_errors, "generate_early")


def plugins_fill_rules(world: "PokemonBWWorld"):
    plugin_errors = []
    for plugin in world.plugins:
        try:
            plugin.fill_rules()
        except Exception as e:
            for arg in e.args:
                plugin_errors.append(f"[{plugin.name}] {arg}")
    if plugin_errors:
        popup(plugin_errors, "fill_rules")


def plugins_generate_encounters(world: "PokemonBWWorld"):
    plugin_errors = []
    for plugin in world.plugins:
        try:
            plugin.generate_encounter()
        except Exception as e:
            for arg in e.args:
                plugin_errors.append(f"[{plugin.name}] {arg}")
    if plugin_errors:
        popup(plugin_errors, "generate_encounters")


def plugins_create_items_main_only(world: "PokemonBWWorld", item_pool: list["PokemonBWItem"]):
    plugin_errors = []
    for plugin in world.plugins:
        try:
            plugin.create_items_main_only(item_pool)
        except Exception as e:
            for arg in e.args:
                plugin_errors.append(f"[{plugin.name}] {arg}")
    if plugin_errors:
        popup(plugin_errors, "create_items_main_only")


def plugins_create_items(world: "PokemonBWWorld", item_pool: list["PokemonBWItem"]):
    plugin_errors = []
    for plugin in world.plugins:
        try:
            plugin.create_items(item_pool)
        except Exception as e:
            for arg in e.args:
                plugin_errors.append(f"[{plugin.name}] {arg}")
    if plugin_errors:
        popup(plugin_errors, "create_items")


def plugins_create_regions(world: "PokemonBWWorld", catchable_species_data: dict[str, "SpeciesEntry"]):
    plugin_errors = []
    for plugin in world.plugins:
        try:
            plugin.create_regions(catchable_species_data)
        except Exception as e:
            for arg in e.args:
                plugin_errors.append(f"[{plugin.name}] {arg}")
    if plugin_errors:
        popup(plugin_errors, "create_regions")


def plugins_write_patch(world: "PokemonBWWorld", opened_zipfile: ZipFile):
    plugin_errors = []
    for plugin in world.plugins:
        try:
            plugin.write_patch(opened_zipfile)
        except Exception as e:
            for arg in e.args:
                plugin_errors.append(f"[{plugin.name}] {arg}")
    if plugin_errors:
        popup(plugin_errors, "write_patch")
