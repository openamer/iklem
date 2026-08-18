"""Convert icon.png to icon.ico (multi-size Windows icon)."""
from PIL import Image

img = Image.open("icon.png")
# Save as .ico with multiple sizes
img.save(
    "icon.ico",
    format="ICO",
    sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
)
print("icon.ico written")
