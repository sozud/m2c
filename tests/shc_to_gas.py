#!/usr/bin/env python3
"""Convert SHC assembly to GNU as format.
SHC's directives, comment markers, hex literals, and a couple of mnemonics are
problematic

Example:

        .EXPORT _test
        .SECTION    P,CODE,ALIGN=4
    _test:                  ; function: test
        MOV.L       L238,R1
        FMOV.S      FR4,FR5
        RTS
        NOP
        .SECTION    D,DATA,ALIGN=4
    L238:
        .DATA.L     H'1234
        .END

becomes:

    .globl _test
    .section .text,"ax",@progbits
    .balign 4
    _test:                   ! function: test
        MOV.L       L238,R1
        FMOV FR4,FR5
        RTS
        NOP
    .section .data,"aw",@progbits
    .balign 4
    L238:
    .long 0x1234
"""

import sys
from typing import List, Optional, Tuple


def is_hex_digit(c: str) -> bool:
    return c in "0123456789abcdefABCDEF"


def hex_converted(text: str) -> str:
    """convert H'1234 into GNU as syntax 0x1234"""
    out = []
    i = 0

    while i < len(text):
        if (
            i + 2 < len(text)
            and text[i].upper() == "H"
            and text[i + 1] == "'"
            and is_hex_digit(text[i + 2])
        ):
            out.append("0x")
            i += 2

            while i < len(text) and is_hex_digit(text[i]):
                out.append(text[i])
                i += 1
        else:
            out.append(text[i])
            i += 1

    return "".join(out)


def parse_fr(s: str, pos: int) -> Optional[Tuple[int, str]]:
    """parse a floating point register name (FR0 - FR15) at s[pos:]"""
    while pos < len(s) and s[pos].isspace():
        pos += 1

    start = pos

    if pos + 2 > len(s) or s[pos : pos + 2].upper() != "FR":
        return None

    pos += 2
    digits_start = pos

    while pos < len(s) and s[pos].isdigit():
        pos += 1

    if pos == digits_start:
        return None

    return pos, s[start:pos]


def convert_fmov_reg_reg(raw: str) -> Optional[str]:
    """FMOV.S FRn,FRm -> FMOV FRn,FRm"""
    for i in range(max(0, len(raw) - 5)):
        if i > 0:
            prev = raw[i - 1]
            if prev.isalnum() or prev == "_":
                continue

        if raw[i : i + 6].upper() != "FMOV.S":
            continue

        pos = i + 6

        parsed = parse_fr(raw, pos)
        if parsed is None:
            continue

        pos, r1 = parsed

        while pos < len(raw) and raw[pos].isspace():
            pos += 1

        if pos >= len(raw) or raw[pos] != ",":
            continue

        pos += 1

        parsed = parse_fr(raw, pos)
        if parsed is None:
            continue

        pos, r2 = parsed

        return raw[:i] + "FMOV " + r1 + "," + r2 + raw[pos:]

    return None


SECTION_NAMES: List[Tuple[str, str]] = [
    ("P", ".text"),
    ("C", ".rodata"),
    ("D", ".data"),
    ("B", ".bss"),
]


def gas_section_name(name: str) -> str:
    for shc_name, gas_name in SECTION_NAMES:
        if name.upper() == shc_name:
            return gas_name

    return name


def parse_uint(s: str) -> Optional[int]:
    s = s.strip()

    if not s:
        return None

    if not all(c.isdigit() for c in s):
        return None

    return int(s, 10)


def convert_line(line: str) -> str:
    if line.endswith("\r"):
        line = line[:-1]

    semi = line.find(";")

    if semi != -1:
        converted = line[:semi]

        if semi + 1 < len(line):
            converted += " !" + line[semi + 1 :]

        line = converted

    s = line.strip()

    if not s:
        return ""

    if s.upper().startswith((".EXPORT", ".IMPORT")):
        is_export = s.upper().startswith(".EXPORT")
        n = 7

        if len(s) > n and s[n].isspace():
            arg = s[n:].strip()

            if arg:
                return (".globl " if is_export else ".extern ") + arg

    if s.upper().startswith(".SECTION") and len(s) > 8 and s[8].isspace():
        rest = s[8:].strip()
        comma1 = rest.find(",")

        if comma1 == -1:
            if rest and not any(c in " \t\r\n," for c in rest):
                flags = ',"ax",@progbits' if rest.upper() == "P" else ',"aw",@progbits'

                return ".section " + gas_section_name(rest) + flags

        else:
            name = rest[:comma1].strip()
            after = rest[comma1 + 1 :].strip()

            comma2 = after.find(",")

            if comma2 == -1:
                kind = after.strip()
            else:
                kind = after[:comma2].strip()

            if name and kind.upper() in ("CODE", "DATA"):
                result = ".section " + gas_section_name(name)

                if kind.upper() == "CODE":
                    result += ',"ax",@progbits'
                else:
                    result += ',"aw",@progbits'

                if comma2 != -1:
                    tail = after[comma2 + 1 :].strip()

                    if tail.upper().startswith("ALIGN="):
                        align = parse_uint(tail[6:])

                        if align is not None:
                            result += "\n.balign " + str(align)

                return result

    if (
        len(s) >= 8
        and s.upper().startswith(".DATA.")
        and s[6].upper() in ("B", "W", "L")
        and s[7].isspace()
    ):
        size = s[6].upper()
        val = s[7:].strip()

        bang = val.find("!")

        if bang != -1:
            val = val[:bang].strip()

        if size == "B":
            directive = ".byte "
        elif size == "W":
            directive = ".word "
        else:
            directive = ".long "

        return directive + hex_converted(val)

    if s.upper().startswith(".END") and (
        len(s) == 4 or (len(s) > 4 and s[4].isspace())
    ):
        return ""

    if s.startswith("."):
        raise ValueError("unsupported SHC directive: " + line)

    fmov = convert_fmov_reg_reg(line)

    if fmov is not None:
        return hex_converted(fmov)

    return hex_converted(line)


def convert(text: str) -> str:
    return "".join(convert_line(line) + "\n" for line in text.splitlines())


def main() -> int:
    try:
        sys.stdout.write(convert(sys.stdin.read()))
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
