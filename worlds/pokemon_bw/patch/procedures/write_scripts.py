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

    # ------------------------------------------------------------
    # --- Init script
    # ------------------------------------------------------------

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
    active_shiny_rate = any((opt["shinysanity"], shcosanity["Maximum"],
                             opt["shinyformsanity"], shfocosanity["Maximum"]))
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

    # ------------------------------------------------------------
    # --- Script system
    # ------------------------------------------------------------

    system_scripts = disassemble(narc.files[873])

    if "statics/starters" in bw_patch_instance.files:
        starters_addr = system_scripts.find_label(system_scripts.script_links[1]) + 1
        starters_data = bw_patch_instance.files["statics/starters"]
        writes = {
            0x8012: (starters_data[0:2], True, b'\0\0'),  # (data, is_bytes, default)
            0x8013: (starters_data[3:5], True, b'\0\0'),
            0x8014: (starters_data[6:8], True, b'\0\0'),
            0x8015: (starters_data[8], False, 0),  # Starters are always the same level anyway
        }
        while (line := system_scripts.lines[starters_addr].parts)[0] != "VMReturn":
            starters_addr += 1
            if line[0] != "WorkSetConst":
                continue
            if (p := writes.get(line[1], False)) and p[0] != p[2]:
                line[2] = p[0] if not p[1] else int.from_bytes(p[0], "little")

    if "statics/statics" in bw_patch_instance.files:
        statics_addr = system_scripts.find_label(system_scripts.script_links[4])
        desertresort_addr = system_scripts.find_label(system_scripts.lines[statics_addr + 2].parts[2]) + 1
        mimics6_addr = system_scripts.find_label(system_scripts.lines[statics_addr + 4].parts[2]) + 1
        mimics10_addr = system_scripts.find_label(system_scripts.lines[statics_addr + 6].parts[2]) + 1
        various_addr = system_scripts.find_label(system_scripts.lines[statics_addr + 8].parts[2]) + 1
        statics_data = bw_patch_instance.files["statics/statics"]
        writes = {
            0x8012: (statics_data[0:2], True, b'\0\0'),
            0x8013: (statics_data[4:6], True, b'\0\0'),
            0x8014: (statics_data[8:10], True, b'\0\0'),
            0x8015: (statics_data[12:14], True, b'\0\0'),
            0x8016: (statics_data[16:18], True, b'\0\0'),
            0x8017: (statics_data[2], False, 255),
            0x8018: (statics_data[6], False, 255),
            0x8019: (statics_data[10], False, 255),
            0x801A: (statics_data[14], False, 255),
            0x801B: (statics_data[18], False, 255),
            0x801C: (statics_data[19], False, 0),
        }
        while (line := system_scripts.lines[desertresort_addr].parts)[0] != "VMJump":
            desertresort_addr += 1
            if line[0] != "WorkSetConst":
                continue
            if (p := writes.get(line[1], False)) and p[0] != p[2]:
                line[2] = p[0] if not p[1] else int.from_bytes(p[0], "little")
        writes = {
            0x8012: (statics_data[28:30], True, b'\0\0'),
            0x8013: (statics_data[30], False, 255),
            0x8014: (statics_data[32:34], True, b'\0\0'),
            0x8015: (statics_data[34], False, 255),
            0x8016: (statics_data[35], False, 0),
        }
        while (line := system_scripts.lines[mimics6_addr].parts)[0] != "VMJump":
            mimics6_addr += 1
            if line[0] != "WorkSetConst":
                continue
            if (p := writes.get(line[1], False)) and p[0] != p[2]:
                line[2] = p[0] if not p[1] else int.from_bytes(p[0], "little")
        writes = {
            0x8012: (statics_data[36:38], True, b'\0\0'),
            0x8013: (statics_data[38], False, 255),
            0x8014: (statics_data[40:42], True, b'\0\0'),
            0x8015: (statics_data[42], False, 255),
            0x8016: (statics_data[43], False, 0),
            0x8017: (statics_data[44:46], True, b'\0\0'),
            0x8018: (statics_data[46], False, 255),
            0x8019: (statics_data[48:50], True, b'\0\0'),
            0x801A: (statics_data[50], False, 255),
            0x801B: (statics_data[51], False, 0),
        }
        while (line := system_scripts.lines[mimics10_addr].parts)[0] != "VMJump":
            mimics10_addr += 1
            if line[0] != "WorkSetConst":
                continue
            if (p := writes.get(line[1], False)) and p[0] != p[2]:
                line[2] = p[0] if not p[1] else int.from_bytes(p[0], "little")
        writes = {
            0x8012: (statics_data[20:22], True, b'\0\0'),
            0x8013: (statics_data[22], False, 255),
            0x8014: (statics_data[23], False, 0),
            0x8015: (statics_data[24:26], True, b'\0\0'),
            0x8016: (statics_data[26], False, 255),
            0x8017: (statics_data[27], False, 0),
            0x8018: (statics_data[52:54], True, b'\0\0'),
            0x8019: (statics_data[54], False, 255),
            0x801A: (statics_data[50], False, 0),
        }
        while (line := system_scripts.lines[various_addr].parts)[0] != "VMJump":
            various_addr += 1
            if line[0] != "WorkSetConst":
                continue
            if (p := writes.get(line[1], False)) and p[0] != p[2]:
                line[2] = p[0] if not p[1] else int.from_bytes(p[0], "little")

    if "statics/gifts" in bw_patch_instance.files:
        gifts_addr = system_scripts.find_label(system_scripts.script_links[3])
        dreamyard_gifts_addr = system_scripts.find_label(system_scripts.lines[gifts_addr + 2].parts[2]) + 1
        various_gifts_addr = system_scripts.find_label(system_scripts.lines[gifts_addr + 4].parts[2]) + 1
        gifts_data = bw_patch_instance.files["statics/gifts"]
        writes = {
            0x8016: (gifts_data[8:10], True, b'\0\0'),
            0x8017: (gifts_data[10], False, 255),
            0x8018: (gifts_data[12:14], True, b'\0\0'),
            0x8019: (gifts_data[14], False, 255),
            0x801A: (gifts_data[16:18], True, b'\0\0'),
            0x801B: (gifts_data[18], False, 255),
            0x801C: (gifts_data[19], False, 0),
        }
        while (line := system_scripts.lines[dreamyard_gifts_addr].parts)[0] != "VMJump":
            dreamyard_gifts_addr += 1
            if line[0] != "WorkSetConst":
                continue
            if (p := writes.get(line[1], False)) and p[0] != p[2]:
                line[2] = p[0] if not p[1] else int.from_bytes(p[0], "little")
        writes = {
            0x8012: (gifts_data[0:2], True, b'\0\0'),
            0x8013: (gifts_data[2], False, 255),
            0x8014: (gifts_data[3], False, 0),
            0x8015: (gifts_data[4:6], True, b'\0\0'),
            0x8016: (gifts_data[6], False, 0),
            0x8017: (gifts_data[20:22], True, b'\0\0'),
            0x8018: (gifts_data[22], False, 255),
            0x8019: (gifts_data[23], False, 0),
        }
        while (line := system_scripts.lines[various_gifts_addr].parts)[0] != "VMJump":
            various_gifts_addr += 1
            if line[0] != "WorkSetConst":
                continue
            if (p := writes.get(line[1], False)) and p[0] != p[2]:
                line[2] = p[0] if not p[1] else int.from_bytes(p[0], "little")

    if "statics/fossils" in bw_patch_instance.files:
        fossils_addr = system_scripts.find_label(system_scripts.script_links[5])
        old_fossils_addr = system_scripts.find_label(system_scripts.lines[fossils_addr + 2].parts[2]) + 1
        new_fossils_addr = system_scripts.find_label(system_scripts.lines[fossils_addr + 4].parts[2]) + 1
        gifts_data = bw_patch_instance.files["statics/fossils"]
        writes = {
            0x8012: (gifts_data[0:2], True, b'\0\0'),
            0x8013: (gifts_data[2], False, 255),
            0x8014: (gifts_data[4:6], True, b'\0\0'),
            0x8015: (gifts_data[6], False, 255),
            0x8016: (gifts_data[8:10], True, b'\0\0'),
            0x8017: (gifts_data[10], False, 255),
            0x8018: (gifts_data[12:14], True, b'\0\0'),
            0x8019: (gifts_data[14], False, 255),
            0x801A: (gifts_data[16:18], True, b'\0\0'),
            0x801B: (gifts_data[18], False, 255),
            0x801C: (gifts_data[19], False, 0),
        }
        while (line := system_scripts.lines[old_fossils_addr].parts)[0] != "VMJump":
            old_fossils_addr += 1
            if line[0] != "WorkSetConst":
                continue
            if (p := writes.get(line[1], False)) and p[0] != p[2]:
                line[2] = p[0] if not p[1] else int.from_bytes(p[0], "little")
        writes = {
            0x8012: (gifts_data[20:22], True, b'\0\0'),
            0x8013: (gifts_data[22], False, 255),
            0x8014: (gifts_data[24:26], True, b'\0\0'),
            0x8015: (gifts_data[26], False, 255),
            0x8016: (gifts_data[28:30], True, b'\0\0'),
            0x8017: (gifts_data[30], False, 255),
            0x8018: (gifts_data[32:34], True, b'\0\0'),
            0x8019: (gifts_data[34], False, 255),
            0x801A: (gifts_data[35], False, 0),
        }
        while (line := system_scripts.lines[new_fossils_addr].parts)[0] != "VMJump":
            new_fossils_addr += 1
            if line[0] != "WorkSetConst":
                continue
            if (p := writes.get(line[1], False)) and p[0] != p[2]:
                line[2] = p[0] if not p[1] else int.from_bytes(p[0], "little")

    if "statics/legendaries" in bw_patch_instance.files:
        legends_addr = system_scripts.find_label(system_scripts.script_links[5])
        swords_addr = system_scripts.find_label(system_scripts.lines[legends_addr + 2].parts[2]) + 1
        other_legends_addr = system_scripts.find_label(system_scripts.lines[legends_addr + 4].parts[2]) + 1
        gifts_data = bw_patch_instance.files["statics/legendaries"]
        writes = {
            0x8012: (gifts_data[0:2], True, b'\0\0'),
            0x8013: (gifts_data[2], False, 255),
            0x8014: (gifts_data[3], False, 0),
            0x8015: (gifts_data[4:6], True, b'\0\0'),
            0x8016: (gifts_data[6], False, 255),
            0x8017: (gifts_data[7], False, 0),
            0x8018: (gifts_data[8:10], True, b'\0\0'),
            0x8019: (gifts_data[10], False, 255),
            0x801A: (gifts_data[11], False, 0),
        }
        while (line := system_scripts.lines[swords_addr].parts)[0] != "VMJump":
            swords_addr += 1
            if line[0] != "WorkSetConst":
                continue
            if (p := writes.get(line[1], False)) and p[0] != p[2]:
                line[2] = p[0] if not p[1] else int.from_bytes(p[0], "little")
        writes = {
            0x8012: (gifts_data[12:14], True, b'\0\0'),
            0x8013: (gifts_data[14], False, 255),
            0x8014: (gifts_data[15], False, 0),
            0x8015: (gifts_data[16:18], True, b'\0\0'),
            0x8016: (gifts_data[18], False, 255),
            0x8017: (gifts_data[19], False, 0),
            0x8018: (gifts_data[20:22], True, b'\0\0'),
            0x8019: (gifts_data[22], False, 255),
            0x801A: (gifts_data[23], False, 0),
            0x801B: (gifts_data[24:26], True, b'\0\0'),
            0x801C: (gifts_data[26], False, 255),
            0x801D: (gifts_data[24:26], True, b'\0\0'),
            0x801E: (gifts_data[26], False, 255),
            0x801F: (gifts_data[27], False, 0),
        }
        while (line := system_scripts.lines[other_legends_addr].parts)[0] != "VMJump":
            other_legends_addr += 1
            if line[0] != "WorkSetConst":
                continue
            if (p := writes.get(line[1], False)) and p[0] != p[2]:
                line[2] = p[0] if not p[1] else int.from_bytes(p[0], "little")

    narc.files[873] = bytes(assemble(system_scripts))
    files_dump["a057/873"] = narc.files[873]

    rom.setFileByName("a/0/5/7", narc.save())
