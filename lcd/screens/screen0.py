# hostname, ip addresses, uptime
import re
import subprocess

CONFIG_PATH = "/etc/ix4-lcd.conf"
DEFAULT_INTERFACES = {
    "LAN_INTERFACE": "br-lan",
    "WIFI_INTERFACE": "phy0-sta0",
}
_INTERFACE_NAME = re.compile(r"^[A-Za-z0-9_.:-]+$")


def get_interfaces():
    interfaces = DEFAULT_INTERFACES.copy()
    try:
        with open(CONFIG_PATH, encoding="utf-8") as config:
            for line in config:
                line = line.partition("#")[0].strip()
                if "=" not in line:
                    continue
                key, value = (part.strip() for part in line.split("=", 1))
                if key in interfaces and _INTERFACE_NAME.fullmatch(value):
                    interfaces[key] = value
    except OSError:
        pass
    return interfaces


def get_ipv4(interface):
    try:
        result = subprocess.run(
            ["ip", "-4", "-o", "addr", "show", "dev", interface],
            capture_output=True, text=True, timeout=2, check=False
        )
        words = result.stdout.split()
        for i, word in enumerate(words[:-1]):
            if word == "inet":
                return words[i + 1].split("/")[0]
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def get_uptime():
    try:
        with open("/proc/uptime") as f:
            seconds = int(float(f.read().split()[0]))
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes = seconds // 60
        if days:
            return f"{days}d {hours:02}h {minutes:02}m"
        return f"{hours}h {minutes:02}m"
    except (OSError, ValueError, IndexError):
        return "unknown"


def get_lines():
    interfaces = get_interfaces()
    return [
        "Pupka - status",
        "LAN: " + (get_ipv4(interfaces["LAN_INTERFACE"]) or "no IPv4"),
        "WiFi: " + (get_ipv4(interfaces["WIFI_INTERFACE"]) or "waiting..."),
        "Uptime: " + get_uptime(),
    ]


def draw_ethernet(draw, x, y):
    # Small network socket
    draw.rectangle((x + 1, y + 2, x + 10, y + 9), outline=1)
    draw.line((x + 3, y, x + 3, y + 3), fill=1)
    draw.line((x + 5, y, x + 5, y + 3), fill=1)
    draw.line((x + 7, y, x + 7, y + 3), fill=1)
    draw.line((x + 9, y, x + 9, y + 3), fill=1)
    draw.line((x + 4, y + 9, x + 4, y + 11), fill=1)
    draw.line((x + 8, y + 9, x + 8, y + 11), fill=1)


def draw_wifi(draw, x, y):
    # Three Wi-Fi signal arcs and a dot
    draw.arc((x, y, x + 12, y + 12), 225, 315, fill=1)
    draw.arc((x + 3, y + 3, x + 9, y + 9), 225, 315, fill=1)
    draw.point((x + 6, y + 11), fill=1)


def draw_screen(image, draw, font):
    interfaces = get_interfaces()
    lan = get_ipv4(interfaces["LAN_INTERFACE"]) or "no IPv4"
    wifi = get_ipv4(interfaces["WIFI_INTERFACE"]) or "waiting..."
    uptime = get_uptime()

    draw.text((1, 1), "Pupka - status", font=font, fill=1)

    draw_ethernet(draw, 2, 17)
    draw.text((16, 17), "LAN " + lan, font=font, fill=1)

    draw_wifi(draw, 2, 32)
    draw.text((16, 32), "WiFi " + wifi, font=font, fill=1)

    draw.text((1, 49), "Uptime: " + uptime, font=font, fill=1)
