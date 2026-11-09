Attempting to perform the InitializeDefaultDrives operation on the 'FileSystem' provider failed.
#!/bin/sh
# Conservative symlink installer for ix4-200d LCD control.
# Default is preview only. Use --apply to create links.
set -eu

usage() {
    echo "Usage: $0 [--apply]"
    echo "Without --apply, print the planned symlinks without changing files."
}

apply=0
case "${1-}" in
    "") ;;
    --apply) apply=1 ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
esac

if [ "$apply" -eq 1 ] && [ "$(id -u)" -ne 0 ]; then
    echo "Run with root privileges to apply links." >&2
    exit 1
fi

SCRIPT_PATH=$0
case "$SCRIPT_PATH" in
    */*) ;;
    *) SCRIPT_PATH=$(command -v "$SCRIPT_PATH") ;;
esac
REPO_DIR=$(CDPATH= cd -- "$(dirname -- "$SCRIPT_PATH")" && pwd -P)

# Source path : system path. Links point into this repository checkout.
set -- \
    "lcd/ix4-lcd.py:/usr/bin/ix4-lcd.py" \
    "lcd/lib/main.py:/usr/lib/ix4-lcd/main.py" \
    "lcd/screens/screen0.py:/usr/lib/ix4-lcd/screens/screen0.py" \
    "lcd/screens/screen1.py:/usr/lib/ix4-lcd/screens/screen1.py" \
    "lcd/screens/screen2.py:/usr/lib/ix4-lcd/screens/screen2.py" \
    "lcd/screens/screen3.py:/usr/lib/ix4-lcd/screens/screen3.py" \
    "lcd/screens/screen4.py:/usr/lib/ix4-lcd/screens/screen4.py" \
    "lcd/screens/screen5.py:/usr/lib/ix4-lcd/screens/screen5.py" \
    "media/logo.png:/usr/lib/ix4-lcd/screens/logo.png" \
    "buttons/BTN_0:/etc/rc.button/BTN_0" \
    "buttons/BTN_1:/etc/rc.button/BTN_1" \
    "buttons/power:/etc/rc.button/power" \
    "buttons/reboot:/etc/rc.button/reboot" \
    "init/ix4-lcd:/etc/init.d/ix4-lcd" \
    "init/ix4-lcd-shutdown-start:/etc/init.d/ix4-lcd-shutdown-start" \
    "init/ix4-a-lcd-shutdown-final:/etc/init.d/ix4-a-lcd-shutdown-final"

# Preflight every source and destination before making any changes.
conflicts=0
while [ "$#" -gt 0 ]; do
    entry=$1
    shift
    source_rel=${entry%%:*}
    destination=${entry#*:}
    source_path="$REPO_DIR/$source_rel"

    if [ ! -e "$source_path" ]; then
        echo "ERROR: missing repository source: $source_path" >&2
        exit 1
    fi

    if [ -L "$destination" ]; then
        current=$(readlink "$destination")
        if [ "$current" = "$source_path" ]; then
            echo "OK: $destination -> $source_path (already correct)"
            continue
        fi
        echo "CONFLICT: $destination is a symlink to $current" >&2
        conflicts=$((conflicts + 1))
        continue
    fi

    if [ -e "$destination" ]; then
        echo "CONFLICT: $destination already exists; leaving it untouched" >&2
        conflicts=$((conflicts + 1))
        continue
    fi

    echo "WOULD LINK: $destination -> $source_path"
done

if [ "$conflicts" -gt 0 ]; then
    echo "$conflicts conflict(s) or missing prerequisite(s); conflicting paths were not changed." >&2
    exit 1
fi

if [ "$apply" -eq 0 ]; then
    echo "Preview only. Re-run with --apply as root to create links."
else
    mkdir -p /usr/lib/ix4-lcd/screens
    set -- \
        "lcd/ix4-lcd.py:/usr/bin/ix4-lcd.py" \
        "lcd/lib/main.py:/usr/lib/ix4-lcd/main.py" \
        "lcd/screens/screen0.py:/usr/lib/ix4-lcd/screens/screen0.py" \
        "lcd/screens/screen1.py:/usr/lib/ix4-lcd/screens/screen1.py" \
        "lcd/screens/screen2.py:/usr/lib/ix4-lcd/screens/screen2.py" \
        "lcd/screens/screen3.py:/usr/lib/ix4-lcd/screens/screen3.py" \
        "lcd/screens/screen4.py:/usr/lib/ix4-lcd/screens/screen4.py" \
        "lcd/screens/screen5.py:/usr/lib/ix4-lcd/screens/screen5.py" \
        "media/logo.png:/usr/lib/ix4-lcd/screens/logo.png" \
        "buttons/BTN_0:/etc/rc.button/BTN_0" \
        "buttons/BTN_1:/etc/rc.button/BTN_1" \
        "buttons/power:/etc/rc.button/power" \
        "buttons/reboot:/etc/rc.button/reboot" \
        "init/ix4-lcd:/etc/init.d/ix4-lcd" \
        "init/ix4-lcd-shutdown-start:/etc/init.d/ix4-lcd-shutdown-start" \
        "init/ix4-a-lcd-shutdown-final:/etc/init.d/ix4-a-lcd-shutdown-final"
    while [ "$#" -gt 0 ]; do
        entry=$1
        shift
        source_rel=${entry%%:*}
        destination=${entry#*:}
        source_path="$REPO_DIR/$source_rel"
        if [ ! -L "$destination" ]; then
            ln -s "$source_path" "$destination"
            echo "LINKED: $destination -> $source_path"
        fi
    done
    echo "Links created. No services were enabled, started, or restarted."
fi

