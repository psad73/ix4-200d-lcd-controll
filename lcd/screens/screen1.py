# recent system messages (timestamp and hostname removed)
from collections import deque
from pathlib import Path
import re


LOG_PATH = Path("/var/log/messages")
SYSLOG_PREFIX = re.compile(
    r"^\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\S+\s+"
)
ISO_PREFIX = re.compile(
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?"
    r"(?:Z|[+-]\d{2}:?\d{2})?\s+\S+\s+"
)


def clean_message(line):
    line = line.rstrip("\r\n")
    line = SYSLOG_PREFIX.sub("", line, count=1)
    line = ISO_PREFIX.sub("", line, count=1)
    return line.strip()


def wrap_text(draw, text, font, max_width=126):
    words = text.split()
    if not words:
        return [""]

    rows = []
    row = ""
    for word in words:
        candidate = word if not row else row + " " + word
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            row = candidate
            continue

        if row:
            rows.append(row)
            row = ""

        # Split unusually long tokens so they still fit the LCD.
        while word and draw.textbbox((0, 0), word, font=font)[2] > max_width:
            part = word
            while part and draw.textbbox((0, 0), part, font=font)[2] > max_width:
                part = part[:-1]
            rows.append(part)
            word = word[len(part):]
        row = word

    if row:
        rows.append(row)
    return rows


def recent_rows(draw, font, max_rows=5):
    try:
        with LOG_PATH.open("r", errors="replace") as log:
            messages = deque(log, maxlen=20)
    except OSError:
        return ["Unable to read /var/log/messages"]

    rows = []
    for line in messages:
        rows.extend(wrap_text(draw, clean_message(line), font))
    return rows[-max_rows:] or ["No messages"]


def get_lines():
    return ["System messages"]


def draw_screen(image, draw, font):
    draw.text((1, 0), "System messages", font=font, fill=1)
    rows = recent_rows(draw, font)
    for index, row in enumerate(rows):
        draw.text((1, 12 + index * 10), row, font=font, fill=1)
