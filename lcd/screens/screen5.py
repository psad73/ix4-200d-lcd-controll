import subprocess


def get_load():
    try:
        with open("/proc/loadavg") as f:
            return f.read().split()[:3]
    except (OSError, IndexError):
        return ["?", "?", "?"]


def get_memory():
    try:
        with open("/proc/meminfo") as f:
            values = {}
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    values[parts[0].rstrip(":")] = int(parts[1])

        available = values.get("MemAvailable", values.get("MemFree", 0))
        return available // 1024
    except (OSError, ValueError):
        return None


def get_fan():
    try:
        result = subprocess.run(
            ["sensors"], capture_output=True, text=True,
            timeout=3, check=False
        )
        for line in result.stdout.splitlines():
            if line.strip().startswith("fan1:"):
                return line.split()[1]
    except (OSError, subprocess.TimeoutExpired, IndexError):
        pass
    return "?"


def get_lines():
    return ["System status"]


def draw_screen(image, draw, font):
    load = get_load()
    memory = get_memory()
    fan = get_fan()

    draw.text((1, 1), "Pupka - system", font=font, fill=1)
    draw.text((1, 16), "Load: " + " ".join(load), font=font, fill=1)
    draw.text((1, 31), "RAM avail: " +
              (str(memory) + " MiB" if memory is not None else "?"),
              font=font, fill=1)
    draw.text((1, 46), "Fan 1: " + fan + " RPM", font=font, fill=1)
