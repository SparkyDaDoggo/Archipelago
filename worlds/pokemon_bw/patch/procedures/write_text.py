import zipfile
from typing import TYPE_CHECKING, Any, Literal

from ...ndspy.rom import NintendoDSRom
from ...ndspy.narc import NARC

if TYPE_CHECKING:
    from ...rom import PokemonBWPatch
    from ..text import Entry


def patch(rom: NintendoDSRom, world_package: str, bw_patch_instance: "PokemonBWPatch",
          files_dump: zipfile.ZipFile) -> None:
    import orjson
    from ...data.text import funny_dialog, efficient_dialog
    from ..text import decode, encode

    data: dict[str, str | Any] = orjson.loads(bw_patch_instance.get_file("text.json"))
    plando: list[tuple[str, str]] = data["plando"]
    narc_system = NARC(rom.getFileByName("a/0/0/2"))
    narc_story = NARC(rom.getFileByName("a/0/0/3"))

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
            files_dump.writestr(f"{'a002' if narc == narc_system else 'a003'}/{key[1]}", encoded)
    elif data["dialog"] == "efficient":
        for key, table in efficient_dialog.table.items():
            narc = narc_system if key[0] == "system" else narc_story
            text_file = decode(narc.files[key[1]])
            for block_num in range(len(table)):
                for line_num, text in table[block_num].items():
                    insert_line(text_file, block_num, line_num, text)
            encoded = encode(text_file)
            narc.files[key[1]] = encoded
            files_dump.writestr(f"{'a002' if narc == narc_system else 'a003'}/{key[1]}", encoded)

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
        files_dump.writestr(f"{'a002' if narc == narc_system else 'a003'}/{key[1]}", encoded)

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
