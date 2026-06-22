import string


class Entry:
    line: str = "[Terminate]"
    key: int = 1
    flags: int = 0

    def __init__(self, line="[Terminate]", key=1, flags=0):
        super().__init__()
        self.line = line
        self.key = key
        self.flags = flags


def decode(data: bytes) -> list[list[Entry]]:

    pointer = [0]

    def read(a: int) -> int:
        pointer[0] += a
        return int.from_bytes(data[pointer[0]-a:pointer[0]], "little")

    def seek(a: int) -> None:
        pointer[0] = a

    numblocks = read(2)
    numentries = read(2)
    blocksizesum = read(4)
    zero = read(4)

    blockoffsets = [0 for _ in range(numblocks)]
    tableoffsets = [[0 for _ in range(numentries)] for _ in range(numblocks)]
    charcounts = [[0 for _ in range(numentries)] for _ in range(numblocks)]
    texts = [[Entry() for _ in range(numentries)] for _ in range(numblocks)]

    for i in range(numblocks):
        blockoffsets[i] = read(4)
    for i in range(numblocks):
        seek(blockoffsets[i])
        blocksize = read(4)
        for j in range(numentries):
            tableoffsets[i][j] = read(4)
            charcounts[i][j] = read(2)
            texts[i][j].flags = read(2)
        for j in range(numentries):
            encchars = []
            decchars = []
            st = texts[i][j]
            seek(blockoffsets[i] + tableoffsets[i][j])
            for k in range(charcounts[i][j]):
                encchars.append(read(2))
            st.key = encchars[-1] ^ 0xFFFF
            while len(encchars):
                decchars.insert(0, encchars.pop() ^ st.key)
                st.key = ((st.key >> 3) | (st.key << 13)) & 0xFFFF
            k = 0
            while k < len(decchars):
                char = decchars[k]
                if char == 0xFFFF:
                    st.line += "[Terminate]"
                elif char == 0xFFFE:
                    st.line += "[NextLine]"  # \n in CTRMap
                elif char == 0xF000:
                    k += 1
                    command = decchars[k]
                    k += 1
                    total = decchars[k]
                    if command == 0xBE01 and total == 0:
                        st.line += f"[End]"  # \c in CTRMap
                    elif command == 0xBE00 and total == 0:
                        st.line += f"[Scroll]"  # \r in CTRMap
                    else:
                        st.line += f"[c_{command:x}_#{total}"
                        for _ in range(total):
                            k += 1
                            st.line += f"_{decchars[k]}"
                        st.line += "]"
                elif 20 < char <= 0xFFF0 and char != 0xF000:
                    st.line += chr(char)
                else:
                    st.line += f"[{hex(char)}]"
                k += 1
            if st.line.endswith("[Terminate]"):
                st.line = st.line[:-11]

    return texts


