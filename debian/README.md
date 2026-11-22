# Debian 12 port

This directory adds a Debian/systemd runtime for the ix4-200d LCD controller.
The OpenWrt init scripts and `/etc/rc.button` handlers remain unchanged.

## Hardware behavior

The LCD uses the existing GPIO map in `lcd/lib/main.py`. On the tested Debian
kernel, GPIO sysfs exposes gpiochip0 at global base 0 (32 lines) and gpiochip32
at global base 32 (18 lines), matching the global line numbers used by
python-periphery.

The Debian `gpio-keys` input device is named
`ocp@f1000000:gpio-keys`. The listener handles:

- BTN_0 press: restart `systemd-networkd`.
- BTN_1 press: advance to the next LCD screen.
- KEY_POWER2 release: request a clean poweroff.
- KEY_RESTART press: request a clean poweroff.

The LCD systemd unit displays the shutdown-start and final messages before
stopping. The old OpenWrt reboot handler also wrote to a fixed hwmon PWM path;
the Debian port does not do this because hwmon numbering is not stable across
kernels. Systemd's normal shutdown behavior is used.

## Install

On Debian 12, install the runtime packages:

```sh
sudo apt install python3-periphery python3-pil python3-evdev smartmontools lm-sensors
```

The last two packages enable disk-health and temperature screens; those screens
degrade gracefully when the tools are missing.

Keep or clone this repository at `/opt/ix4-lcd-panel`, then preview:

```sh
cd /opt/ix4-lcd-panel
sh debian/install.sh
```

Apply the installation and enable both units:

```sh
sudo sh debian/install.sh --apply
```

The project files stay under `/opt/ix4-lcd-panel`. The installer creates
symlinks for the systemd unit files under `/etc/systemd/system`, creates
`/etc/ix4-lcd.conf` only if absent, and enables both services. Existing
configuration is preserved, and existing unit files or conflicting symlinks
are left untouched.

The Debian config defaults to `eth1` and `wlx98ded00b1c6c`, based on the
reported `ip -br link` output. Edit `/etc/ix4-lcd.conf` if interface names
change. BTN_0 restarts networking, so an SSH connection through the NAS may
briefly disconnect.

## Logs and status

```sh
systemctl status ix4-lcd ix4-lcd-buttons
journalctl -u ix4-lcd -u ix4-lcd-buttons
```

Screen 1 prefers `/var/log/messages` when present and otherwise reads the
recent journal. The controller runs as root because it opens the LCD GPIO lines.
