import logging
import sys
from typing import Any, TYPE_CHECKING, ClassVar, Callable
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
    from ..data import SpeciesData, ExtendedRule


class PluginProtocol:
    # Hide from the plugin creator
    _initialized: bool
    _ov_table: dict[int, Overlay]
    _ov_arrays: dict[int, bytearray]
    _narcs: dict[str, NARC]
    _rom: NintendoDSRom
    _files_dump: dict[str, bytes | bytearray]
    _options: dict[str, Any]
    _settings: dict[str, Any]
    _arm9: bytearray | None
    _arm7: bytearray | None

    # Relevant to the plugin creator
    slot_data: ClassVar[dict[str, Any]] = {}
    general_options: ClassVar[dict[str, Any]] = {}
    all_plugin_options: ClassVar[dict[str, Any]] = {}
    all_plugin_settings: ClassVar[dict[str, Any]] = {}
    patch_instance: "PokemonBWPatch"
    world: "PokemonBWWorld"
    all_plugins: list

    # Needs to be set by the plugin creator
    name: str
    domain: str
    version: str
    author: str


class OverrideProtocol(PluginProtocol):

    def __init__(self, plugins: list["Plugin"], patch_instance: "PokemonBWPatch" = None, world: "PokemonBWWorld" = None):
        if not hasattr(PluginProtocol, "_initialized") or PluginProtocol._initialized is False:
            PluginProtocol._initialized = True
            PluginProtocol.all_plugin_settings.update(settings.get_settings()["pokemon_bw_settings"]["plugin_settings"])
            if world is None:
                PluginProtocol.slot_data.update(orjson.loads(patch_instance.files.get("slot_data.json", b'{}')))
                PluginProtocol.general_options.update(PluginProtocol.slot_data.get("options", {}))
                PluginProtocol.all_plugin_options.update(PluginProtocol.general_options.get("plugin_options", {}))
            else:
                PluginProtocol.slot_data.update(world.part_slot_data())
                PluginProtocol.general_options.update(PluginProtocol.slot_data["options"])
                PluginProtocol.all_plugin_options.update(PluginProtocol.general_options["plugin_options"])
        options = PluginProtocol.all_plugin_options.get(self.domain, {})
        this_settings = PluginProtocol.all_plugin_settings.get(self.domain, {})
        if isinstance(options, list):
            options = {value: True for value in options}
        elif not isinstance(options, dict):
            options = {}
        if isinstance(this_settings, list):
            this_settings = {value: True for value in this_settings}
        elif not isinstance(this_settings, dict):
            this_settings = {}
        self._options = options
        self._settings = this_settings
        self.all_plugins = plugins
        self.patch_instance = patch_instance
        self.world = world

    def patching_prepare(self, rom: NintendoDSRom, files_dump: dict[str, bytes | bytearray]):
        self._rom = rom
        self._files_dump = files_dump
        self._narcs = {}
        self._ov_table = rom.loadArm9Overlays()
        self._ov_arrays = {}
        self._arm7 = None
        self._arm9 = None

    def patching_done(self):
        for path, narc in self._narcs.items():
            self._rom.setFileByName(path, narc.save())
        for ov_num, ov_data in self._ov_arrays:
            ov = self._ov_table[ov_num]
            ov.data = bytes(ov_data)
            self._rom.files[ov.fileID] = ov.save(compress=ov.compressed)
        self._rom.arm9OverlayTable = saveOverlayTable(self._ov_table)
        if self._arm9 is not None:
            arm9 = bytearray(codeCompression.compress(self._arm9, True))
            arm9[0xfc4:0xfc7] = (len(arm9) + 0x4000).to_bytes(3, "little")
            self._rom.arm9 = bytes(arm9)

    @staticmethod
    def otpp_patch_array(array: bytearray, otp: bytes | bytearray):
        array[:] = otpp.patch(array, otp)

    def get_option(self, name: str, default=None, typ: type = object) -> Any:
        ret = self._options.get(name, default)
        if not isinstance(ret, typ):
            return default
        return ret

    def get_setting(self, name: str, default=None, typ: type = object) -> Any:
        ret = self._settings.get(name, default)
        if not isinstance(ret, typ):
            return default
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

    def get_arm9(self) -> bytearray:
        if self._arm9 is None:
            self._arm9 = bytearray(codeCompression.decompress(self._rom.arm9))
            self._files_dump["arm9"] = self._arm9
        return self._arm9

    def get_arm7(self) -> bytearray:
        if self._arm7 is None:
            self._arm7 = bytearray(self._rom.arm7)
            self._files_dump["arm7"] = self._arm7
        return self._arm7

    @staticmethod
    def modify_rule(old: "ExtendedRule", new: Callable[["ExtendedRule", CollectionState, "PokemonBWWorld"], bool]):
        old_code_function = FunctionType(old.__code__, globals())
        old.__code__ = (lambda state, world: new(old_code_function, state, world)).__code__

    def new_item(self, name: str, classification: ItemClassification | None = None):
        from ..items import PokemonBWItem
        from ..data.items import all_items_dict_view

        data = all_items_dict_view[name]
        return PokemonBWItem(name,
                             classification if classification is not None else data.classification(self.world),
                             data.item_id,
                             self.world.player)


class FillProtocol(PluginProtocol):

    def patch(self):
        ...

    def generate_early(self):
        ...

    def generate_encounter(self):
        ...

    def create_regions(self, catchable_species_data: dict[str, "SpeciesData"]):
        ...

    def create_items(self, item_pool: list["PokemonBWItem"]):
        ...

    def write_patch(self, opened_zipfile: ZipFile):
        ...


class Plugin(OverrideProtocol, FillProtocol):
    pass


def load_plugins(patch_instance: "PokemonBWPatch" = None, world: "PokemonBWWorld" = None) -> list[Plugin]:
    plugins: list[Plugin] = []
    for module_name, module_type in sys.modules.items():
        if not module_name.startswith("worlds.pokemon_bw_"):
            continue
        if hasattr(module_type, "Plugin"):
            if not isinstance(module_type.Plugin, type):
                logging.warning(f"{module_name[7:]}.Plugin is not a class")
            else:
                # for key, value in MergeProtocol.__dict__.items():
                #    if not isinstance(value, Callable):
                #         continue
                #     other_value = getattr(module_type.Plugin, key, None)
                #     if isinstance(other_value, Callable) and value != other_value:
                #         def merged(*args, **kwargs):
                #             value(*args, **kwargs)
                #             other_value(*args, **kwargs)
                #         setattr(module_type.Plugin, key, merged)
                #     else:
                #         setattr(module_type.Plugin, key, value)
                for key, value in OverrideProtocol.__dict__.items():
                    if not isinstance(value, Callable):
                        continue
                    setattr(module_type.Plugin, key, value)
                for key, value in FillProtocol.__dict__.items():
                    if not isinstance(value, Callable) or hasattr(module_type.Plugin, key):
                        continue
                    setattr(module_type.Plugin, key, value)
                for key, value in PluginProtocol.__annotations__:
                    if key not in PluginProtocol.__dict__:
                        continue
                    setattr(module_type.Plugin, key, value)
                plugins.append(module_type.Plugin(plugins, patch_instance, world))
        elif "." not in module_name[7:]:
            logging.warning(f"{module_name[7:]} has the patch plugin naming scheme, "
                            f"but doesn't contain a class named 'Plugin' in __init__.py")
    return plugins
