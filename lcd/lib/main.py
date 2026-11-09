#!/usr/bin/python3
import glob
import importlib.util
import os
import re
import signal
import threading
import time

from periphery import GPIO
from PIL import Image, ImageDraw, ImageFont

# Verified ix4-200d LCD GPIO mapping. Do not change.
RS = GPIO(15, "out")
A0 = GPIO(34, "out")
CS = GPIO(35, "out")
RW = GPIO(44, "out")
E  = GPIO(45, "out")

D0 = GPIO(36, "out")
D1 = GPIO(37, "out")
D2 = GPIO(38, "out")
D3 = GPIO(39, "out")
D4 = GPIO(40, "out")
D5 = GPIO(41, "out")
D6 = GPIO(42, "out")
D7 = GPIO(43, "out")

DATA = [D7, D6, D5, D4, D3, D2, D1, D0]
PINS = [RS, A0, CS, RW, E] + DATA

SCREEN_DIR = "/usr/lib/ix4-lcd/screens"
PIDFILE = "/var/run/ix4-lcd.pid"

stopping = threading.Event()
refresh_requested = threading.Event()
screen_index = 0
screens = []
shutdown_message = None


def stop_handler(signum, frame):
    stopping.set()


def next_screen_handler(signum, frame):
    global screen_index
    if screens and shutdown_message is None:
        screen_index = (screen_index + 1) % len(screens)
        refresh_requested.set()


def shutdown_start_handler(signum, frame):
    global shutdown_message
    shutdown_message = ["Shutting down...", "Please wait"]
    refresh_requested.set()


def shutdown_final_handler(signum, frame):
    global shutdown_message
    shutdown_message = ["Safe to power off", "Good bye!"]
    refresh_requested.set()


signal.signal(signal.SIGTERM, stop_handler)
signal.signal(signal.SIGINT, stop_handler)
signal.signal(signal.SIGUSR1, next_screen_handler)
signal.signal(signal.SIGUSR2, shutdown_start_handler)
signal.signal(signal.SIGALRM, shutdown_final_handler)


def set_gpio(pin, value):
    pin.write(bool(value))


def write_lcm(kind, value):
    set_gpio(E, 0)
    mask = 128
    for pin in DATA:
        set_gpio(pin, value & mask)
        mask >>= 1
    set_gpio(A0, kind)
    set_gpio(RW, 0)
    set_gpio(CS, 0)
    set_gpio(E, 1)
    set_gpio(E, 0)
    set_gpio(CS, 1)


def set_page(page):
    write_lcm(0, 0xB0 + page)
    write_lcm(0, 0x10)
    write_lcm(0, 0x00)


def init_lcm():
    set_gpio(RS, 1)
    for cmd in [
        0xAE, 0xA2, 0xA0, 0xC8, 0xA6, 0x40,
        0x22, 0x81, 0x3F, 0xF8, 0x00, 0xA4,
        0x2C, 0x2E, 0x2F, 0xAF
    ]:
        write_lcm(0, cmd)


def draw_lcm(image_bytes):
    for page in range(8):
        set_page(page)
        for x in range(128):
            write_lcm(1, image_bytes[page * 128 + x])

def load_screens():
    loaded = []
    paths = glob.glob(os.path.join(SCREEN_DIR, "screen*.py"))

    def screen_number(path):
        match = re.fullmatch(r"screen(\d+)\.py", os.path.basename(path))
        return int(match.group(1)) if match else None

    paths = [
        (screen_number(path), path)
        for path in paths
        if screen_number(path) is not None
    ]

    for number, path in sorted(paths):
        try:
            name = "ix4_screen_" + str(number)
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if not callable(getattr(module, "get_lines", None)):
                raise ValueError("Screen must provide get_lines()")

            loaded.append((number, module))
        except Exception as exc:
            print("Could not load", path, ":", exc, flush=True)

    return loaded


def fit_text(draw, text, font, max_width=128):
    text = str(text)
    while text and draw.textbbox((0, 0), text, font=font)[2] > max_width:
        text = text[:-1]
    return text


def render_lines(lines, plain=False):
    image = Image.new("1", (128, 64), 0)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    number, module = screens[screen_index] if screens else (None, None)

    custom_draw = getattr(module, "draw_screen", None) if module else None
    if callable(custom_draw) and not plain:
        custom_draw(image, draw, font)
    else:
        lines = [str(line) for line in lines][:5]
        spacing = 12 if len(lines) >= 5 else 15

        for index, line in enumerate(lines):
            draw.text(
                (1, index * spacing + 1),
                fit_text(draw, line, font),
                font=font,
                fill=1
            )

    pixels = image.load()
    result = [0] * 1024

    for page in range(8):
        for x in range(128):
            value = 0
            for bit in range(8):
                if pixels[x, page * 8 + bit]:
                    value |= 1 << bit
            result[page * 128 + x] = value

    return result


def current_lines():
    if not screens:
        return ["No screens found", "Check screens folder"]

    number, module = screens[screen_index]
    try:
        return module.get_lines()
    except Exception as exc:
        print("Screen", number, "failed:", exc, flush=True)
        return ["Screen error", "screen" + str(number)]


try:
    screens = load_screens()
    if not screens:
        print("No valid screens found in", SCREEN_DIR, flush=True)

    with open(PIDFILE, "w") as pidfile:
        pidfile.write(str(os.getpid()) + "\n")

    init_lcm()

    while not stopping.is_set():
        if shutdown_message is not None:
            draw_lcm(render_lines(shutdown_message, plain=True))
        else:
            draw_lcm(render_lines(current_lines()))
        refresh_requested.clear()
        refresh_requested.wait(5)

finally:
    try:
        os.unlink(PIDFILE)
    except OSError:
        pass

    for pin in reversed(PINS):
        try:
            pin.close()
        except Exception:
            pass
