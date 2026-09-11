from enum import Enum
from typing import Literal
from dataclasses import dataclass

from .script_actions import actions_table
from .script_commands import commands_table


class ByteType(Enum):
    UNKNOWN = 0
    IGNORE = 1
    RAW = 2
    COMMAND_HEADER = 3
    COMMAND_TAIL = 4
    ACTION_HEADER = 5
    ACTION_TAIL = 6


@dataclass
class Line:
    type: Literal["command", "raw", "action", "label", "comment"]
    parts: list[str | int]


@dataclass
class ScriptFile:
    script_links: dict[int, str]
    stop_bytes: bool
    lines: list[Line]

    def find_label(self, label: str) -> int:
        """Returns the position of the label (not the code!) in self.lines."""
        for i in range(len(self.lines)):
            if self.lines[i].type == "label" and self.lines[i].parts[0] == label:
                return i
        return -1


def disassemble(data: bytes | bytearray) -> ScriptFile:
    script_file = ScriptFile({}, True, [])
    pointer = 0
    scripts = []
    while data[pointer:pointer+2] != b'\x13\xfd':
        if pointer in scripts:
            break
        scr_addr = 4 + pointer + int.from_bytes(data[pointer:pointer+4], "little")
        scripts.append(scr_addr)
        pointer += 4

    # structure analysis
    structure: list[ByteType] = [ByteType.UNKNOWN] * len(data)
    links: dict[int, str] = {}

    def fill_raw_action(addr: int):
        match structure[addr]:
            case ByteType.COMMAND_HEADER:
                structure[addr : addr + 4] = [ByteType.RAW] * 4
                down_command = int.from_bytes(data[addr:addr+2], "little")
                down_params_len = sum(int(par[0]) for par in commands_table[down_command][1:])
                structure[addr : addr + down_params_len + 2] = [ByteType.RAW] * (down_params_len+2)
            case ByteType.COMMAND_TAIL:
                down_addr = addr - 1
                while structure[down_addr] == ByteType.COMMAND_TAIL:
                    down_addr -= 1
                down_command = int.from_bytes(data[down_addr:down_addr+2], "little")
                down_params_len = sum(int(par[0]) for par in commands_table[down_command][1:])
                structure[down_addr : down_addr + down_params_len + 2] = [ByteType.RAW] * (down_params_len+2)
            case ByteType.ACTION_TAIL:
                down_addr = addr - 1
                while structure[down_addr] == ByteType.ACTION_TAIL:
                    down_addr -= 1
                structure[down_addr : down_addr + 4] = [ByteType.RAW] * 4
        structure[addr] = ByteType.RAW
        for next_addr in range(1, 4):
            match structure[next_addr]:
                case ByteType.COMMAND_HEADER:
                    down_command = int.from_bytes(data[next_addr:next_addr+2], "little")
                    down_params_len = sum(int(par[0]) for par in commands_table[down_command][1:])
                    structure[next_addr : next_addr + down_params_len + 2] = [ByteType.RAW] * (down_params_len+2)
                case ByteType.ACTION_HEADER:
                    structure[next_addr: next_addr + 4] = [ByteType.RAW] * 4
            structure[next_addr] = ByteType.RAW

    def fill_raw_command(addr: int, params_len: int):
        match structure[addr]:
            case ByteType.COMMAND_TAIL:
                down_addr = addr - 1
                while structure[down_addr] == ByteType.COMMAND_TAIL:
                    down_addr -= 1
                down_command = int.from_bytes(data[down_addr:down_addr+2], "little")
                down_params_len = sum(int(par[0]) for par in commands_table[down_command][1:])
                structure[down_addr:down_addr+down_params_len+2] = [ByteType.RAW] * (down_params_len+2)
            case ByteType.ACTION_HEADER:
                structure[addr:addr+4] = [ByteType.RAW] * 4
            case ByteType.ACTION_TAIL:
                down_addr = addr - 1
                while structure[down_addr] == ByteType.ACTION_TAIL:
                    down_addr -= 1
                structure[down_addr:down_addr+4] = [ByteType.RAW] * 4
        structure[addr] = ByteType.RAW
        for next_addr in range(addr+1, addr+params_len+2):
            match structure[next_addr]:
                case ByteType.COMMAND_HEADER:
                    down_command = int.from_bytes(data[next_addr:next_addr+2], "little")
                    down_params_len = sum(int(par[0]) for par in commands_table[down_command][1:])
                    structure[next_addr:next_addr+down_params_len+2] = [ByteType.RAW] * (down_params_len+2)
                case ByteType.ACTION_HEADER:
                    structure[next_addr:next_addr+4] = [ByteType.RAW] * 4
            structure[next_addr] = ByteType.RAW

    def walk_action(addr: int):
        while addr < len(data):
            if structure[addr] == ByteType.ACTION_HEADER:
                return
            action = int.from_bytes(data[addr:addr+2], "little")
            if structure[addr] in (ByteType.RAW, ByteType.COMMAND_HEADER, ByteType.COMMAND_TAIL, ByteType.ACTION_TAIL):
                fill_raw_action(addr)
            else:  # only UNKNOWN at this point
                for param_addr in range(addr+1, addr+4):
                    if structure[param_addr] in (ByteType.RAW, ByteType.COMMAND_HEADER, ByteType.ACTION_HEADER):
                        fill_raw_action(addr)
                        break
            if structure[addr] == ByteType.UNKNOWN:
                structure[addr] = ByteType.ACTION_HEADER
                structure[addr+1:addr+4] = [ByteType.ACTION_TAIL] * 3
            if action == 0xfe:
                return
            addr += 4

    def walk_command(addr: int):
        try:
            while addr < len(data):
                if structure[addr] == ByteType.COMMAND_HEADER:
                    return
                command = int.from_bytes(data[addr:addr+2], "little")
                params = commands_table[command][1:]
                params_len = sum(int(par[0]) for par in params)
                if structure[addr] in (ByteType.RAW, ByteType.COMMAND_TAIL, ByteType.ACTION_HEADER, ByteType.ACTION_TAIL):
                    fill_raw_command(addr, params_len)
                else:  # only UNKNOWN at this point
                    for param_addr in range(addr+1, addr+params_len+2):
                        if structure[param_addr] in (ByteType.RAW, ByteType.COMMAND_HEADER, ByteType.ACTION_HEADER):
                            fill_raw_command(addr, params_len)
                            break
                if structure[addr] == ByteType.UNKNOWN:
                    structure[addr] = ByteType.COMMAND_HEADER
                    structure[addr+1:addr+params_len+2] = [ByteType.COMMAND_TAIL] * (params_len+1)
                match command:
                    case 2:  # if vmhalt, return
                        return
                    case 4:  # if vmcall, branch and add link
                        link_addr = addr + 2 + params_len + int.from_bytes(data[addr+2:addr+6], "little")
                        link_addr %= 0x100000000
                        if link_addr not in links:
                            links[link_addr] = f"sub{len(links)}"
                        walk_command(link_addr)
                    case 5:  # if vmreturn, return
                        return
                    case 0x1e:  # if vmjump, jump and add link
                        link_addr = addr + 2 + params_len + int.from_bytes(data[addr+2:addr+6], "little")
                        link_addr %= 0x100000000
                        if link_addr not in links:
                            links[link_addr] = f"lbl{script_num}_{len(links)}"
                        addr = link_addr
                        continue
                    case 0x1f:  # if vmjumpif, branch and add link
                        link_addr = addr + 2 + params_len + int.from_bytes(data[addr+3:addr+7], "little")
                        link_addr %= 0x100000000
                        if link_addr not in links:
                            links[link_addr] = f"lbl{script_num}_{len(links)}"
                        walk_command(link_addr)
                    case 0x20:  # if vmcallif, branch and add link
                        link_addr = addr + 2 + params_len + int.from_bytes(data[addr+3:addr+7], "little")
                        link_addr %= 0x100000000
                        if link_addr not in links:
                            links[link_addr] = f"sub{len(links)}"
                        walk_command(link_addr)
                    case 0x64:  # if actorcmdexec, branch action and add link
                        link_addr = addr + 2 + params_len + int.from_bytes(data[addr+4:addr+8], "little")
                        link_addr %= 0x100000000
                        if link_addr not in links:
                            links[link_addr] = f"act{script_num}_{len(links)}"
                        walk_action(link_addr)
                    case 0x8c:  # if CallTrainerLose, return
                        return
                    case 0x17a:  # if CallWildLose, return
                        return
                addr += params_len + 2
        except OverflowError as e:
            raise Exception(e.args, f"Address {addr}")

    script_num = 0
    for script_addr in scripts:
        if script_addr not in links:
            links[script_addr] = f"scr{script_num}"
        script_num += 1
        walk_command(script_addr)

    pointer = len(scripts) * 4 + 2
    while pointer < len(data):
        if structure[pointer] != ByteType.UNKNOWN:
            pointer += 1
            continue
        search = pointer + 1
        zero = data[pointer] == 0
        while search < len(data) and structure[search] == ByteType.UNKNOWN:
            if data[search] != 0:
                zero = False
            search += 1
        if search >= len(data):
            if zero and len(data) - pointer < 4:
                structure[pointer:] = [ByteType.IGNORE] * (len(data) - pointer)
            else:
                structure[pointer:] = [ByteType.RAW] * (len(data) - pointer)
        elif structure[search] == ByteType.ACTION_HEADER and zero and search - pointer < 4:
            structure[pointer:search] = [ByteType.IGNORE] * (search - pointer)
        else:
            structure[pointer:search] = [ByteType.RAW] * (search - pointer)
        pointer = search+1

    for script_num in range(len(scripts)):
        script_file.script_links[script_num] = links[scripts[script_num]]
    pointer = len(scripts) * 4
    if data[pointer:pointer+2] == b'\x13\xfd':
        pointer += 2
    else:
        script_file.stop_bytes = False
    while pointer < len(data):
        if pointer in links:
            script_file.lines.append(Line("label", [links[pointer]]))
        match structure[pointer]:
            case x if x in (ByteType.UNKNOWN, ByteType.COMMAND_TAIL, ByteType.ACTION_TAIL):
                raise Exception(f"Caught {x} byte type after last analysis:\nAddress {pointer}, "
                                f"surrounding byte types {structure[pointer-1]} and {structure[pointer+1]}")
            case ByteType.RAW:
                script_file.lines.append(Line("raw", [data[pointer]]))
                pointer += 1
            case ByteType.IGNORE:
                pointer += 1
            case ByteType.COMMAND_HEADER:
                comm_num = int.from_bytes(data[pointer:pointer+2], "little")
                comm_def = commands_table[comm_num]
                line = Line("command", [comm_def[0]])
                pointer += 2
                if comm_num in (4, 0x1e):
                    value = int.from_bytes(data[pointer:pointer + 4], 'little')
                    line.parts.append(links[(value+pointer+4)%0x100000000])
                    pointer += 4
                elif comm_num in (0x1f, 0x20):
                    cond = data[pointer]
                    value = int.from_bytes(data[pointer+1:pointer + 5], 'little')
                    line.parts.extend((cond, links[(value+pointer+5)%0x100000000]))
                    pointer += 5
                elif comm_num == 0x64:
                    actor = int.from_bytes(data[pointer:pointer+2], 'little')
                    value = int.from_bytes(data[pointer+2:pointer+6], 'little')
                    line.parts.extend((actor, links[(value+pointer+6)%0x100000000]))
                    pointer += 6
                else:
                    for param in comm_def[1:]:
                        length = int(param[0])
                        value = int.from_bytes(data[pointer:pointer+length], "little")
                        line.parts.append(value)
                        pointer += length
                script_file.lines.append(line)
            case ByteType.ACTION_HEADER:
                act_num = int.from_bytes(data[pointer:pointer+2], "little")
                value = int.from_bytes(data[pointer+2:pointer+4], "little")
                script_file.lines.append(Line("action", [actions_table[act_num], value]))
                pointer += 4
    return script_file


