# ix4-200d LCD control

LCD controller and front-panel button scripts for the Lenovo/Iomega ix4-200d.
The repository supports both OpenWrt and Debian 12.

## Layout

- `lcd/` — Python launcher, controller and screen modules.
- `buttons/` — OpenWrt button hotplug handlers.
- `init/` — OpenWrt init scripts for LCD startup and shutdown messages.
- `debian/` — Debian 12 systemd units, input-event listener, installer and configuration.
- `media/` — `logo.png` and `logo.bmp`; screen 2 uses the PNG.
- `config/ix4-lcd.conf` — OpenWrt default network interface names.
- `docs/` — file mapping, GPIO notes and recovery guidance.
- `install.sh` — conservative OpenWrt installer.

## Requirements

The OpenWrt scripts expect an OpenWrt-like system with `/etc/rc.common`,
`/etc/rc.button/`, Python 3, `python-periphery` (module `periphery`) and
Pillow (module `PIL`). Screens also call standard commands such as `ip`,
`smartctl` and `sensors`; availability depends on the screen and firmware.

For Debian 12, see [debian/README.md](debian/README.md). The Debian port uses
systemd and the Linux input event device for front-panel buttons.

## Install on OpenWrt

1. Copy or clone this repository to a persistent local path on the NAS. Init
   scripts point to absolute paths, so do not keep it on a removable or
   late-mounted data volume.
2. Inspect `docs/FILE-MAPPING.txt` and make a separate backup of existing
   device files.
3. Run `sh install.sh` to preview. It makes no changes by default.
4. If the preview is correct, run `sh install.sh --apply` as root. It creates
   symlinks only for paths that do not already exist. Existing paths, including
   dangling or differently targeted symlinks, are conflicts and left alone.
5. Review links and script permissions. Enable or start services only after
   checking the local OpenWrt service behavior.

## Operation on OpenWrt

- LCD service: `ix4-lcd`.
- `BTN_1` sends SIGUSR1 to cycle screens.
- Shutdown scripts request LCD messages with SIGUSR2 and SIGALRM.
- The `power` button calls `sync` and `/sbin/poweroff`.

## Reuse and licensing

No `LICENSE` file is present. Until the owner adds a license, assume reuse,
redistribution and modification are not granted. The logo assets' origin and
redistribution rights are also unverified.
