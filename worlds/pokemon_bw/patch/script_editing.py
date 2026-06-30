import os
from os import PathLike
from enum import Enum
from typing import Literal

from .script_actions import actions_table
from .script_commands import commands_table


def see_write(out, s, end="\n"):
    if print_disassembly:
        print(s, end=end)
    print(s, end=end, file=out)


def debug(s):
    if debug_active:
        print(s)


class ByteType(Enum):
    UNKNOWN = 0
    IGNORE = 1
    RAW = 2
    COMMAND_HEADER = 3
    COMMAND_TAIL = 4
    ACTION_HEADER = 5
    ACTION_TAIL = 6


class Word:
    value: str | int
    type: Literal["int", "hex", "command", "link", "label"]


def disassemble(data: bytes | bytearray) -> list[list[Word]]:
    actions = {}
    for line in action_text:
        a = line.split()
        actions[int(a[0], 16)] = a
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

    def fill_raw_action(addr: int, shift: int):
        debug(f"{'  '*shift}Filling raw action at {addr}")
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

    def fill_raw_command(addr: int, params_len: int, shift: int):
        debug(f"{'  '*shift}Filling raw command at {addr}")
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

    def walk_action(addr: int, shift: int):
        debug(f"{'  '*shift}Walk action at {addr}")
        while addr < len(data):
            if structure[addr] == ByteType.ACTION_HEADER:
                debug(f"{'  '*shift}Walk action found header at {addr}")
                return
            action = int.from_bytes(data[addr:addr+2], "little")
            if structure[addr] in (ByteType.RAW, ByteType.COMMAND_HEADER, ByteType.COMMAND_TAIL, ByteType.ACTION_TAIL):
                fill_raw_action(addr, shift)
            else:  # only UNKNOWN at this point
                for param_addr in range(addr+1, addr+4):
                    if structure[param_addr] in (ByteType.RAW, ByteType.COMMAND_HEADER, ByteType.ACTION_HEADER):
                        fill_raw_action(addr, shift)
                        break
            if structure[addr] == ByteType.UNKNOWN:
                structure[addr] = ByteType.ACTION_HEADER
                structure[addr+1:addr+4] = [ByteType.ACTION_TAIL] * 3
            if action == 0xfe:
                debug(f"{'  '*shift}EndAction at {addr}")
                return
            addr += 4

    def walk_command(addr: int, shift: int):
        try:
            debug(f"{'  '*shift}Walk command at {addr}")
            while addr < len(data):
                if structure[addr] == ByteType.COMMAND_HEADER:
                    debug(f"{'  '*shift}Walk command found header at {addr}")
                    return
                command = int.from_bytes(data[addr:addr+2], "little")
                params = commands_table[command][1:]
                params_len = sum(int(par[0]) for par in params)
                if structure[addr] in (ByteType.RAW, ByteType.COMMAND_TAIL, ByteType.ACTION_HEADER, ByteType.ACTION_TAIL):
                    fill_raw_command(addr, params_len, shift)
                else:  # only UNKNOWN at this point
                    for param_addr in range(addr+1, addr+params_len+2):
                        if structure[param_addr] in (ByteType.RAW, ByteType.COMMAND_HEADER, ByteType.ACTION_HEADER):
                            fill_raw_command(addr, params_len, shift)
                            break
                if structure[addr] == ByteType.UNKNOWN:
                    structure[addr] = ByteType.COMMAND_HEADER
                    structure[addr+1:addr+params_len+2] = [ByteType.COMMAND_TAIL] * (params_len+1)
                match command:
                    case 2:  # if vmhalt, return
                        debug(f"{'  '*shift}VMHalt at {addr}")
                        return
                    case 4:  # if vmcall, branch and add link
                        link_addr = addr + 2 + params_len + int.from_bytes(data[addr+2:addr+6], "little")
                        link_addr %= 0x100000000
                        if link_addr not in links:
                            links[link_addr] = f"sub{len(links)}"
                        debug(f"{'  '*shift}VMCall at {addr} to {link_addr}")
                        walk_command(link_addr, shift+1)
                    case 5:  # if vmreturn, return
                        debug(f"{'  '*shift}VMReturn at {addr}")
                        return
                    case 0x1e:  # if vmjump, jump and add link
                        link_addr = addr + 2 + params_len + int.from_bytes(data[addr+2:addr+6], "little")
                        link_addr %= 0x100000000
                        if link_addr not in links:
                            links[link_addr] = f"lbl{script_num}_{len(links)}"
                        debug(f"{'  '*shift}VMJump at {addr} to {link_addr}")
                        addr = link_addr
                        continue
                    case 0x1f:  # if vmjumpif, branch and add link
                        link_addr = addr + 2 + params_len + int.from_bytes(data[addr+3:addr+7], "little")
                        link_addr %= 0x100000000
                        if link_addr not in links:
                            links[link_addr] = f"lbl{script_num}_{len(links)}"
                        debug(f"{'  '*shift}VMJumpIf at {addr} to {link_addr}")
                        walk_command(link_addr, shift+1)
                    case 0x20:  # if vmcallif, branch and add link
                        link_addr = addr + 2 + params_len + int.from_bytes(data[addr+3:addr+7], "little")
                        link_addr %= 0x100000000
                        if link_addr not in links:
                            links[link_addr] = f"sub{len(links)}"
                        debug(f"{'  '*shift}VMCallIf at {addr} to {link_addr}")
                        walk_command(link_addr, shift+1)
                    case 0x64:  # if actorcmdexec, branch action and add link
                        link_addr = addr + 2 + params_len + int.from_bytes(data[addr+4:addr+8], "little")
                        link_addr %= 0x100000000
                        if link_addr not in links:
                            links[link_addr] = f"act{script_num}_{len(links)}"
                        debug(f"{'  '*shift}ActorCmdExec at {addr} to {link_addr}")
                        walk_action(link_addr, shift+1)
                    # case 0x8c:  # if CallTrainerLose, return
                    #     debug(f"{'  '*shift}CallTrainerLose at {addr}")
                    #     return
                    # case 0x17a:  # if CallWildLose, return
                    #     debug(f"{'  '*shift}CallWildLose at {addr}")
                    #     return
                addr += params_len + 2
        except OverflowError as e:
            raise Exception(e.args, f"Address {addr}")

    script_num = 0
    for script_addr in scripts:
        if script_addr not in links:
            links[script_addr] = f"scr{script_num}"
            debug(f"Registered link scr{script_num}")
        script_num += 1
        walk_command(script_addr, 1)

    def enhanced_set_const_single(p, s) -> bool:
        # Check for unused WorkSetConst commands
        unknown_setconst = data.find(b'\x28\0', p, s)
        if unknown_setconst != -1 and s - unknown_setconst >= 6:
            if data[unknown_setconst+3:unknown_setconst+6] == b'\x80\0\0':
                structure[unknown_setconst] = ByteType.COMMAND_HEADER
                structure[unknown_setconst+1:unknown_setconst+6] = [ByteType.COMMAND_TAIL] * 5
                return True
        return False

    def enhanced_set_const_walk(p, s) -> bool:
        # Check for unused WorkSetConst commands
        unknown_setconst = data.find(b'\x28\0', p, s)
        if unknown_setconst != -1 and s - unknown_setconst >= 6:
            if data[unknown_setconst+3:unknown_setconst+6] == b'\x80\0\0':
                if (
                    structure[unknown_setconst+6] in (ByteType.RAW, ByteType.UNKNOWN, ByteType.COMMAND_HEADER) and
                    0 < int.from_bytes(data[unknown_setconst+6:unknown_setconst+8], "little") <= 0x260
                ):
                    walk_command(unknown_setconst, 0)
                else:
                    structure[unknown_setconst] = ByteType.COMMAND_HEADER
                    structure[unknown_setconst+1:unknown_setconst+6] = [ByteType.COMMAND_TAIL] * 5
                return True
        return False

    def enhanced_jump(p, s) -> bool:
        # Check for unused(?) jump commands
        unknown_jump = data.find(b'\x1e\0', p, s)
        if unknown_jump != -1 and s - unknown_jump >= 6:
            addr = unknown_jump + 6 + int.from_bytes(data[unknown_jump+2:unknown_jump+6], "little")
            addr %= 0x100000000
            if addr < len(data):
                walk_command(unknown_jump, 0)
                return True
        unknown_jump = data.find(b'\x1f\0', p, s)
        if unknown_jump != -1 and s - unknown_jump >= 7:
            addr = unknown_jump + 7 + int.from_bytes(data[unknown_jump+3:unknown_jump+7], "little")
            addr %= 0x100000000
            if addr < len(data):
                walk_command(unknown_jump, 0)
                return True
        return False

    def enhanced_actions(p, s) -> bool:
        # Check for unused(?) actions
        end_action = data.find(b'\xfe\0\0\0', p, s)
        if end_action % 4 == 0:
            back_search = end_action - 4
            while back_search >= p and data[back_search+1] == 0 and data[back_search] <= 0xc0:
                back_search -= 4
            else:
                walk_action(back_search+4, 0)
                return True
        return False

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
        if enhanced_disassembly:
            if enhanced_set_const_single(pointer, search): continue
            # if enhanced_set_const_walk(pointer, search): continue
            if enhanced_jump(pointer, search): continue
            if enhanced_actions(pointer, search): continue
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

    with open(dest, "wt") as out:
        for script_num in range(len(scripts)):
            see_write(out, f"{script_num} {links[scripts[script_num]]}")
        pointer = len(scripts) * 4
        if data[pointer:pointer+2] == b'\x13\xfd':
            see_write(out, "# commands")
            pointer += 2
        else:
            see_write(out, "# no stop bytes\n# commands")
        while pointer < len(data):
            if pointer in links:
                if links[pointer][0:3] == "scr":
                    see_write(out, f"\n# {links[pointer]}")
                elif links[pointer][0:3] == "lbl":
                    see_write(out, f"\n   # {links[pointer]}")
                elif links[pointer][0:3] == "act":
                    see_write(out, f"\n   # {links[pointer]}")
                else:
                    see_write(out, f"\n# {links[pointer]}")
            match structure[pointer]:
                case x if x in (ByteType.UNKNOWN, ByteType.COMMAND_TAIL, ByteType.ACTION_TAIL):
                    raise Exception(f"Caught {x} byte type after last analysis:\nAddress {pointer}, "
                                    f"surrounding byte types {structure[pointer-1]} and {structure[pointer+1]}")
                case ByteType.RAW:
                    command_counting["RAW"].append(f)
                    see_write(out, f"    _{hex(data[pointer])}")
                    pointer += 1
                case ByteType.IGNORE:
                    pointer += 1
                case ByteType.COMMAND_HEADER:
                    comm_num = int.from_bytes(data[pointer:pointer+2], "little")
                    comm_def = commands_table[comm_num]
                    command_counting[comm_def[0]].append(f)
                    see_write(out, f"    {comm_def[0]}", "")
                    pointer += 2
                    if comm_num in (4, 0x1e):
                        value = int.from_bytes(data[pointer:pointer + 4], 'little')
                        see_write(out, f" {links[(value+pointer+4)%0x100000000]}")
                        pointer += 4
                    elif comm_num in (0x1f, 0x20):
                        cond = data[pointer]
                        value = int.from_bytes(data[pointer+1:pointer + 5], 'little')
                        see_write(out, f" {cond} {links[(value+pointer+5)%0x100000000]}")
                        pointer += 5
                    elif comm_num == 0x64:
                        actor = int.from_bytes(data[pointer:pointer+2], 'little')
                        value = int.from_bytes(data[pointer+2:pointer+6], 'little')
                        if actor in range(0x4000, 0x4200) or actor in range(0x8000, 0x8100):
                            see_write(out, f" {hex(actor)} {links[(value+pointer+6)%0x100000000]}")
                        else:
                            see_write(out, f" {actor} {links[(value+pointer+6)%0x100000000]}")
                        pointer += 6
                    else:
                        for param in comm_def[1:]:
                            length = int(param[0])
                            value = int.from_bytes(data[pointer:pointer+length], "little")
                            if value in range(0x4000, 0x4200) or value in range(0x8000, 0x8100) or value in range(0xFF00, 0x10000):
                                see_write(out, f" {hex(value)}", "")
                            else:
                                see_write(out, f" {value}", "")
                            pointer += length
                        see_write(out, "")
                case ByteType.ACTION_HEADER:
                    act_num = int.from_bytes(data[pointer:pointer+2], "little")
                    value = int.from_bytes(data[pointer+2:pointer+4], "little")
                    see_write(out, f"     {actions_table[act_num]} {value}")
                    pointer += 4


