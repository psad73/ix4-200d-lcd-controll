# disk status
import glob
import os


def get_lines():
    disks = sorted(glob.glob("/sys/block/sd[a-z]"))
    lines = ["Disk status: " + str(len(disks)) + " found"]

    if not disks:
        return lines + ["No sd disks detected"]

    for path in disks[:4]:
        name = os.path.basename(path)
        try:
            with open(path + "/device/state") as f:
                state = f.read().strip().upper()
        except OSError:
            state = "UNKNOWN"

        lines.append(name + ": " + state)

    if len(disks) > 4:
        lines.append("More disks detected")

    return lines[:5]
