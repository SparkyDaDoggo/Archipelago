from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..ndspy.rom import NintendoDSRom


def extract(rom: "NintendoDSRom", target: str) -> None:
    if __name__ == '__main__':
        from ndspy.narc import NARC
        from text import decode
    else:
        from ..ndspy.narc import NARC
        from .text import decode
    with open(target+".story.txt", "wb") as story_f, open(target+".system.txt", "wb") as system_f:
        narc_system = NARC(rom.getFileByName("a/0/0/2"))
        narc_story = NARC(rom.getFileByName("a/0/0/3"))
        for i in range(len(narc_system.files)):
            text = decode(narc_system.files[i])
            system_f.write(f"Text file {i}:\n    ('system', {i}): [".encode())
            for block_num in range(len(text)):
                system_f.write("{\n".encode())
                for line_num in range(len(text[block_num])):
                    try:
                        system_f.write(f"        {line_num}: \"{text[block_num][line_num].line}\"\n".encode())
                    except UnicodeEncodeError:
                        system_f.write(f"        {line_num}: \"{text[block_num][line_num].line}\"\n".encode("utf-16", errors="surrogatepass"))
                system_f.write("    },".encode())
            system_f.write("],\n".encode())
        for i in range(len(narc_story.files)):
            text = decode(narc_story.files[i])
            story_f.write(f"Text file {i}:\n    ('story', {i}): [".encode())
            for block_num in range(len(text)):
                story_f.write("{\n".encode())
                for line_num in range(len(text[block_num])):
                    try:
                        story_f.write(f"        {line_num}: \"{text[block_num][line_num].line}\"\n".encode())
                    except UnicodeEncodeError:
                        story_f.write(f"        {line_num}: \"{text[block_num][line_num].line}\"\n".encode("utf-16", errors="surrogatepass"))
                story_f.write("    },".encode())
            story_f.write("],\n".encode())


if __name__ == '__main__':
    try:
        from ndspy.rom import NintendoDSRom
        from sys import argv
        extract(NintendoDSRom.fromFile(argv[1]), argv[1])
    except Exception as e:
        import traceback
        input(traceback.format_exc())
