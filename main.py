from __future__ import annotations
from PIL import Image
import json
import math
import argparse
import sys
import os
import re
from pathlib import Path

emoji_dir = "72x72"
emojis = sorted(
    f for f in os.listdir(emoji_dir)
    if os.path.isfile(os.path.join(emoji_dir, f)) and f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
)

cols = 60 
rows = math.ceil(len(emojis) / cols)
size = 72

sheet = Image.new("RGBA", (cols * size, rows * size))

only_emojis = []

def filename_to_emoji(name):
    hexes = re.findall(r"[0-9a-fA-F]{4,6}", name)
    return ''.join(chr(int(h, 16)) for h in hexes)

for i, emoji in enumerate(emojis):
    x = (i % cols) * size
    y = (i // cols) * size
    img = Image.open(os.path.join(emoji_dir, emoji))
    sheet.paste(img, (x, y))

    name = os.path.splitext(emoji)[0]
    emoji_char = filename_to_emoji(name)
    only_emojis.append(emoji_char)

sheet.save("twemoji-spritesheet.png")
print(f"Saved sheet with {len(emojis)} emojis.")

with open("twemoji-only.txt", "w", encoding="utf-8") as fh:
    fh.write("\n".join(only_emojis))

print("Wrote twemoji-only.txt")

def read_emojis(txt_path: Path):
    with txt_path.open("r", encoding="utf-8") as fh:
        lines = [l.rstrip("\n") for l in fh]
    return [l for l in lines if l != ""]

def chunk_emojis(emojis: list[str], cols: int):
    rows = math.ceil(len(emojis) / cols)
    return ["".join(emojis[i * cols:(i + 1) * cols]) for i in range(rows)]

def inject_chars_into_json(json_path: Path, chars: list[str], out_path: Path):
    if json_path.exists():
        data = json.loads(json_path.read_text(encoding="utf-8"))
    else:
        data = {}

    providers = data.get("providers")
    if not isinstance(providers, list) or len(providers) == 0:
        providers = [{}]
        data["providers"] = providers

    if not isinstance(providers[0], dict):
        providers[0] = {}
    providers[0]["chars"] = chars

    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} with {len(chars)} char-rows (cols per row applied).")

def main(argv):
    p = argparse.ArgumentParser(description="Inject emoji rows into JSON providers[0].chars")
    p.add_argument("--json", "-j", type=Path, default=Path("font.json"), help="input JSON file to modify")
    p.add_argument("--txt", "-t", type=Path, default=Path("twemoji-only.txt"), help="emoji list (one per line)")
    p.add_argument("--cols", "-c", type=int, default=60, help="number of emojis per row (columns)")
    p.add_argument("--out", "-o", type=Path, default=None, help="output JSON (defaults to overwrite --json)")
    args = p.parse_args(argv)

    if not args.txt.exists():
        print(f"Emoji txt not found: {args.txt}", file=sys.stderr); sys.exit(1)

    emojis = read_emojis(args.txt)
    if not emojis:
        print("No emojis found in txt file.", file=sys.stderr); sys.exit(1)

    chars = chunk_emojis(emojis, args.cols)
    out_path = args.out or args.json
    inject_chars_into_json(args.json, chars, out_path)

if __name__ == "__main__":
    main(sys.argv[1:])
