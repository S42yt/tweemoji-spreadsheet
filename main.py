from PIL import Image
import os, math

emoji_dir = "72x72"
emojis = sorted(os.listdir(emoji_dir))

cols = 60 
rows = math.ceil(len(emojis) / cols)
size = 72

sheet = Image.new("RGBA", (cols * size, rows * size))

for i, emoji in enumerate(emojis):
    x = (i % cols) * size
    y = (i // cols) * size
    img = Image.open(os.path.join(emoji_dir, emoji))
    sheet.paste(img, (x, y))

sheet.save("twemoji-spritesheet.png")
print(f"Saved sheet with {len(emojis)} emojis.")
