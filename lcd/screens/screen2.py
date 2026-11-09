from pathlib import Path
from PIL import Image


LOGO_PATH = Path("/usr/lib/ix4-lcd/screens/logo.png")


def get_lines():
    return ["Pupka logo"]


def draw_screen(image, draw, font):
    logo = Image.open(LOGO_PATH).convert("1")
    image.paste(logo, (32, 0))