def encode(texts: list[list[Entry]]) -> bytes:

    # Format:
    # numblocks: 2, numentries: 2, blocksizesum: 4, zero: 4, blockoffsets: 4*numblocks
    # in every block:
    #   blocksize: 4, (offset: 4, charcount: 2, flags: 2)*numentries, (chars: x)*numentries

    data = bytearray()
    blocksizesum = 0

    data += len(texts).to_bytes(2, "little")
    numentries = max(len(entries) for entries in texts)
    for entries in texts:
        if len(entries) != numentries:
            raise Exception(f"Unequal count of entries in different text blocks: max {numentries}, found {len(entries)}")
    data += numentries.to_bytes(2, "little")
    data += b'\0\0\0\0\0\0\0\0'  # blocksizesum

    for i in range(len(texts)):
        data += b'\0\0\0\0'  # blockoffset
    for i in range(len(texts)):
        blockoffset = len(data)
        data[4*i+12:4*i+16] = blockoffset.to_bytes(4, "little")
        data += b'\0\0\0\0'  # blocksize
        for j in range(len(texts[i])):
            entry = texts[i][j]
            data += b'\0\0\0\0'  # tableoffset
            data += b'\0\0'  # charcount
            data += entry.flags.to_bytes(2, "little")
        for j in range(len(texts[i])):
            tableoffset = len(data)-blockoffset
            data[8*j+blockoffset+4:8*j+blockoffset+8] = tableoffset.to_bytes(4, "little")
            entry = texts[i][j]
            decchars: list[int] = []  # ordered from first to last char
            k = 0
            while k < len(entry.line):
                char = entry.line[k]
                if char != "[":
                    if char == "]":
                        raise Exception(f"Extra closing bracket: "+entry.line[:k+1])
                    unicode = ord(char)
                    if unicode > 0xffff:
                        raise Exception(f"Unicode character cannot be written to text file: {char} ({hex(unicode)})")
                    decchars.append(unicode)
                    k += 1
                else:
                    if k + 10 < len(entry.line) and entry.line[k:k+11] == "[Terminate]":
                        decchars.append(0xffff)
                        k += 11
                    elif k + 9 < len(entry.line) and entry.line[k:k+10] == "[NextLine]":
                        decchars.append(0xfffe)
                        k += 10
                    elif k + 4 < len(entry.line) and entry.line[k:k+5] == "[End]":
                        decchars.extend([0xf000, 0xbe01, 0])
                        k += 5
                    elif k + 7 < len(entry.line) and entry.line[k:k+8] == "[Scroll]":
                        decchars.extend([0xf000, 0xbe00, 0])
                        k += 8
                    elif k + 4 < len(entry.line) and entry.line[k:k+3] == "[0x":
                        end = entry.line.find("]", k)
                        if end == -1:
                            raise Exception("Unclosed raw value: "+entry.line[k:])
                        raw = int(entry.line[k+1:end], 16)
                        if raw > 0xffff:
                            raise Exception("Unsupported raw number: "+entry.line[k+1:end])
                        decchars.append(raw)
                        k = end + 1
                    elif k + 2 < len(entry.line) and entry.line[k:k+3] == "[c_":
                        end = entry.line.find("]", k)
                        if end == -1:
                            raise Exception("Unclosed command: "+entry.line[k:])
                        parts = entry.line[k+1:end].split("_")
                        if len(parts) < 3:
                            raise Exception("Incomplete command: "+entry.line[k+1:end])
                        if parts[2][0] != "#":
                            raise Exception("Bad command formatting: "+entry.line[k+1:end])
                        if int(parts[2][1:]) != len(parts) - 3:
                            raise Exception("Incorrect value count for command: "+entry.line[k+1:end])
                        decchars.extend([int(parts[1], 16), int(parts[2][1:])])
                        decchars.extend(int(part) for part in parts[3:])
                        k = end + 1
                    else:
                        end = entry.line.find("]", k)
                        raise Exception("Bad special characters: "+(entry.line[k+1:end] if end != -1 else entry.line[k+1]))
            if decchars[-1] != 0xffff:
                decchars.append(0xffff)
            encchars: list[int] = []
            key = entry.key
            for decoded in decchars:
                key = ((key << 3) & 0xffff) | (key >> 13)
                encchars.append(decoded ^ key)
            for encoded in encchars:
                data += encoded.to_bytes(2, "little")
            data[8*j+blockoffset+8:8*j+blockoffset+10] = len(encchars).to_bytes(2, "little")  # charcount
        blocksize = len(data) - blockoffset
        blocksizesum += blocksize
        data[blockoffset:blockoffset+4] = blocksize.to_bytes(4, "little")  # blocksize
    data[4:8] = blocksizesum.to_bytes(4, "little")

    return data


def is_bad_text(line: str) -> str:
    k = 0
    while k < len(line):
        char = line[k]
        if char == "]":
            return "Extra closing bracket"
        if char == "[":
            if k + 10 < len(line) and line[k:k+11] == "[Terminate]":
                k += 11
                if k == len(line):
                    return ""
                return "[Terminate] before end of line"
            elif k + 9 < len(line) and line[k:k + 10] == "[NextLine]":
                k += 10
            elif k + 4 < len(line) and line[k:k+5] == "[End]":
                k += 5
            elif k + 7 < len(line) and line[k:k+8] == "[Scroll]":
                k += 8
            elif k + 4 < len(line) and line[k:k+3] == "[0x":
                end = line.find("]", k)
                if end == -1:
                    return "Missing closing bracket"
                if not line[k+3:end].isnumeric():
                    return "Non-numeric raw value"
                if int(line[k+1:end]) > 0xffff:
                    return "Raw value too big"
                k = end + 1
            elif k + 2 < len(line) and line[k:k+3] == "[c_":
                end = line.find("]", k)
                if end == -1:
                    return "Missing closing bracket"
                parts = line[k+1:end].split("_")
                if len(parts) < 3:
                    return "Incomplete command"
                if parts[2][0] != "#":
                    return "Missing # at command param count"
                if not parts[2][1:].isnumeric():
                    return "Non-numeric command param count"
                if int(parts[2][1:]) != len(parts) - 3:
                    return "Incorrect command param count"
                if not all(c in string.hexdigits for c in parts[1]):
                    return "Command is not a hexadecimal number"
                for part in parts[3:]:
                    if not part.isnumeric():
                        return "Non-numeric command param"
                k = end + 1
        else:
            k += 1
    return "Line ended without [Terminate]"
