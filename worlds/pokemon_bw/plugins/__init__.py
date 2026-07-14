import logging
import sys
from random import Random
from typing import Any, TYPE_CHECKING, Callable
from zipfile import ZipFile
from types import FunctionType

from orjson import orjson

import settings
from BaseClasses import CollectionState, ItemClassification
from ..ndspy import codeCompression
from ..ndspy.code import Overlay, saveOverlayTable
from ..ndspy.rom import NintendoDSRom
from ..ndspy.narc import NARC
from ..patch import otpp

if TYPE_CHECKING:
    from ..rom import PokemonBWPatch
    from .. import PokemonBWWorld
    from ..items import PokemonBWItem
    from ..data import SpeciesData, ExtendedRule, AccessRule
    from BaseClasses import CollectionRule
    ModifiedExtendedRule = Callable[["AccessRule", CollectionState, "PokemonBWWorld"], bool]

try:
    from ._dev import DEV
except ImportError:
    DEV = False


all_plugin_classes: list[type] | None = None


class PluginProtocol:
    """Initialized fields are written to all imported Plugin classes"""

    # Relevant to the plugin creator
    slot_data: dict[str, Any]
    general_options: dict[str, Any]
    all_plugin_options: dict[str, Any]
    all_plugin_settings: dict[str, Any]
    patch_instance: "PokemonBWPatch"
    world: "PokemonBWWorld"
    all_plugins: list
    random: Random
    arm9: bytearray
    arm7: bytearray

    # Hide from the plugin creator
    _initialized: bool
    _ov_table: dict[int, Overlay]
    _ov_arrays: dict[int, bytearray]
    _narcs: dict[str, NARC]
    _rom: NintendoDSRom
    _files_dump: dict[str, bytes | bytearray]
    _options: dict[str, Any]
    _settings: dict[str, Any]
    _arm9: bytearray  # For backwards compatibility
    _arm7: bytearray  # For backwards compatibility

    # Needs to be set by the plugin creator
    name: str
    domain: str
    version: str
    author: str


