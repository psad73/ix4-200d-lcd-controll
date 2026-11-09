import subprocess
import glob
import os


def get_smart_status(device):
    try:
        result = subprocess.run(
            ["smartctl", "-H", device],
            capture_output=True,
            text=True,
            timeout=4,
            check=False
        )
        output = result.stdout + "\n" + result.stderr

        if "PASSED" in output:
            return "OK"
        if "FAILED" in output:
            return "FAIL"
        if "SMART support is: Unavailable" in output:
            return "N/A"
        if "SMART support is: Disabled" in output:
            return "OFF"
        return "CHECK"
    except (OSError, subprocess.TimeoutExpired):
        return "ERR"


def get_lines():
    devices = sorted(glob.glob("/dev/sd[a-z]"))
    lines = ["SMART health"]

    if not devices:
        return lines + ["No drives found"]

    for device in devices[:4]:
        name = os.path.basename(device)
        status = get_smart_status(device)
        lines.append(name + ": " + status)

    if len(devices) > 4:
        lines.append("More drives...")

    return lines[:5]
