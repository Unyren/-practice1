from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from .config import OrganizeConfig
from .runner import run_organizer


class OrganizerGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("MP3 Organizer")
        self.geometry("780x600")
        self._create_widgets()

    def _create_widgets(self) -> None:
        padding = {"padx": 8, "pady": 6}

        frame = ttk.Frame(self)
        frame.pack(fill="x", **padding)

        ttk.Label(frame, text="Source Folder:").grid(row=0, column=0, sticky="w")
        self.source_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.source_var, width=70).grid(row=0, column=1, sticky="ew")
        ttk.Button(frame, text="Browse", command=self._browse_source).grid(row=0, column=2)

        ttk.Label(frame, text="Destination Folder:").grid(row=1, column=0, sticky="w")
        self.dest_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.dest_var, width=70).grid(row=1, column=1, sticky="ew")
        ttk.Button(frame, text="Browse", command=self._browse_destination).grid(row=1, column=2)

        ttk.Label(frame, text="Mode:").grid(row=2, column=0, sticky="w")
        self.mode_var = tk.StringVar(value="copy")
        ttk.Combobox(frame, textvariable=self.mode_var, values=["copy", "move"], state="readonly", width=12).grid(row=2, column=1, sticky="w")

        ttk.Label(frame, text="Duplicate Strategy:").grid(row=3, column=0, sticky="w")
        self.duplicate_var = tk.StringVar(value="rename")
        ttk.Combobox(
            frame,
            textvariable=self.duplicate_var,
            values=["rename", "skip", "overwrite"],
            state="readonly",
            width=12,
        ).grid(row=3, column=1, sticky="w")

        ttk.Label(frame, text="Template:").grid(row=4, column=0, sticky="w")
        self.template_var = tk.StringVar(value="genre/{genre}/{artist}")
        ttk.Entry(frame, textvariable=self.template_var, width=70).grid(row=4, column=1, columnspan=2, sticky="ew")

        ttk.Label(frame, text="Fallback Folder:").grid(row=5, column=0, sticky="w")
        self.fallback_var = tk.StringVar(value="unknown")
        ttk.Entry(frame, textvariable=self.fallback_var, width=30).grid(row=5, column=1, sticky="w")

        ttk.Label(frame, text="Exclude Patterns:").grid(row=6, column=0, sticky="w")
        self.exclude_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.exclude_var, width=70).grid(row=6, column=1, columnspan=2, sticky="ew")

        self.dry_run_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Dry run", variable=self.dry_run_var).grid(row=7, column=0, sticky="w")

        self.verbose_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Verbose logging", variable=self.verbose_var).grid(row=7, column=1, sticky="w")

        ttk.Button(self, text="Start", command=self._start_organizer).pack(pady=8)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status_var).pack(fill="x", padx=8)

        self.log_text = tk.Text(self, wrap="word", height=20, state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _browse_source(self) -> None:
        selected = filedialog.askdirectory(title="Select source folder")
        if selected:
            self.source_var.set(selected)

    def _browse_destination(self) -> None:
        selected = filedialog.askdirectory(title="Select destination folder")
        if selected:
            self.dest_var.set(selected)

    def _append_log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)

    def _start_organizer(self) -> None:
        source = self.source_var.get().strip()
        destination = self.dest_var.get().strip()
        if not source or not destination:
            self._append_log("Source and destination folders are required.")
            return

        config = OrganizeConfig(
            source=Path(source),
            destination=Path(destination),
            mode=self.mode_var.get(),
            template=self.template_var.get(),
            fallback_dir=self.fallback_var.get() or "unknown",
            duplicate_strategy=self.duplicate_var.get(),
            dry_run=self.dry_run_var.get(),
            exclude_patterns=[pattern.strip() for pattern in self.exclude_var.get().split(",") if pattern.strip()],
            workers=1,
            verbose=self.verbose_var.get(),
        )

        self._append_log("Starting organizer...")
        self._set_status("Running")
        self._set_controls_state("disabled")

        thread = threading.Thread(target=self._run_worker, args=(config,), daemon=True)
        thread.start()

    def _run_worker(self, config: OrganizeConfig) -> None:
        try:
            run_organizer(config, progress_callback=self._gui_callback)
        except Exception as exc:
            self.after(0, lambda: self._append_log(f"Unhandled error: {exc}"))
        finally:
            self.after(0, lambda: self._set_status("Completed"))
            self.after(0, lambda: self._set_controls_state("normal"))

    def _gui_callback(self, message: str) -> None:
        self.after(0, lambda: self._append_log(message))

    def _set_controls_state(self, state: str) -> None:
        for child in self.winfo_children():
            if isinstance(child, ttk.Frame):
                for grandchild in child.winfo_children():
                    try:
                        grandchild.configure(state=state)
                    except tk.TclError:
                        pass
        try:
            self.log_text.configure(state=state if state == "normal" else "disabled")
        except tk.TclError:
            pass
