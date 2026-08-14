import zipfile
from typing import TYPE_CHECKING, Any, Literal

from ...ndspy.rom import NintendoDSRom
from ...ndspy.narc import NARC

if TYPE_CHECKING:
    from ...rom import PokemonBWPatch
    from ..text import Entry


def patch(rom: NintendoDSRom, world_package: str, bw_patch_instance: "PokemonBWPatch",
          files_dump: dict[str, bytes | bytearray]) -> None:
    import orjson
    from ...data.text import funny_dialog, efficient_dialog
    from ..text import decode, encode

    data: dict[str, str | Any] = orjson.loads(bw_patch_instance.get_file("text.json"))
    plando: list[tuple[str, str]] = data["plando"]
    narc_system = NARC(rom.getFileByName("a/0/0/2"))
    narc_story = NARC(rom.getFileByName("a/0/0/3"))
    slotdata = orjson.loads(bw_patch_instance.files.get("slot_data.json", b'{}'))

    # funny/efficient dialog
    if data["dialog"] == "funny":
        all_lines: dict[tuple[Literal["system", "story"], int], list[tuple[int, int, str]]] = {}
        for text_data in funny_dialog.table:
            key = (text_data.section, text_data.file)
            value = (text_data.block, text_data.entry, text_data.text)
            if key not in all_lines:
                all_lines[key] = [value]
            else:
                all_lines[key].append(value)
        for key, values in all_lines.items():
            narc = narc_system if key[0] == "system" else narc_story
            text_file = decode(narc.files[key[1]])
            for value in values:
                insert_line(text_file, value[0], value[1], value[2])
            encoded = encode(text_file)
            narc.files[key[1]] = encoded
            files_dump[f"{'a002' if narc == narc_system else 'a003'}/{key[1]}"] = encoded
    elif data["dialog"] == "efficient":
        for key, table in efficient_dialog.table.items():
            narc = narc_system if key[0] == "system" else narc_story
            text_file = decode(narc.files[key[1]])
            for block_num in range(len(table)):
                for line_num, text in table[block_num].items():
                    insert_line(text_file, block_num, line_num, text)
            encoded = encode(text_file)
            narc.files[key[1]] = encoded
            files_dump[f"{'a002' if narc == narc_system else 'a003'}/{key[1]}"] = encoded

    # Plando
    all_lines: dict[tuple[str, int], list[tuple[int, int, str]]] = {}
    for location, text in plando:
        parts = location.split()
        key = (parts[0], int(parts[1]))
        value = (int(parts[2]), int(parts[3]), text)
        if key not in all_lines:
            all_lines[key] = [value]
        else:
            all_lines[key].append(value)
    for key, values in all_lines.items():
        narc = narc_system if key[0] == "system" else narc_story
        text_file = decode(narc.files[key[1]])
        for value in values:
            insert_line(text_file, value[0], value[1], value[2])
        encoded = encode(text_file)
        narc.files[key[1]] = encoded
        files_dump[f"{'a002' if narc == narc_system else 'a003'}/{key[1]}"] = encoded

    # world info NPC
    info41 = "General information about the world:[NextLine]"
    info42 = "Information about encounter[NextLine]randomization:[Scroll][NextLine]"
    info43 = "Information about stats randomization:[NextLine]"
    info44 = "Information about locations and logic:[NextLine]"
    info45 = "Miscellaneous information:[NextLine]"

    if isinstance(slotdata['options']['goal'], list):
        info41 += "- Combined goals:[Scroll][NextLine]"
        for goal in slotdata['options']['goal']:
            info41 += f"-- {goal.replace('_', ' ').capitalize()}[Scroll][NextLine]"
    else:
        info41 += f"- Goal: {slotdata['options']['goal'].replace('_', ' ').capitalize()}[Scroll][NextLine]"
    if slotdata["options"]["plugin_options"]:
        info41 += "- Plugin options found for...[Scroll][NextLine]"
        for domain in slotdata["options"]["plugin_options"]:
            info41 += f"-- {domain}[Scroll][NextLine]"
    else:
        info41 += "- No plugin options found[Scroll][NextLine]"

    if slotdata["options"]["randomize_wild_pokemon"]:
        info42 += "- Wild randomization modifiers:[Scroll][NextLine]"
        for mod in slotdata["options"]["randomize_wild_pokemon"]:
            info42 += f"-- {mod.capitalize()}[Scroll][NextLine]"
    else:
        info42 += "- No wild randomization[Scroll][NextLine]"
    if slotdata["options"]["randomize_trainer_pokemon"]:
        info42 += "- Trainer randomization modifiers:[Scroll][NextLine]"
        for mod in slotdata["options"]["randomize_trainer_pokemon"]:
            info42 += f"-- {mod.capitalize()}[Scroll][NextLine]"
    else:
        info42 += "- No trainer randomization[Scroll][NextLine]"
    if slotdata["options"]["encounter_plando"]:
        if len(slotdata["options"]["encounter_plando"]) == 1:
            info42 += "- One encounter plando entry[Scroll][NextLine]"
        else:
            info42 += f"- {len(slotdata['options']['encounter_plando'])} encounter plando entries[Scroll][NextLine]"
    info42 += (f"- {len(slotdata['options']['wild_randomization_blacklist'])} "
               f"blacklisted wild pokémon[Scroll][NextLine]")
    info42 += (f"- {len(slotdata['options']['trainer_randomization_blacklist'])} "
               f"blacklisted trainer pokémon[Scroll][NextLine]")

    if slotdata["options"]["randomize_base_stats"]:
        info43 += "- Base stats randomization modifiers:[Scroll][NextLine]"
        for mod in slotdata["options"]["randomize_base_stats"]:
            info43 += f"-- {mod.capitalize()}[Scroll][NextLine]"
    else:
        info43 += "- No base stats randomization[Scroll][NextLine]"
    if slotdata["options"]["randomize_evolutions"]:
        info43 += "- Evolution randomization modifiers:[Scroll][NextLine]"
        for mod in slotdata["options"]["randomize_evolutions"]:
            info43 += f"-- {mod.capitalize()}[Scroll][NextLine]"
    else:
        info43 += "- No evolution randomization[Scroll][NextLine]"
    if slotdata["options"]["randomize_catch_rates"]:
        info43 += "- Catch rates randomization modifiers:[Scroll][NextLine]"
        for mod in slotdata["options"]["randomize_catch_rates"]:
            info43 += f"-- {mod.capitalize()}[Scroll][NextLine]"
    else:
        info43 += "- No catch rates randomization[Scroll][NextLine]"
    if slotdata["options"]["randomize_level_up_movesets"]:
        info43 += "- Levelup moveset randomization[Scroll][NextLine]modifiers:[Scroll][NextLine]"
        for mod in slotdata["options"]["randomize_level_up_movesets"]:
            info43 += f"-- {mod.capitalize()}[Scroll][NextLine]"
    else:
        info43 += "- No levelup moveset randomization[Scroll][NextLine]"
    if slotdata["options"]["randomize_types"]:
        info43 += "- Types randomization modifiers:[Scroll][NextLine]"
        for mod in slotdata["options"]["randomize_types"]:
            info43 += f"-- {mod.capitalize()}[Scroll][NextLine]"
    else:
        info43 += "- No types randomization[Scroll][NextLine]"
    if slotdata["options"]["stats_plando"]:
        if len(slotdata["options"]["stats_plando"]) == 1:
            info43 += "- One stats plando entry[Scroll][NextLine]"
        else:
            info43 += f"- {len(slotdata['options']['stats_plando'])} stats plando entries[Scroll][NextLine]"

    info44 += (f"- Shuffle badge rewards: {slotdata['options']['shuffle_badges'].replace('_', ' ').capitalize()}"
               f"[Scroll][NextLine]"
               f"- Shuffle TM rewards: {slotdata['options']['shuffle_tm_hm'].replace('_', ' ').capitalize()}"
               f"[Scroll][NextLine]"
               f"- Season control: {slotdata['options']['season_control'].replace('_', ' ').capitalize()}"
               f"[Scroll][NextLine]")
    if isinstance(slotdata['options']['dexsanity'], list):
        info44 += f"- {len(slotdata['options']['dexsanity'])} fixed Dexsanity checks[Scroll][NextLine]"
    else:
        info44 += f"- {slotdata['options']['dexsanity']} random Dexsanity checks[Scroll][NextLine]"
    if slotdata['options']['dexcountsanity']["Maximum"]:
        info44 += (f"- Dexcountsanity checks with maximum {slotdata['options']['dexcountsanity']['Maximum']}, "
                   f"steps {slotdata['options']['dexcountsanity']['Steps']}, "
                   f"and leniency {slotdata['options']['dexcountsanity']['Leniency']}[Scroll][NextLine]")
    if isinstance(slotdata['options']['shinysanity'], list):
        info44 += f"- {len(slotdata['options']['shinysanity'])} fixed Shinysanity checks[Scroll][NextLine]"
    else:
        info44 += f"- {slotdata['options']['shinysanity']} random Shinysanity checks[Scroll][NextLine]"
    shcosanity = slotdata['options']['shinycountsanity']
    if isinstance(shcosanity, int):
        shcosanity = {"Maximum": shcosanity, "Steps": 1, "Leniency": 0}
    if shcosanity["Maximum"]:
        info44 += (f"- Shinycountsanity checks with maximum {shcosanity['Maximum']}, "
                   f"steps {shcosanity['Steps']}, "
                   f"and leniency {shcosanity['Leniency']}[Scroll][NextLine]")
    if slotdata["options"]["replace_evo_methods"]:
        info44 += "- Replaced evolution methods:[Scroll][NextLine]"
        for mod in slotdata["options"]["replace_evo_methods"]:
            info44 += f"-- {mod.capitalize()}[Scroll][NextLine]"
    if slotdata["options"]["modify_logic"]:
        info44 += "- Logic modifications:[Scroll][NextLine]"
        for mod in slotdata["options"]["modify_logic"]:
            info44 += f"-- {mod.capitalize()}[Scroll][NextLine]"

    if slotdata["options"]["adjust_levels"]:
        info45 += "- Level adjustments:[Scroll][NextLine]"
        for mod in slotdata["options"]["adjust_levels"]:
            info45 += f"-- {mod.capitalize()}[Scroll][NextLine]"
    else:
        info45 += "- No level adjustments[Scroll][NextLine]"
    if isinstance(slotdata["options"]["modify_levels"], dict):
        info45 += "- Level modifications:[Scroll][NextLine]"
        if slotdata["options"]["modify_levels"]["Wild mode"] == 0:
            info45 += f"-- Wild * {slotdata['options']['modify_levels']['Wild value'] / 100}[Scroll][NextLine]"
        elif slotdata["options"]["modify_levels"]["Wild mode"] == 1:
            info45 += f"-- Wild + {slotdata['options']['modify_levels']['Wild value']}[Scroll][NextLine]"
        else:
            info45 += f"-- Wild ^ {slotdata['options']['modify_levels']['Wild value'] / 100}[Scroll][NextLine]"
        if slotdata["options"]["modify_levels"]["Trainer mode"] == 0:
            info45 += f"-- Trainer * {slotdata['options']['modify_levels']['Trainer value'] / 100}[Scroll][NextLine]"
        elif slotdata["options"]["modify_levels"]["Trainer mode"] == 1:
            info45 += f"-- Trainer + {slotdata['options']['modify_levels']['Trainer value']}[Scroll][NextLine]"
        else:
            info45 += f"-- Trainer ^ {slotdata['options']['modify_levels']['Trainer value'] / 100}[Scroll][NextLine]"
    else:
        info45 += "- Advanced level modifications[Scroll][NextLine]"
    if "encounter_rates.json" in bw_patch_instance.files:
        rates = orjson.loads(bw_patch_instance.files["encounter_rates.json"])
        if rates["choice"] != "custom":
            info45 += f"- Encounter rates: {rates['choice'].replace('_', ' ').capitalize()}[Scroll][NextLine]"
        else:
            info45 += "- Custom encounter rates[Scroll][NextLine]"
    else:
        info45 += "- Vanilla encounter rates[Scroll][NextLine]"
    if not slotdata["options"]["master_ball_seller"]:
        info45 += "- No Master Ball seller[Scroll][NextLine]"
    else:
        info45 += "- Master Ball seller modifiers:[Scroll][NextLine]"
        for mod in slotdata["options"]["master_ball_seller"]:
            info45 += f"-- {mod.title()}[Scroll][NextLine]"
        info45 += f"-- Actual cost: {slotdata['master_ball_seller_cost']}[Scroll][NextLine]"
    if slotdata["options"]["funny_dialog"] == "funny":
        info45 += "- Funny dialog[Scroll][NextLine]"
    elif slotdata["options"]["funny_dialog"] == "efficient":
        info45 += "- Efficient dialog[Scroll][NextLine]"
    if slotdata["options"]["text_plando"]:
        if len(slotdata["options"]["text_plando"]) == 1:
            info45 += "- One text plando entry[Scroll][NextLine]"
        else:
            info45 += f"- {len(slotdata['options']['text_plando'])} text plando entries[Scroll][NextLine]"

    info41 += "...[End]"
    info42 += "...[End]"
    info43 += "...[End]"
    info44 += "...[End]"
    info45 += "...[End]"

    text_file = decode(narc_story.files[436])
    insert_line(text_file, 0, 41, info41)
    insert_line(text_file, 0, 42, info42)
    insert_line(text_file, 0, 43, info43)
    insert_line(text_file, 0, 44, info44)
    insert_line(text_file, 0, 45, info45)
    encoded = encode(text_file)
    narc_story.files[436] = encoded
    files_dump["a003/436"] = encoded

    rom.setFileByName("a/0/0/2", narc_system.save())
    rom.setFileByName("a/0/0/3", narc_story.save())


def insert_line(text_file: list[list["Entry"]], block_num: int, line_num: int, text: str) -> None:
    # Assuming all_lines always has at least 1 block
    copy_flags = 0 if len(text_file[0]) == 0 else text_file[0][0].flags
    copy_key = 1 if len(text_file[0]) == 0 else text_file[0][0].key
    while block_num >= len(text_file):
        text_file.append([Entry(flags=copy_flags) for _ in range(len(text_file[0]))])
    while line_num >= len(text_file[0]):
        for block in text_file:
            block.append(Entry(key=copy_key, flags=copy_flags))
    text_file[block_num][line_num].line = text


def write_plando(bw_patch_instance: "PokemonBWPatch", opened_zipfile: zipfile.ZipFile) -> None:
    import orjson

    lines: list[tuple[str, str]] = [
        (line.at, line.text[0])
        for line in bw_patch_instance.world.options.text_plando
        if line.text
    ]
    opened_zipfile.writestr("text.json", orjson.dumps({
        "dialog": bw_patch_instance.world.options.funny_dialog.current_key,
        "plando": lines,
    }))
