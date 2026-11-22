#!/bin/sh
# Debian 12 installer. Preview by default; use --apply to install and enable.
set -eu

usage() {
    echo "Usage: $0 [--apply]"
}

apply=0
case "${1-}" in
    "") ;;
    --apply) apply=1 ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
esac

if [ "$apply" -eq 1 ] && [ "$(id -u)" -ne 0 ]; then
    echo "Run with root privileges to apply installation." >&2
    exit 1
fi

SCRIPT_PATH=$0
case "$SCRIPT_PATH" in
    */*) ;;
    *) SCRIPT_PATH=$(command -v "$SCRIPT_PATH") ;;
esac
REPO_DIR=$(CDPATH= cd -- "$(dirname -- "$SCRIPT_PATH")/.." && pwd -P)
EXPECTED_DIR=/opt/ix4-lcd-panel
UNIT_DIR=/etc/systemd/system

if [ "$REPO_DIR" != "$EXPECTED_DIR" ]; then
    echo "Keep the project at $EXPECTED_DIR and run $EXPECTED_DIR/debian/install.sh." >&2
    exit 1
fi

for required in \
    "$REPO_DIR/lcd/lib/main.py" \
    "$REPO_DIR/lcd/screens/screen0.py" \
    "$REPO_DIR/debian/buttond.py" \
    "$REPO_DIR/debian/stop-for-shutdown.sh" \
    "$REPO_DIR/debian/ix4-lcd.service" \
    "$REPO_DIR/debian/ix4-lcd-buttons.service" \
    "$REPO_DIR/media/logo.png"
do
    if [ ! -f "$required" ]; then
        echo "Missing required file: $required" >&2
        exit 1
    fi
done

if [ ! -e /sys/class/gpio/export ]; then
    echo "GPIO sysfs export is unavailable; the LCD controller cannot use the configured GPIO lines." >&2
    exit 1
fi

if ! /usr/bin/python3 -c 'from periphery import GPIO; from PIL import Image; import evdev' >/dev/null 2>&1; then
    echo "Install runtime packages first: apt install python3-periphery python3-pil python3-evdev" >&2
    exit 1
fi

if [ ! -d /run/systemd/system ]; then
    echo "This installer requires a running systemd system." >&2
    exit 1
fi

preflight_unit() {
    unit_name=$1
    target="$UNIT_DIR/$unit_name"
    source="$REPO_DIR/debian/$unit_name"
    if [ -L "$target" ]; then
        current=$(readlink -f "$target" 2>/dev/null || true)
        if [ "$current" = "$source" ]; then
            echo "OK: $target already links to project"
            return 0
        fi
        echo "CONFLICT: $target links elsewhere" >&2
        return 1
    fi
    if [ -e "$target" ]; then
        echo "CONFLICT: $target already exists" >&2
        return 1
    fi
    echo "WOULD LINK: $target -> $source"
}

preflight_unit ix4-lcd.service
preflight_unit ix4-lcd-buttons.service

if [ -e /etc/ix4-lcd.conf ]; then
    echo "KEEP: /etc/ix4-lcd.conf already exists"
else
    echo "WOULD CREATE: /etc/ix4-lcd.conf from Debian defaults"
fi
echo "PROJECT: files remain under $EXPECTED_DIR"
echo "ENABLE: ix4-lcd.service and ix4-lcd-buttons.service"

if [ "$apply" -eq 0 ]; then
    echo "Preview only. Re-run with --apply as root to install."
    exit 0
fi

install -d -m 755 "$UNIT_DIR"
for unit in ix4-lcd.service ix4-lcd-buttons.service; do
    target="$UNIT_DIR/$unit"
    source="$REPO_DIR/debian/$unit"
    if [ ! -L "$target" ]; then
        ln -s "$source" "$target"
    fi
done

if [ ! -e /etc/ix4-lcd.conf ]; then
    install -m 644 "$REPO_DIR/debian/ix4-lcd.conf" /etc/ix4-lcd.conf
fi

systemctl daemon-reload
systemctl enable --now ix4-lcd.service ix4-lcd-buttons.service
echo "Installed. Project files remain under $EXPECTED_DIR."
echo "Review with: systemctl status ix4-lcd ix4-lcd-buttons"