class OverrideProtocol(PluginProtocol):
    """Methods will be written into the imported Plugin classes, potentially overriding user-defined methods"""

    def __init__(self, plugins: list["Plugin"], patch_instance: "PokemonBWPatch" = None, world: "PokemonBWWorld" = None):
        if plugins:
            self.all_plugin_settings = plugins[0].all_plugin_settings
            self._settings = plugins[0]._settings
            self.slot_data = plugins[0].slot_data
            self.general_options = plugins[0].general_options
            self.all_plugin_options = plugins[0].all_plugin_options
        else:
            self.all_plugin_settings = settings.get_settings()["pokemon_bw_settings"]["plugin_settings"].copy()
            self._settings = self.all_plugin_settings.get(self.domain, {})
            if isinstance(self._settings, list):
                self._settings = {value: True for value in self._settings}
            elif not isinstance(self._settings, dict):
                self._settings = {}
            else:
                self._settings = self._settings.copy()
            if world is None:
                self.slot_data = orjson.loads(patch_instance.files.get("slot_data.json", b'{}'))
                self.general_options = self.slot_data.get("options", {})
                self.all_plugin_options = self.general_options.get("plugin_options", {})
            else:
                self.slot_data = world.part_slot_data()
                self.general_options = self.slot_data["options"]
                self.all_plugin_options = self.general_options["plugin_options"]
        self._options = self.all_plugin_options.get(self.domain, {})
        if isinstance(self._options, list):
            self._options = {value: True for value in self._options}
        elif not isinstance(self._options, dict):
            self._options = {}
        else:
            self._options = self._options.copy()
        self.all_plugins = plugins
        self.patch_instance = patch_instance
        self.world = world
        self.random = Random(self.slot_data["seed"])

    def patching_prepare(self, rom: NintendoDSRom, files_dump: dict[str, bytes | bytearray], common_narcs: dict,
                         common_ov_table: dict, common_ov_arrays: dict, common_arm7: bytearray, common_arm9: bytearray):
        self._rom = rom
        self._files_dump = files_dump
        self._narcs = common_narcs
        self._ov_table = common_ov_table
        self._ov_arrays = common_ov_arrays
        self.arm7 = self._arm7 = common_arm7  # For backwards compatibility
        self.arm9 = self._arm9 = common_arm9  # For backwards compatibility

    @staticmethod
    def otpp_patch_array(array: bytearray, otp: bytes | bytearray):
        array[:] = otpp.patch(array, otp)

    def get_option(self, name: str, default=None, typ: type = object, support_weighting=True) -> Any:
        ret = self._options.get(name, default)
        if not isinstance(ret, typ):
            return default
        if support_weighting and isinstance(ret, dict) and typ.__hash__ is not None:
            ret2 = {r: rr for r, rr in ret.items() if isinstance(rr, int) and isinstance(r, typ)}
            if not len(ret2):
                return default
            self._options[name] = self.random.choices(tuple(ret2.keys()), tuple(ret2.values()))[0]
            return self._options[name]
        if support_weighting and isinstance(ret, list) and typ.__hash__ is not None:
            ret2 = [r for r in ret if isinstance(r, typ)]
            if not len(ret2):
                return default
            self._options[name] = self.random.choice(ret2)
            return self._options[name]
        return ret

    def get_setting(self, name: str, default=None, typ: type = object, support_weighting=True) -> Any:
        ret = self._settings.get(name, default)
        if not isinstance(ret, typ):
            return default
        if support_weighting and typ.__hash__ is not None and isinstance(ret, dict):
            ret2 = {r: rr for r, rr in ret.items() if isinstance(rr, int) and isinstance(r, typ)}
            if not len(ret2):
                return default
            self._settings[name] = self.random.choices(tuple(ret2.keys()), tuple(ret2.values()))[0]
            return self._settings[name]
        if support_weighting and typ.__hash__ is not None and isinstance(ret, list):
            ret2 = [r for r in ret if isinstance(r, typ)]
            if not len(ret2):
                return default
            self._settings[name] = self.random.choice(ret2)
            return self._settings[name]
        return ret

    def get_from_narc(self, path: str, file_num: int) -> bytearray:
        narc: NARC
        file: bytearray | bytes
        if path not in self._narcs:
            self._narcs[path] = narc = NARC(self._rom.getFileByName(path))
        else:
            narc = self._narcs[path]
        if not isinstance(narc.files[file_num], bytearray):
            narc.files[file_num] = file = bytearray(narc.files[file_num])
        else:
            file = narc.files[file_num]
        self._files_dump[path.replace("/", "") + f"/{file_num}"] = file
        return file

    def get_overlay(self, ov_num: int) -> bytearray:
        ov: bytearray
        if ov_num not in self._ov_arrays:
            self._ov_arrays[ov_num] = ov = bytearray(self._ov_table[ov_num].data)
        else:
            ov = self._ov_arrays[ov_num]
        self._files_dump[f"ov{ov_num}"] = ov
        return ov

    def get_arm9(self) -> bytearray:  # For backwards compatibility
        return self.arm9

    def get_arm7(self) -> bytearray:  # For backwards compatibility
        return self.arm7

    @staticmethod
    def modify_rule(old: "ExtendedRule", new: "ModifiedExtendedRule"):
        if not getattr(old, "_is_modified", False):
            from ..data.locations.rules import _g
            old_code_function = FunctionType(old.__code__, _g)
            def wrapper(state: CollectionState, world: "PokemonBWWorld", _old: "ExtendedRule",
                        _new: tuple["ModifiedExtendedRule", ...]):
                current = _old
                for __new in _new:
                    current = getattr(__new, "__get__")(current)
                return current(state, world)
            old.__code__ = wrapper.__code__
            old._is_modified = True
            old.__defaults__ = (None, None, old_code_function, (new, ))
        else:
            old.__defaults__ = (None, None, old.__defaults__[2], old.__defaults__[3] + (new, ))

    def modify_local_rule(self, old: "ExtendedRule", new: "ModifiedExtendedRule", apply_combined=True):
        assert self.world.rules_dict is not None, "Trying to modify local rules before being initialized"
        if old in self.world.rules_dict:
            old_acc = self.world.rules_dict[old]
            self.world.rules_dict[old] = lambda state: new(old_acc, state, self.world)
        else:
            self.world.rules_dict[old] = lambda state: new(old, state, self.world)
        if apply_combined:
            def mod(_old: "AccessRule") -> "AccessRule":
                return lambda state: new(_old, state, self.world)
            for rules in tuple(self.world.rules_dict):
                if isinstance(rules, tuple) and old in rules:
                    self.world.rules_dict[rules] = mod(self.world.rules_dict[rules])

    def new_item(self, name: str, classification: ItemClassification = None) -> "PokemonBWItem":
        from ..items import PokemonBWItem
        from ..data.items import all_items_dict_view

        data = all_items_dict_view[name]
        return PokemonBWItem(name,
                             classification if classification is not None else data.classification(self.world),
                             data.item_id,
                             self.world.player)

    def new_event(self, location: str, item: str, region: str, *,
                  collection_rule: "CollectionRule" = None, extended_rule: "ExtendedRule" = None) -> None:
        from ..locations import PokemonBWLocation
        from ..items import PokemonBWItem

        region = self.world.regions[region]
        location = PokemonBWLocation(self.world.player, location, None, region)
        location.place_locked_item(PokemonBWItem(item, ItemClassification.progression, None, self.world.player))
        if collection_rule is not None and extended_rule is not None:
            raise Exception(f"Event [({region}) {location}: {item}] defined both a collection rule and an "
                            f"extended rule, which is not allowed")
        elif collection_rule is not None:
            location.access_rule = collection_rule
        elif extended_rule is not None:
            location.access_rule = lambda state: extended_rule(state, self.world)
        region.locations.append(location)

    @staticmethod
    def replace_filler(item_pool: list["PokemonBWItem"], *items: "PokemonBWItem"):
        items_index = 0
        for i in range(len(item_pool)):
            item = item_pool[i]
            if item.classification == ItemClassification.filler:
                item_pool[i] = items[items_index]
                items_index += 1
                if items_index >= len(items):
                    return
        else:
            raise Exception(f"Could not find {len(items)-items_index} more filler item(s) to be replaced by "
                            f"{', '.join(it.name for it in items)}")


