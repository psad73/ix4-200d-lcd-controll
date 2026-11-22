#!/usr/bin/python3
"""Dispatch ix4-200d front-panel keys on Debian."""

import os
import signal
import subprocess
import time

from evdev import InputDevice, ecodes, list_devices

DEVICE_NAME = "ocp@f1000000:gpio-keys"
PIDFILE = "/var/run/ix4-lcd.pid"


def log(message):
    subprocess.run(
        ["logger", "-t", "ix4-button", message],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def signal_lcd(signum):
    try:
        with open(PIDFILE, encoding="ascii") as pidfile:
            value = pidfile.read().strip()
        if value.isdecimal():
            os.kill(int(value), signum)
        else:
            log("LCD PID file is invalid")
    except (OSError, ProcessLookupError):
        log("LCD controller is not running")


def run_systemctl(*args):
    try:
        result = subprocess.run(
            ["/usr/bin/systemctl", *args],
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        log("systemctl " + " ".join(args) + " failed: " + str(exc))
        return False
    if result.returncode:
        log("systemctl " + " ".join(args) + " failed")
    return result.returncode == 0


def find_button_device():
    for path in list_devices():
        try:
            device = InputDevice(path)
        except OSError:
            continue
        if device.name == DEVICE_NAME:
            return device
        device.close()
    return None


def handle_key(code, value):
    if code == ecodes.BTN_0 and value == 1:
        log("BTN_0: restarting systemd-networkd")
        run_systemctl("restart", "systemd-networkd")
    elif code == ecodes.BTN_1 and value == 1:
        log("BTN_1: advancing LCD screen")
        signal_lcd(signal.SIGUSR1)
    elif code == ecodes.KEY_RESTART and value == 1:
        log("Reset button: requesting system poweroff")
        run_systemctl("poweroff")
    elif code == ecodes.KEY_POWER2 and value == 0:
        log("Power button released: requesting system poweroff")
        run_systemctl("poweroff")


def main():
    while True:
        device = find_button_device()
        if device is None:
            log("gpio-keys input device not found; retrying")
            time.sleep(3)
            continue

        log("Listening on " + device.path + " (" + device.name + ")")
        try:
            for event in device.read_loop():
                if event.type == ecodes.EV_KEY:
                    handle_key(event.code, event.value)
        except OSError as exc:
            log("Input device disconnected: " + str(exc))
        finally:
            device.close()
        time.sleep(1)


if __name__ == "__main__":
    main()
