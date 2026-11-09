# device temp, disk temp
import glob
import subprocess
import re
import os


def get_drive_temp(device):
    try:
        result = subprocess.run(
            ["smartctl", "-A", device],
            capture_output=True, text=True, timeout=4, check=False
        )
        for line in result.stdout.splitlines():
            if re.search(r"\b(Temperature_Celsius|Airflow_Temperature_Cel|Temperature_Internal)\b", line):
                match = re.search(r"\s(\d+)\s+\([^)]*\)\s*$", line)
                if match:
                    return int(match.group(1))

                # SMART attribute raw value is normally the final field.
                fields = line.split()
                if fields:
                    raw = re.search(r"\d+", fields[-1])
                    if raw:
                        return int(raw.group())
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def get_board_temps():
    try:
        result = subprocess.run(
            ["sensors"], capture_output=True, text=True,
            timeout=3, check=False
        )
        values = re.findall(r"temp\d+:\s+\+?(-?\d+(?:\.\d+)?)°C", result.stdout)
        return [round(float(v)) for v in values[:3]]
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return []


def get_lines():
    return ["Drive and board temperatures"]


def draw_screen(image, draw, font):
    drives = sorted(glob.glob("/dev/sd[a-z]"))[:4]
    temps = [get_drive_temp(d) for d in drives]
    board = get_board_temps()

    draw.text((1, 0), "Drive temperatures", font=font, fill=1)

    for i, device in enumerate(drives):
        x = 1 + i * 32
        value = "--" if temps[i] is None else str(temps[i])
        draw.text((x, 13), os.path.basename(device), font=font, fill=1)
        draw.text((x + 2, 25), value + "C", font=font, fill=1)

    draw.line((0, 39, 127, 39), fill=1)
    draw.text((1, 43), "Board:", font=font, fill=1)

    if board:
        text = " / ".join(str(t) for t in board) + " C"
    else:
        text = "unavailable"

    draw.text((1, 54), text, font=font, fill=1)
