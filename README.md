Attempting to perform the InitializeDefaultDrives operation on the 'FileSystem' provider failed.
# ix4-200d LCD control

LCD controller and front-panel button scripts for the Lenovo/Iomega ix4-200d running OpenWrt. The code displays status screens and uses the front-panel buttons to change screens or request a safe poweroff.

This repository is owner-maintained. It has only been inspected remotely; installation has not been tested on a device. Review the scripts and confirm paths and dependencies for your firmware before installing.

## Layout

- `lcd/` — Python launcher, controller and screen modules.
- `buttons/` — OpenWrt button hotplug handlers.
- `init/` — OpenWrt init scripts for LCD startup and shutdown messages.
- `media/` — `logo.png` and `logo.bmp`; screen 2 uses the PNG.
- `docs/` — file mapping, GPIO notes and recovery guidance.
- `backups/` — placeholder only; it is not a recoverable device backup.
- `install.sh` — conservative symlink installer.

## Requirements

The scripts expect an OpenWrt-like system with `/etc/rc.common`, `/etc/rc.button/`, Python 3, `python-periphery` (module `periphery`) and Pillow (module `PIL`). Screens also call standard commands such as `ip`, `smartctl` and `sensors`; availability depends on the screen and firmware. The controller opens GPIO lines 15, 34–45. Confirm these interfaces and GPIO numbering on your exact device and firmware.

## Install

1. Copy or clone this repository to a persistent local path on the NAS. Init scripts point to the repository's absolute paths, so do not keep it on a removable or late-mounted data volume.
2. Inspect `docs/FILE-MAPPING.txt` and make a separate backup of existing device files.
3. Run `./install.sh` to preview. It makes no changes by default.
4. If the preview is correct, run `./install.sh --apply` as root. It creates symlinks only for paths that do not already exist. Existing paths, including dangling or differently targeted symlinks, are conflicts and left alone.
5. Review links and script permissions. Enable or start services only after checking the local OpenWrt service behavior. The installer does not enable services, restart anything, edit rc.d ordering, or change the device's buttons or services.

The installer creates `/usr/lib/ix4-lcd/screens` if needed after preflighting all link destinations. It does not move or copy this repository, back up device files, or overwrite existing targets. All symlink targets are derived from the checkout's location.

## Operation

- LCD service: `ix4-lcd`.
- `BTN_0` sends SIGUSR1 to cycle screens.
- Shutdown scripts request LCD messages with SIGUSR2 and SIGALRM.
- `power` calls `sync` and `/sbin/poweroff`.
- Screen 2 reads `/usr/lib/ix4-lcd/screens/logo.png`, provided by a link to `media/logo.png`.

The display is 128×64. See `docs/GPIO-MAP.txt` and `docs/RESTORE-INSTRUCTIONS.txt`.

## Restore

Stop or disable only services you enabled, then remove only symlinks verified to point into this checkout. Restore pre-install files from your own backup. See `docs/RESTORE-INSTRUCTIONS.txt`. No restore has been tested on hardware.

## Reuse and licensing

No `LICENSE` file is present. Until the owner adds a license, assume reuse, redistribution and modification are not granted. The logo assets' origin and redistribution rights are also unverified.

## Review findings

The default branch had two commits (`init` and `v0.1`, 9 November 2026). Several documentation files and `install.sh` were empty placeholders. The repository includes both logo assets, but their provenance and licensing have not been verified. The empty backup placeholder is not a backup. See `docs/IX4-FILE-MANIFEST.txt` for items discussed in project history but absent from the repository.

