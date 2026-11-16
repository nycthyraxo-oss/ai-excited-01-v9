#!/usr/bin/env python3
"""First Class entry runner: copy entry.png to the output dir (stdlib only)."""

import os
import shutil
import sys

ENTRY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")


def validate(path: str) -> int:
    """Check the entry image: JPEG magic, size <= 1 MiB, dims <= 1024x1024."""
    import struct

    size = os.path.getsize(path)
    if size > 1024 * 1024:
        print(f"entry.png too large: {size} bytes", file=sys.stderr)
        return 1
    with open(path, "rb") as f:
        data = f.read()
    if data[:2] != b"\xff\xd8" or data[-2:] != b"\xff\xd9":
        print("entry.png is not a valid JPEG (SOI/EOI)", file=sys.stderr)
        return 1
    i = 2
    while i < len(data) - 1:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            if width > 1024 or height > 1024:
                print(f"entry.png too big: {width}x{height}", file=sys.stderr)
                return 1
            print(f"validated entry.png: {width}x{height}, {size} bytes")
            return 0
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        length = struct.unpack(">H", data[i + 2:i + 4])[0]
        i += 2 + length
    print("entry.png has no SOF marker", file=sys.stderr)
    return 1


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "out"
    )
    os.makedirs(out_dir, exist_ok=True)
    with open(ENTRY, "rb") as src:
        magic = src.read(2)
    if magic != b"\xff\xd8":
        print("entry.png is not a JPEG", file=sys.stderr)
        return 1
    if validate(ENTRY) != 0:
        return 1
    shutil.copyfile(ENTRY, os.path.join(out_dir, "entry.png"))
    print("wrote", os.path.join(out_dir, "entry.png"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