def assemble(f: PathLike | str, dest: PathLike | str):
    data = [line.split() for line in get_text_file_lines(f)]
    command_text = get_text_file_lines("commands.txt")
    action_text = get_text_file_lines("actions.txt")
    commands: dict[str, tuple[list[str], int]] = {}
    actions: dict[str, int] = {}
    for line in command_text:
        c = line.split()
        commands[c[1]] = (c[2:], int(c[0], 16))
        debug(f"Registered command {c}")
    for line in action_text:
        a = line.split()
        actions[a[1]] = int(a[0], 16)
        debug(f"Registered action {a}")

    links: dict[str, int] = {}
    assembly: bytearray = bytearray()
    # {calling address: label name}
    link_calls: dict[int, str] = {}

    # search "# command"
    for l in range(len(data)):
        words = data[l]
        if words == ["#", "commands"]:
            script_lines = data[:l]
            command_lines = data[l+1:]
            debug(f"# command at line {l}")
            break
    else:
        raise Exception("Missing '# commands'")
    # write script list
    stop_bytes = True
    if len(script_lines) > 0 and script_lines[-1] == ["#", "no", "stop", "bytes"]:
        stop_bytes = False
        script_lines.pop()
        debug(f"# no stop bytes at line {l}")
    for words in script_lines:
        if len(words) == 0:
            continue
        if len(words) < 2 or not words[0].isnumeric():
            raise Exception(f"Bad line in script list: {' '.join(words)}")
        script = int(words[0])
        link_calls[script*4] = words[1]
        debug(f"Script {script} calling {words[1]}")
        if len(assembly) < script*4+4:
            assembly.extend(bytes(script*4+4-len(assembly)))
    if stop_bytes:
        assembly.extend(b'\x13\xfd')
    # write command lines
    last_link = ""  # only used for actions right after a label
    block_false_link_names: list[str] = []
    block_end_link_names: list[str] = []
    for words in command_lines:
        if len(words) == 0:
            continue
        if words[0] == "#":
            if len(words) != 2:
                raise Exception(f"Bad label definition: {' '.join(words)}")
            if words[1] in links:
                raise Exception(f"Double label definition: {words[1]}")
            links[words[1]] = len(assembly)
            last_link = words[1]
            debug(f"Link {words[1]} to {len(assembly)}")
        elif words[0] == "##":
            debug(f"Comment {' '.join(words[1:])}")
        elif words[0].startswith("_"):
            raw = int(words[0][1:], 16)
            if raw > 0xff:
                raise Exception(f"Raw value out of bounds: {' '.join(words)}")
            assembly.append(raw)
            last_link = ""
            debug(f"Raw {raw}")
        elif words[0] == "if":
            if len(words) != 5:
                raise Exception(f"Bad if statement word count: {' '.join(words)}")
            if words[2] != "==" or words[3] not in ("work", "const"):
                raise Exception(f"Bad if statement words: {' '.join(words)}")
            if not words[1].isalnum() or not words[4].isalnum():
                raise Exception(f"Bad if statement numbers: {' '.join(words)}")
            # Get the link name for where to jump if this block is executed and there is an elif or else
            block_end_link_names.append(f"block{len(assembly)}")
            while block_end_link_names[-1] in links:
                block_end_link_names[-1] += "_"
            # Get the link name for where to jump if the condition is not met
            block_false_link_names.append(f"if{len(assembly)}")
            while block_false_link_names[-1] in links:
                block_false_link_names[-1] += "_"
            # StackPush
            assembly.extend(b'\x09\0')
            assembly.extend(int(words[1], 16).to_bytes(2, "little"))
            # StackPush[Const]
            if words[3] == "work":
                assembly.extend(b'\x09\0')
                assembly.extend(int(words[4], 16).to_bytes(2, "little"))
            else:
                assembly.extend(b'\x08\0')
                assembly.extend(int(words[4]).to_bytes(2, "little"))
            # StackCmp 1
            # VMJumpIf 255 "where to jump if false"
            assembly.extend(b'\x11\0\1\0\x1f\0\xff')
            link_calls[len(assembly)] = block_false_link_names[-1]
            assembly.extend(b'\0\0\0\0')
            # Cleanup
            last_link = ""
            debug(f"if {' '.join(words[1:])} (new block depth {len(block_false_link_names)})")
        elif words[0] == "elif":
            if len(words) != 5:
                raise Exception(f"Bad elif statement word count: {' '.join(words)}")
            if words[2] != "==" or words[3] not in ("work", "const"):
                raise Exception(f"Bad elif statement words: {' '.join(words)}")
            if not words[1].isalnum() or not words[4].isalnum():
                raise Exception(f"Bad elif statement numbers: {' '.join(words)}")
            if len(block_false_link_names) == 0:
                raise Exception(f"elif block without being in an if block: {' '.join(words)}")
            if not block_false_link_names[-1].startswith("if"):
                raise Exception(f"elif block following after a non-if block: {' '.join(words)}")
            # VMJump "next endblock because last if/elif block was executed"
            assembly.extend(b'\x1e\0')
            link_calls[len(assembly)] = block_end_link_names[-1]
            assembly.extend(b'\0\0\0\0')
            # Jump here if last if/elif block was false
            links[block_false_link_names[-1]] = len(assembly)
            # Get new link name for where to jump if the condition is not met
            block_false_link_names[-1] = f"if{len(assembly)}"
            while block_false_link_names[-1] in links:
                block_false_link_names[-1] += "_"
            # StackPush
            assembly.extend(b'\x09\0')
            assembly.extend(int(words[1], 16).to_bytes(2, "little"))
            # StackPush[Const]
            if words[3] == "work":
                assembly.extend(b'\x09\0')
                assembly.extend(int(words[4], 16).to_bytes(2, "little"))
            else:
                assembly.extend(b'\x08\0')
                assembly.extend(int(words[4]).to_bytes(2, "little"))
            # StackCmp 1
            # VMJumpIf 255 "where to jump if false"
            assembly.extend(b'\x11\0\1\0\x1f\0\xff')
            link_calls[len(assembly)] = block_false_link_names[-1]
            assembly.extend(b'\0\0\0\0')
            # Cleanup
            last_link = ""
            debug(f"elif {' '.join(words[1:])} (keeping block depth {len(block_false_link_names)})")
        elif words[0] == "else":
            if len(words) != 1:
                raise Exception(f"Bad else statement word count: {' '.join(words)}")
            if len(block_false_link_names) == 0:
                raise Exception(f"else block without being in a block: {' '.join(words)}")
            if not block_false_link_names[-1].startswith("if"):
                raise Exception(f"else block following after a non-if block: {' '.join(words)}")
            # VMJump "next endblock because last if/elif block was executed"
            assembly.extend(b'\x1e\0')
            link_calls[len(assembly)] = block_end_link_names[-1]
            assembly.extend(b'\0\0\0\0')
            # Jump here if last if/elif block was false
            links[block_false_link_names[-1]] = len(assembly)
            # No jump from here needed anymore, so prevent other elif/else blocks after this
            block_false_link_names[-1] = "_"
            # Cleanup
            last_link = ""
            debug(f"else {' '.join(words[1:])} (keeping block depth {len(block_false_link_names)})")
        elif words[0] == "while":
            if len(words) != 5:
                raise Exception(f"Bad while statement word count: {' '.join(words)}")
            if words[2] != "==" or words[3] not in ("work", "const"):
                raise Exception(f"Bad while statement words: {' '.join(words)}")
            if not words[1].isalnum() or not words[4].isalnum():
                raise Exception(f"Bad while statement numbers: {' '.join(words)}")
            # Get the link name for where to jump back for looping
            block_end_link_names.append(f"block{len(assembly)}")
            while block_end_link_names[-1] in links:
                block_end_link_names[-1] += "_"
            # Get the link name for where to jump if false (aka endblock)
            block_false_link_names.append(f"while{len(assembly)}")
            while block_false_link_names[-1] in links:
                block_false_link_names[-1] += "_"
            # Set looping link here at beginning
            links[block_end_link_names[-1]] = len(assembly)
            # StackPush
            assembly.extend(b'\x09\0')
            assembly.extend(int(words[1], 16).to_bytes(2, "little"))
            # StackPush[Const]
            if words[3] == "work":
                assembly.extend(b'\x09\0')
                assembly.extend(int(words[4], 16).to_bytes(2, "little"))
            else:
                assembly.extend(b'\x08\0')
                assembly.extend(int(words[4]).to_bytes(2, "little"))
            # StackCmp 1
            # VMJumpIf 255 "where to jump if false"
            assembly.extend(b'\x11\0\1\0\x1f\0\xff')
            link_calls[len(assembly)] = block_false_link_names[-1]
            assembly.extend(b'\0\0\0\0')
            # Cleanup
            last_link = ""
            debug(f"while {' '.join(words[1:])} (new block depth {len(block_false_link_names)})")
        elif words[0] == "endblock":
            if len(words) != 1:
                raise Exception(f"Bad endblock statement word count: {' '.join(words)}")
            if len(block_false_link_names) == 0:
                raise Exception(f"endblock without being in a block")
            if block_false_link_names[-1] == "_":
                # Only link the jumps at end of if/elif blocks
                links[block_end_link_names[-1]] = len(assembly)
                # Cleanup
                block_false_link_names.pop()
                block_end_link_names.pop()
                last_link = ""
                debug(f"ending if[-elif]-else block (reducing block depth to {len(block_false_link_names)})")
            elif block_false_link_names[-1].startswith("if"):
                # Link the jumps at end of if/elif blocks and the false jump of the last if/elif block
                links[block_end_link_names[-1]] = len(assembly)
                links[block_false_link_names[-1]] = len(assembly)
                # Cleanup
                block_false_link_names.pop()
                block_end_link_names.pop()
                last_link = ""
                debug(f"ending if[-elif] block (reducing block depth to {len(block_false_link_names)})")
            else:  # Only while block at this point
                # Add looping jump and then link false jump
                assembly.extend(b'\x1e\0')
                link_calls[len(assembly)] = block_end_link_names[-1]
                assembly.extend(b'\0\0\0\0')
                links[block_false_link_names[-1]] = len(assembly)
                # Cleanup
                block_false_link_names.pop()
                block_end_link_names.pop()
                last_link = ""
                debug(f"ending while block (reducing block depth to {len(block_false_link_names)})")
        elif words[0] in commands:
            given_param_count = len(words) - 1
            needed_param_count = len(commands[words[0]][0])
            if given_param_count != needed_param_count:
                raise Exception(f"Param count mismatch: {' '.join(words)}")
            command = commands[words[0]][1]
            param_lengths = [int(p[0]) for p in commands[words[0]][0]]
            assembly.extend(command.to_bytes(2, "little"))
            last_link = ""
            debug(f"Command {' '.join(words)}")
            for param_num in range(given_param_count):
                param_val = words[param_num+1]
                if param_val.isnumeric():
                    assembly.extend(int(param_val).to_bytes(param_lengths[param_num], "little"))
                elif param_val.startswith("0x"):
                    assembly.extend(int(param_val, 16).to_bytes(param_lengths[param_num], "little"))
                else:
                    link_calls[len(assembly)] = param_val
                    assembly.extend(b"\0\0\0\0")
                    debug(f"    Calling link {param_val}")
        elif words[0] in actions:
            if len(words) != 2:
                raise Exception(f"Bad action call: {' '.join(words)}")
            if last_link != "" and links[last_link] % 4 != 0:
                links[last_link] += (4 - (links[last_link] % 4))
            action = actions[words[0]]
            value = int(words[1])
            if len(assembly) % 4 != 0:
                assembly.extend(bytes(4 - (len(assembly) % 4)))
            assembly.extend(action.to_bytes(2, "little"))
            assembly.extend(value.to_bytes(2, "little"))
            last_link = ""
            debug(f"Action {' '.join(words)}")
        else:
            raise Exception(f"Unknown command: {' '.join(words)}")
    if len(block_false_link_names) != 0:
        raise Exception(f"{len(block_false_link_names)} if or while blocks not ended")
    # fill link calls
    for addr, link_name in link_calls.items():
        if link_name not in links:
            raise Exception(f"Unknown label: {link_name}")
        jump = ((links[link_name]-addr-4) % 0x100000000)
        assembly[addr:addr+4] = jump.to_bytes(4, "little")
        debug(f"Linking param at address {hex(addr)} to {hex(links[link_name])}, jumping {hex(jump)}")
    if len(assembly) % 4 != 0:
        assembly.extend([0] * (4 - (len(assembly) % 4)))
    with open(dest, "wb") as out:
        out.write(assembly)


if __name__ == "__main__":
    from sys import argv

    # settings
    debug_active = False
    print_disassembly = False
    enhanced_disassembly = False
    write_counting = False
    if len(argv) >= 2:
        if argv[1].endswith(".asm"):
            assemble(argv[1], argv[1][:-4] + ".bin")
        elif argv[1].endswith(".bin"):
            disassemble(argv[1], argv[1][:-4] + ".asm")
        else:
            try:
                assemble(argv[1], argv[1] + ".bin")
            except UnicodeDecodeError:
                disassemble(argv[1], argv[1] + ".asm")
