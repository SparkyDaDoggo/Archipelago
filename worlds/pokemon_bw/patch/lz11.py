# MODIFIED DSDECMP-JAVA SOURCE FOR RANDOMIZER'S NEEDS, PORTED FROM UPR-FVX TO PYTHON
# License is below

# Copyright (c) 2010 Nick Kraayenbrink
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

def decomp(data: bytes, offset: int) -> bytes:
    offset += 1
    length = int.from_bytes(data[offset:offset+3], "little")
    offset += 3
    if length == 0:
        length = int.from_bytes(data[offset:offset+4], "big")
        offset += 4

    out = bytearray(length)
    curr_size = 0
    flags: int
    flag: bool
    b1: int
    bt: int
    b2: int
    b3: int
    _len: int
    disp: int
    cdest: int

    while curr_size < len(out):
        flags = data[offset] & 0xff
        offset += 1

        i = 0
        while i < 8 and curr_size < len(out):
            flag = (flags & (0x80 >> i)) > 0
            if flag:
                b1 = data[offset] & 0xff
                offset += 1

                match b1 >> 4:
                    case 0:
                        _len = b1 << 4
                        bt = data[offset] & 0xff
                        offset += 1
                        _len |= bt >> 4
                        _len += 0x11
                        disp = (bt & 0x0f) << 8
                        b2 = data[offset] & 0xff
                        offset += 1
                        disp |= b2
                    case 1:
                        bt = data[offset] & 0xff
                        offset += 1
                        b2 = data[offset] & 0xff
                        offset += 1
                        b3 = data[offset] & 0xff
                        offset += 1
                        _len = (b1 & 0xf) << 12
                        _len |= bt << 4
                        _len |= b2 >> 4
                        _len += 0x111
                        disp = (b2 & 0x0f) << 8
                        disp |= b3
                    case _:
                        _len = (b1 >> 4) + 1
                        disp = (b1 & 0x0f) << 8
                        b2 = data[offset] & 0xff
                        offset += 1
                        disp |= b2

                if disp > curr_size:
                    raise Exception(f"disp {disp} > curr_size {curr_size}")

                cdest = curr_size

                j = 0
                while j < _len and curr_size < len(out):
                    out[curr_size] = out[cdest - disp - 1 + j]
                    curr_size += 1
                    j += 1

                if curr_size > len(out):
                    break
            else:
                out[curr_size] = data[offset]
                curr_size += 1
                offset += 1

                if curr_size > len(out):
                    break

            i += 1

    return bytes(out)
