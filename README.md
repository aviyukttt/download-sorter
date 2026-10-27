# Download Sorter

A friendly, dependency-free desktop GUI for Zorin OS that keeps `~/Downloads` tidy. It organizes files on demand or automatically every day at a chosen time. New files are classified into Photos, Screenshots, Videos, Audio, Documents, Archives, Code, or Others.

## Features

- Native-looking Tkinter GUI; no server and no external Python packages.
- Organizes top-level files from a configurable folder into category folders.
- Daily scheduler with an editable 24-hour time such as `18:00`.
- Safe duplicate handling: existing files are never overwritten; duplicates become `name (1).ext`.
- Screenshot detection by filename, including `Screenshot from 2026-10-27.png`.
- Optional hidden-file handling and configurable source/destination folders.
- User-level installation; no `sudo` is required for the app itself.

## Install on Zorin OS (recommended)

These commands work regardless of where you clone the repository:

```bash
sudo apt update
sudo apt install -y python3 python3-tk git

git clone https://github.com/aviyukttt/download-sorter.git
cd download-sorter
chmod +x install.sh uninstall.sh
./install.sh
```

After installation, open the application menu and search for **Download Sorter**. You can also launch it directly:

```bash
python3 "$HOME/.local/share/download-sorter/app.py"
```

The installer copies the app to `~/.local/share/download-sorter/` and generates the desktop launcher at `~/.local/share/applications/download-sorter.desktop`. It does not assume that the repository is located in `/home/ubuntu` or any other specific directory.

### Enable automatic start at login

The daily scheduler runs while the app is open. To start the app automatically whenever you log in:

```bash
cd download-sorter
./install.sh --autostart
```

The app opens as a normal GUI window; minimize it if you do not want it in the foreground. The default daily run time is 18:00 and can be changed in the app.

### Upgrade to a newer version

```bash
cd download-sorter
git pull
./install.sh
```

If autostart was already enabled, run `./install.sh --autostart` after pulling so the autostart copy is refreshed too.

### Uninstall

From the repository directory, run:

```bash
./uninstall.sh
```

This removes the installed app, application-menu launcher, and autostart entry. It does **not** delete your Downloads, organized files, or settings at `~/.config/download-sorter/config.json`.

## First-run behavior

The first run defaults to `~/Downloads`, sorts into category subfolders inside `~/Downloads`, and schedules the daily run at 18:00. Change the source folder, destination folder, time, and monitoring options in the GUI, then click **Save settings**.

## Troubleshooting

**The application does not appear in the menu:** log out and back in, or run `update-desktop-database ~/.local/share/applications` if that command is available. You can always launch it directly with the command above.

**The installer says Tkinter is missing:** run `sudo apt update && sudo apt install -y python3-tk`, then run `./install.sh` again.

**The daily job does not run:** make sure the GUI is running and **Automatically watch for new files** is enabled. This app is intentionally a user-session application; it does not run while you are logged out.

## Categories

| Folder | Common extensions |
| --- | --- |
| Photos | JPG, PNG, GIF, WEBP, HEIC, BMP, TIFF, RAW |
| Screenshots | Any filename containing `screenshot` or `screen shot` |
| Videos | MP4, MKV, MOV, AVI, WEBM |
| Audio | MP3, WAV, FLAC, AAC, OGG, M4A |
| Documents | PDF, DOCX, ODT, TXT, XLSX, PPTX, CSV |
| Archives | ZIP, TAR, GZ, BZ2, XZ, 7Z, RAR, DEB, ISO |
| Code | Python, JavaScript, TypeScript, HTML, CSS, JSON, YAML, shell, and more |
| Others | Files that do not match the above rules |

## Development and tests

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT. See [LICENSE](LICENSE).
