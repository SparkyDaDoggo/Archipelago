from typing import TYPE_CHECKING

import orjson

from ...ndspy.rom import NintendoDSRom
from ...ndspy.narc import NARC

if TYPE_CHECKING:
    from ...rom import PokemonBWPatch


def patch(rom: NintendoDSRom, world_package: str, bw_patch_instance: "PokemonBWPatch",
          files_dump: dict[str, bytes | bytearray]) -> None:
    from ..script_editing import disassemble, assemble, Line
    from ...options import ReusableTMs
    from ...data.pokemon import types, species
    from ...data.items import seasons

    narc = NARC(rom.getFileByName("a/0/5/7"))
    slotdata = orjson.loads(bw_patch_instance.files.get("slot_data.json", b'{}'))
    opt = slotdata["options"]

    init_scripts = disassemble(narc.files[866])
    to_insert = []
    # Sequence0 address
    init_addr = init_scripts.find_label(init_scripts.script_links[0])
    assert init_addr != -1
    # Calling Routine0
    first_command = init_scripts.lines[init_addr+1].parts
    assert first_command[0] == "VMCall"
    # Routine0 address
    r0_addr = init_scripts.find_label(first_command[1])
    assert r0_addr != -1
    # Checking for any FlagSet => probably correct function found
    first_command = init_scripts.lines[r0_addr+1].parts
    assert first_command[0] == "FlagSet"

    to_insert += (
        # TMHM hunt NPC
        # "name **in** goal" works for both single goal strings and combined goals lists
        Line("command", [
            "FlagReset" if "tmhm_hunt" in opt["goal"] else "FlagSet",
            0x192
        ]),
        # Legendary hunt NPC
        Line("command", [
            "FlagReset" if "legendary_hunt" in opt["goal"] else "FlagSet",
            0x1EA
        ]),
    )

    # Master ball sellers
    seller_modifiers = [mod.casefold() for mod in opt["master_ball_seller"]]
    cost = slotdata["master_ball_seller_cost"]
    max_amount = 10 if not cost else (65535 // cost)  # Only implemented 10 in scripts for now
    to_insert += (
        Line("command", ["WorkSetConst", 0x40F2, cost]),
        Line("command", ["WorkSetConst", 0x40FA, max_amount]),
        Line("command", ["FlagSet" if "ns castle" in seller_modifiers else "FlagReset", 0x1CF]),
        Line("command", ["FlagSet" if "pc" in seller_modifiers else "FlagReset", 0x1D1]),
        Line("command", ["FlagSet" if "cherens mom" in seller_modifiers else "FlagReset", 0x1D2]),
        Line("command", ["FlagSet" if "undella mansion seller" in seller_modifiers else "FlagReset", 0x1D0]),
    )

    # Shiny rate activation
    shcosanity, shfocosanity = opt["shinycountsanity"], opt["shinyformcountsanity"]
    if isinstance(shcosanity, int):
        shcosanity = {"Maximum": shcosanity}
    if isinstance(shfocosanity, int):
        shfocosanity = {"Maximum": shfocosanity}
    active_shiny_rate = any((opt["shinysanity"], shcosanity, opt["shinyformsanity"], shfocosanity))
    to_insert += (
        Line("command", ["FlagSet" if active_shiny_rate else "FlagReset", 0x1E8]),
        Line("command", ["WorkSetConst", 0x40F3, 1024 if active_shiny_rate else 8]),
    )

    # Other
    to_insert += (
        # Reusable items dialog
        Line("command", ["WorkSetConst", 0x40F7, ReusableTMs._by_name[opt["reusable_tms"]]]),
        # Studio Castelia check type
        Line("command", ["WorkSetConst", 0x4137, types.by_name[slotdata["studio_castelia_type"]]]),
        # Driftveil check move ID
        Line("command", ["WorkSetConst", 0x413B, slotdata["driftveil_random_move_id"]]),
        # Various checks species ID
        Line("command", ["WorkSetConst", 0x4113, species.by_name[slotdata["other_locations_species"]].dex_number]),
        # Initial exp multiplier
        Line("command", ["WorkSetConst", 0x40F4, opt["exp_multiplier"] - 1]),

        # Initial season and npc vanish
        Line("command", ["FlagSet" if opt["season_control"] == "vanilla" else "FlagReset", 0x193]),
        # Can always be set, because vanilla ignores that variable and changeable always starts with Spring by default
        Line("command", ["WorkSetConst", 0x40C1, seasons.table[slotdata["starting_season"]].var_value]),

        # Relic Castle sand filled room roadblock pokémon and level
        Line("command", ["WorkSetConst", 0x40F8, slotdata["relic_castle_roadblock"][0]]),
        Line("command", ["WorkSetConst", 0x40F9, slotdata["relic_castle_roadblock"][1]]),
    )

    init_scripts.lines[r0_addr+1:r0_addr+1] = to_insert
    narc.files[866] = bytes(assemble(init_scripts))
    files_dump["a057/866"] = narc.files[866]

    rom.setFileByName("a/0/5/7", narc.save())
