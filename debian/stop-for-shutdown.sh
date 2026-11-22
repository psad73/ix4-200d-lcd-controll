#!/bin/sh
set -u

pid=${1-}
case "$pid" in
    ''|*[!0-9]*) exit 0 ;;
esac

kill -USR2 "$pid" 2>/dev/null || exit 0
sleep 5
kill -ALRM "$pid" 2>/dev/null || exit 0
sleep 3
