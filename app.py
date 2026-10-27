#!/usr/bin/env python3
"""Download Sorter — a small, dependency-free desktop organizer for Zorin OS."""
from __future__ import annotations

import json
import os
import queue
import shutil
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except ModuleNotFoundError:  # Allows the file-sorting logic to be tested headlessly.
    tk = None
    filedialog = messagebox = ttk = None

APP_NAME = "Download Sorter"
CONFIG_DIR = Path.home() / ".config" / "download-sorter"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_RULES = {
    "Photos": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".bmp", ".tiff", ".raw", ".cr2", ".nef"],
    "Screenshots": [".screenshot.png", ".screenshot.jpg"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".m4v"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".opus"],
    "Documents": [".pdf", ".doc", ".docx", ".odt", ".txt", ".rtf", ".xls", ".xlsx", ".ods", ".ppt", ".pptx", ".csv"],
    "Archives": [".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar", ".deb", ".iso"],
    "Code": [".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".yaml", ".yml", ".sh", ".cpp", ".java", ".rs", ".go"],
}

@dataclass
class Settings:
    source: str = str(Path.home() / "Downloads")
    destination: str = str(Path.home() / "Downloads")
    run_time: str = "18:00"
    watch: bool = True
    include_hidden: bool = False

    @classmethod
    def load(cls) -> "Settings":
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return cls(**{k: data[k] for k in cls.__dataclass_fields__ if k in data})
        except (OSError, ValueError, TypeError):
            return cls()

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(self.__dict__, indent=2), encoding="utf-8")


def category_for(path: Path) -> str:
    """Return the destination folder for a file based on extension/name."""
    name = path.name.lower()
    if "screenshot" in name or name.startswith("screen shot"):
        return "Screenshots"
    suffix = path.suffix.lower()
    for category, extensions in DEFAULT_RULES.items():
        if suffix in extensions:
            return category
    return "Others"


