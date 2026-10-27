# Download Sorter

A friendly, dependency-free desktop GUI for Zorin OS that keeps `~/Downloads` tidy. It can organize files on demand or run automatically every day at a chosen time. New files are classified into Photos, Screenshots, Videos, Audio, Documents, Archives, Code, or Others.

## Features

- Native-looking Tkinter GUI; no server and no external Python packages.
- Watches a configurable folder and sorts its top-level files into category folders.
- Daily scheduler with editable 24-hour time such as `18:00`.
- Safe duplicate handling: existing files are never overwritten; duplicates become `name (1).ext`.
- Screenshot detection by filename, including files such as `Screenshot from 2026-10-27.png`.
- Optional hidden-file handling and configurable source/destination folders.
- `.desktop` launcher for the Zorin application menu.

## Run on Zorin OS

```bash
python3 app.py
```

Tkinter is normally included with Zorin OS. If it is missing:

```bash
sudo apt update
sudo apt install python3-tk
```

Then launch **Download Sorter** from the application menu by installing the desktop file:

```bash
mkdir -p ~/.local/share/applications
cp download-sorter.desktop ~/.local/share/applications/
# Update the Exec/Icon paths if you cloned this repo somewhere other than ~/download-sorter.
```

The first run defaults to `~/Downloads`, sorts into category subfolders inside `~/Downloads`, and schedules the daily run at 18:00. Settings are stored at `~/.config/download-sorter/config.json`.

## Autostart at login (optional)

To keep the daily scheduler active after login:

```bash
mkdir -p ~/.config/autostart
cp download-sorter.desktop ~/.config/autostart/
```

The app stays open as a small GUI window; minimize it if desired. The daily job runs only while the app is running.

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

## Tests

Run the dependency-free unit tests:

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT. See [LICENSE](LICENSE).