class FillProtocol(PluginProtocol):
    """Methods will only be written to the imported Plugin classes if they don't exist there yet"""

    def patch(self): ...

    @classmethod
    def stage_init(cls): ...

    def generate_early(self): ...

    def fill_rules(self): ...

    def generate_encounter(self): ...

    def create_regions(self, catchable_species_data: dict[str, "SpeciesData"]): ...

    def create_items_main_only(self, item_pool: list["PokemonBWItem"]): ...

    def create_items(self, item_pool: list["PokemonBWItem"]): ...

    def write_patch(self, opened_zipfile: ZipFile): ...


class Plugin(OverrideProtocol, FillProtocol):
    pass


def patching_done(rom: NintendoDSRom, common_narcs: dict, common_ov_table: dict, common_ov_arrays: dict,
                  common_arm7: bytearray, common_arm9: bytearray):
    for path, narc in common_narcs.items():
        rom.setFileByName(path, narc.save())
    for ov_num, ov_data in common_ov_arrays.items():
        ov = common_ov_table[ov_num]
        ov.data = bytes(ov_data)
        rom.files[ov.fileID] = ov.save(compress=ov.compressed)
    rom.arm9OverlayTable = saveOverlayTable(common_ov_table)
    arm9 = bytearray(codeCompression.compress(common_arm9, True))
    arm9[0xfc4:0xfc7] = (len(arm9) + 0x4000).to_bytes(3, "little")
    rom.arm9 = bytes(arm9)
    rom.arm7 = bytes(common_arm7)


def load_plugins(patch_instance: "PokemonBWPatch" = None, world: "PokemonBWWorld" = None) -> list[Plugin]:
    global all_plugin_classes
    if all_plugin_classes is None:
        all_plugin_classes = []
        for module_name, module_type in sys.modules.items():
            if not module_name.startswith("worlds.pokemon_bw_"):
                continue
            if hasattr(module_type, "Plugin"):
                if not isinstance(module_type.Plugin, type):
                    logging.warning(f"{module_name[7:]}.Plugin is not a class")
                else:
                    if DEV and not hasattr(module_type.Plugin, "_allow_dev"):
                        continue
                    logging.info(f"Plugin {module_name[7:]} loaded")
                    for key, value in OverrideProtocol.__dict__.items():
                        if not isinstance(value, Callable | classmethod):
                            continue
                        setattr(module_type.Plugin, key, value)
                    for key, value in FillProtocol.__dict__.items():
                        if not isinstance(value, Callable | classmethod) or hasattr(module_type.Plugin, key):
                            continue
                        setattr(module_type.Plugin, key, value)
                    getattr(module_type.Plugin, "stage_init")()
                    all_plugin_classes.append(module_type.Plugin)
            elif "." not in module_name[7:]:
                logging.warning(f"{module_name[7:]} has the plugin naming scheme, "
                                f"but doesn't contain a class named 'Plugin' in __init__.py")
    plugins: list[Plugin] = []
    for plugin_class in all_plugin_classes:
        plugins.append(plugin_class(plugins, patch_instance, world))
    return plugins