def assemble(script_file: ScriptFile) -> bytearray:
    commands: dict[str, tuple[tuple[str, ...], int]] = {names[0]: (names[1:], num) for num, names in commands_table.items()}
    actions: dict[str, int] = {name: num for num, name in actions_table.items()}
    links: dict[str, int] = {}
    assembly: bytearray = bytearray()
    # {calling address: label name}
    link_calls: dict[int, str] = {}

    # write script list
    for index, lbl in script_file.script_links.items():
        link_calls[index*4] = lbl
        if len(assembly) < index*4+4:
            assembly.extend(bytes(index*4+4-len(assembly)))
    if script_file.stop_bytes:
        assembly.extend(b'\x13\xfd')
    # write command lines
    last_link = ""  # only used for actions right after a label
    for line in script_file.lines:
        if line.type == "label":
            if len(line.parts) != 1:
                raise Exception(f"Bad label definition: {' '.join(line.parts)}")
            if line.parts[0] in links:
                raise Exception(f"Double label definition: {line.parts[0]}")
            links[line.parts[0]] = len(assembly)
            last_link = line.parts[0]
        elif line.type == "comment":
            pass
        elif line.type == "raw":
            if line.parts[0] > 0xff:
                raise Exception(f"Raw value out of bounds: {line.parts[0]}")
            assembly.append(line.parts[0])
            last_link = ""
        elif line.type == "command":
            given_param_count = len(line.parts) - 1
            needed_param_count = len(commands[line.parts[0]][0])
            if given_param_count != needed_param_count:
                raise Exception(f"Param count mismatch: {' '.join(line.parts)}")
            command = commands[line.parts[0]][1]
            param_lengths = [int(p[0]) for p in commands[line.parts[0]][0]]
            assembly.extend(command.to_bytes(2, "little"))
            last_link = ""
            for param_num in range(given_param_count):
                param_val = line.parts[param_num+1]
                if isinstance(param_val, int):
                    assembly.extend(param_val.to_bytes(param_lengths[param_num], "little"))
                else:
                    link_calls[len(assembly)] = param_val
                    assembly.extend(b"\0\0\0\0")
        elif line.type == "action":
            if len(line.parts) != 2:
                raise Exception(f"Bad action call: {' '.join(line.parts)}")
            if last_link != "" and links[last_link] % 4 != 0:
                links[last_link] += (4 - (links[last_link] % 4))
            action = actions[line.parts[0]]
            value = line.parts[1]
            if len(assembly) % 4 != 0:
                assembly.extend(bytes(4 - (len(assembly) % 4)))
            assembly.extend(action.to_bytes(2, "little"))
            assembly.extend(value.to_bytes(2, "little"))
            last_link = ""
        else:
            raise Exception(f"Unknown command: [{line.type}] {' '.join(line.parts)}")
    # fill link calls
    for addr, link_name in link_calls.items():
        if link_name not in links:
            raise Exception(f"Unknown label: {link_name}")
        jump = ((links[link_name]-addr-4) % 0x100000000)
        assembly[addr:addr+4] = jump.to_bytes(4, "little")
    if len(assembly) % 4 != 0:
        assembly.extend([0] * (4 - (len(assembly) % 4)))
    return assembly
