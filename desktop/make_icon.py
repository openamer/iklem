"""Generate the iklem app icon (512x512 PNG) — dark background, blue diamond."""
from PIL import Image, ImageDraw

SIZE = 512
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# Rounded-square dark background
radius = 96
d.rounded_rectangle([0, 0, SIZE, SIZE], radius=radius, fill=(13, 17, 23, 255))

# Blue diamond (the brand mark)
accent = (88, 166, 255, 255)
cx, cy = SIZE // 2, SIZE // 2
half = 150
diamond = [
    (cx, cy - half),       # top
    (cx + half, cy),       # right
    (cx, cy + half),       # bottom
    (cx - half, cy),       # left
]
d.polygon(diamond, fill=accent)

# Inner darker diamond for depth
inner_half = 90
inner = [
    (cx, cy - inner_half),
    (cx + inner_half, cy),
    (cx, cy + inner_half),
    (cx - inner_half, cy),
]
d.polygon(inner, fill=(31, 111, 235, 255))

img.save("icon.png")
print("icon.png written")