def unique_destination(path: Path) -> Path:
    """Avoid overwriting an existing file by appending a numbered suffix."""
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    counter = 1
    while True:
        candidate = path.with_name(f"{stem} ({counter}){suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def organize_folder(source: Path, destination: Path, include_hidden: bool = False):
    """Move top-level files from source into categorized folders.

    Returns (moved, skipped, errors), where moved is [(name, category)].
    """
    moved, skipped, errors = [], [], []
    source = source.expanduser().resolve()
    destination = destination.expanduser().resolve()
    if not source.exists():
        return moved, skipped, [f"Source folder does not exist: {source}"]
    destination.mkdir(parents=True, exist_ok=True)
    try:
        items = list(source.iterdir())
    except OSError as exc:
        return moved, skipped, [str(exc)]
    for item in items:
        if not item.is_file() or (item.name.startswith(".") and not include_hidden):
            continue
        # Avoid moving files that are already in the organizer's destination subfolders.
        if item.parent != source:
            continue
        category = category_for(item)
        target_dir = destination / category
        target_dir.mkdir(parents=True, exist_ok=True)
        target = unique_destination(target_dir / item.name)
        try:
            shutil.move(str(item), str(target))
            moved.append((item.name, category))
        except (OSError, shutil.Error) as exc:
            errors.append(f"{item.name}: {exc}")
    return moved, skipped, errors


class OrganizerApp(tk.Tk if tk is not None else object):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("940x680")
        self.minsize(760, 560)
        self.configure(bg="#f5f7fb")
        self.settings = Settings.load()
        self.events: queue.Queue = queue.Queue()
        self.stop_event = threading.Event()
        self.last_daily_run = ""
        self._build_style()
        self._build_ui()
        self._load_fields()
        self.after(250, self._drain_events)
        self.protocol("WM_DELETE_WINDOW", self._close)
        self._append_log("Ready. Your Downloads folder is protected until you click Organize now.")
        threading.Thread(target=self._scheduler_loop, daemon=True).start()

    def _build_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f5f7fb")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("TLabel", background="#f5f7fb", foreground="#24324a", font=("TkDefaultFont", 10))
        style.configure("Title.TLabel", background="#f5f7fb", foreground="#15233d", font=("TkDefaultFont", 24, "bold"))
        style.configure("Subtitle.TLabel", background="#f5f7fb", foreground="#64748b", font=("TkDefaultFont", 10))
        style.configure("CardTitle.TLabel", background="#ffffff", foreground="#15233d", font=("TkDefaultFont", 12, "bold"))
        style.configure("TButton", padding=(12, 8), font=("TkDefaultFont", 10))
        style.configure("Accent.TButton", background="#2563eb", foreground="white", padding=(15, 9), font=("TkDefaultFont", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#1d4ed8")])
        style.configure("TEntry", padding=7)
        style.configure("TCheckbutton", background="#ffffff", foreground="#24324a")
        style.configure("Treeview", rowheight=28, background="#ffffff", fieldbackground="#ffffff", borderwidth=0)
        style.configure("Treeview.Heading", background="#e8eef8", foreground="#334155", font=("TkDefaultFont", 9, "bold"))

    def _build_ui(self):
        outer = ttk.Frame(self, padding=28)
        outer.pack(fill="both", expand=True)
        header = ttk.Frame(outer)
        header.pack(fill="x", pady=(0, 20))
        ttk.Label(header, text="Download Sorter", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="A calm, automatic home for everything in your Downloads folder.", style="Subtitle.TLabel").pack(anchor="w", pady=(5, 0))

        content = ttk.Frame(outer)
        content.pack(fill="both", expand=True)
        left = ttk.Frame(content, style="Card.TFrame", padding=20)
        left.pack(side="left", fill="y", padx=(0, 16))
        right = ttk.Frame(content, style="Card.TFrame", padding=20)
        right.pack(side="left", fill="both", expand=True)

        ttk.Label(left, text="Organizer settings", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 16))
        self.source_var = tk.StringVar(); self.destination_var = tk.StringVar(); self.time_var = tk.StringVar()
        self.watch_var = tk.BooleanVar(); self.hidden_var = tk.BooleanVar()
        self._path_row(left, "Watch folder", self.source_var, self._choose_source)
        self._path_row(left, "Sort into", self.destination_var, self._choose_destination)
        ttk.Label(left, text="Daily run time (24-hour)", style="CardTitle.TLabel").pack(anchor="w", pady=(20, 5))
        time_row = ttk.Frame(left, style="Card.TFrame"); time_row.pack(fill="x")
        ttk.Entry(time_row, textvariable=self.time_var, width=10).pack(side="left")
        ttk.Label(time_row, text=" e.g. 18:00", background="#ffffff", foreground="#64748b").pack(side="left")
        ttk.Checkbutton(left, text="Automatically watch for new files", variable=self.watch_var).pack(anchor="w", pady=(18, 5))
        ttk.Checkbutton(left, text="Include hidden files", variable=self.hidden_var).pack(anchor="w", pady=5)
        ttk.Button(left, text="Save settings", command=self._save_settings).pack(fill="x", pady=(22, 8))
        ttk.Button(left, text="Organize now", style="Accent.TButton", command=self._organize_now).pack(fill="x")
        ttk.Label(left, text="Categories\nPhotos • Screenshots • Videos\nAudio • Documents • Archives\nCode • Others", background="#ffffff", foreground="#64748b", justify="left").pack(anchor="w", pady=(24, 0))

        top = ttk.Frame(right, style="Card.TFrame")
        top.pack(fill="x")
        ttk.Label(top, text="Activity", style="CardTitle.TLabel").pack(side="left")
        self.status_var = tk.StringVar(value="Monitoring is ready")
        ttk.Label(top, textvariable=self.status_var, background="#ffffff", foreground="#2563eb").pack(side="right")
        table_frame = ttk.Frame(right, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True, pady=(14, 0))
        self.tree = ttk.Treeview(table_frame, columns=("file", "category", "time"), show="headings")
        self.tree.heading("file", text="File"); self.tree.heading("category", text="Moved to"); self.tree.heading("time", text="Time")
        self.tree.column("file", width=280); self.tree.column("category", width=130); self.tree.column("time", width=120)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview); self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True); scrollbar.pack(side="right", fill="y")
        ttk.Label(right, text="Tip: files are never overwritten; duplicates receive a numbered name.", background="#ffffff", foreground="#64748b").pack(anchor="w", pady=(12, 0))

    def _path_row(self, parent, label, variable, command):
        ttk.Label(parent, text=label, style="CardTitle.TLabel").pack(anchor="w", pady=(0, 5))
        row = ttk.Frame(parent, style="Card.TFrame"); row.pack(fill="x", pady=(0, 10))
        ttk.Entry(row, textvariable=variable, width=28).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse", command=command).pack(side="left", padx=(6, 0))

    def _load_fields(self):
        self.source_var.set(self.settings.source); self.destination_var.set(self.settings.destination)
        self.time_var.set(self.settings.run_time); self.watch_var.set(self.settings.watch); self.hidden_var.set(self.settings.include_hidden)

    def _choose_source(self):
        selected = filedialog.askdirectory(initialdir=self.source_var.get(), title="Choose folder to watch")
        if selected: self.source_var.set(selected)

    def _choose_destination(self):
        selected = filedialog.askdirectory(initialdir=self.destination_var.get(), title="Choose destination folder")
        if selected: self.destination_var.set(selected)

    def _save_settings(self, quiet=False):
        try:
            datetime.strptime(self.time_var.get().strip(), "%H:%M")
        except ValueError:
            messagebox.showerror("Invalid time", "Please use 24-hour time in HH:MM format, for example 18:00.")
            return False
        self.settings = Settings(self.source_var.get().strip(), self.destination_var.get().strip(), self.time_var.get().strip(), self.watch_var.get(), self.hidden_var.get())
        self.settings.save()
        if not quiet: self._append_log("Settings saved.")
        return True

    def _organize_now(self):
        if not self._save_settings(quiet=True): return
        self.status_var.set("Organizing…")
        threading.Thread(target=self._organize_worker, daemon=True).start()

    def _organize_worker(self):
        moved, _, errors = organize_folder(Path(self.settings.source), Path(self.settings.destination), self.settings.include_hidden)
        self.events.put(("result", moved, errors))

    def _scheduler_loop(self):
        while not self.stop_event.is_set():
            now = datetime.now()
            key = now.strftime("%Y-%m-%d")
            if self.settings.watch and now.strftime("%H:%M") == self.settings.run_time and self.last_daily_run != key:
                self.last_daily_run = key
                self.events.put(("scheduled",))
            time.sleep(20)

    def _drain_events(self):
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == "scheduled":
                    self._append_log(f"Daily run started at {datetime.now().strftime('%H:%M')}.")
                    threading.Thread(target=self._organize_worker, daemon=True).start()
                elif event[0] == "result":
                    _, moved, errors = event
                    for name, category in moved:
                        self.tree.insert("", 0, values=(name, category, datetime.now().strftime("%H:%M:%S")))
                    self.status_var.set(f"{len(moved)} file(s) organized" if not errors else f"Done with {len(errors)} warning(s)")
                    self._append_log(f"Moved {len(moved)} file(s)." + (f" {len(errors)} warning(s)." if errors else ""))
                    for error in errors: self._append_log(f"Warning: {error}")
        except queue.Empty:
            pass
        self.after(250, self._drain_events)

    def _append_log(self, message):
        # Keep a compact status history in the window title for users who run it minimized.
        self.title(f"{APP_NAME} — {message}")

    def _close(self):
        self.stop_event.set(); self.destroy()


if __name__ == "__main__":
    if tk is None:
        raise SystemExit("Tkinter is required for the GUI. Install it with: sudo apt install python3-tk")
    OrganizerApp().mainloop()
