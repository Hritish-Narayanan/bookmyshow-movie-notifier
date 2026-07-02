"""Tkinter user interface for BookMyShow Movie Notifier."""

from __future__ import annotations

import threading
import time
import tkinter as tk
from dataclasses import dataclass
from queue import Empty, Queue
from datetime import datetime, timedelta
from tkinter import ttk

from .config import Config, load_config
from .notifier import format_notification, send_notification
from .utils import format_duration, pick_random_interval, setup_logger
from .watcher import check_once


@dataclass(slots=True)
class UiEvent:
    kind: str
    message: str


class QueueLogger:
    """Adapter that forwards log messages to the UI queue."""

    def __init__(self, queue: Queue[UiEvent], logger_name: str = "movie_watcher.gui") -> None:
        self.queue = queue
        self.logger = setup_logger("INFO")
        self.logger.name = logger_name

    def info(self, message: str, *args) -> None:
        self.queue.put(UiEvent("log", message % args if args else message))

    def exception(self, message: str, *args) -> None:
        self.queue.put(UiEvent("error", message % args if args else message))


class MovieWatcherApp(tk.Tk):
    """Fancy Tkinter front-end for the watcher."""

    def __init__(self) -> None:
        super().__init__()
        self.title("BookMyShow Movie Notifier")
        self.geometry("980x680")
        self.minsize(860, 600)
        self.configure(bg="#0f172a")

        self.config_data = load_config()
        self.event_queue: Queue[UiEvent] = Queue()
        self.worker: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.logger = QueueLogger(self.event_queue)
        self.next_check_at: datetime | None = None
        self.monitor_interval_seconds = 0

        self._build_styles()
        self._build_layout()
        self._pump_events()
        self.after(500, self.start_monitoring)

    def _build_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#0f172a")
        style.configure("Card.TFrame", background="#111827", relief="flat")
        style.configure("Title.TLabel", background="#0f172a", foreground="#f8fafc", font=("Segoe UI", 22, "bold"))
        style.configure("Subtitle.TLabel", background="#0f172a", foreground="#94a3b8", font=("Segoe UI", 10))
        style.configure("Section.TLabel", background="#111827", foreground="#e2e8f0", font=("Segoe UI", 11, "bold"))
        style.configure("Body.TLabel", background="#111827", foreground="#cbd5e1", font=("Segoe UI", 10))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 10))
        style.map("Accent.TButton", background=[("active", "#38bdf8")], foreground=[("active", "#0f172a")])
        style.configure("Dark.TButton", font=("Segoe UI", 10), padding=(12, 9))
        style.configure("TEntry", fieldbackground="#0b1220", background="#0b1220", foreground="#e2e8f0")

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=20)
        root.pack(fill="both", expand=True)

        header = ttk.Frame(root)
        header.pack(fill="x")
        ttk.Label(header, text="BookMyShow Movie Notifier", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Monitor BookMyShow and send ntfy alerts when theatres are added.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        body = ttk.Frame(root)
        body.pack(fill="both", expand=True, pady=(18, 0))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(1, weight=1)

        config_card = ttk.Frame(body, style="Card.TFrame", padding=18)
        config_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 12))
        actions_card = ttk.Frame(body, style="Card.TFrame", padding=18)
        actions_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 12))
        log_card = ttk.Frame(body, style="Card.TFrame", padding=18)
        log_card.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 0))

        self.status_var = tk.StringVar(value="Idle")
        self.next_check_var = tk.StringVar(value="Next check: not scheduled")
        self.url_var = tk.StringVar(value=self.config_data.bookmyshow_url)
        self.interval_var = tk.StringVar(
            value=f"{self.config_data.check_interval_min}s - {self.config_data.check_interval_max}s"
        )
        self.headless_var = tk.StringVar(value="Yes" if self.config_data.headless else "No")
        self.ntfy_var = tk.StringVar(value=self.config_data.ntfy_url)

        ttk.Label(config_card, text="Configuration", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        rows = [
            ("BookMyShow URL", self.url_var),
            ("Check interval", self.interval_var),
            ("Headless mode", self.headless_var),
            ("ntfy URL", self.ntfy_var),
        ]
        for index, (label, variable) in enumerate(rows, start=1):
            ttk.Label(config_card, text=label + ":", style="Body.TLabel").grid(row=index, column=0, sticky="w", pady=3)
            ttk.Label(config_card, textvariable=variable, style="Body.TLabel", wraplength=390).grid(
                row=index, column=1, sticky="w", pady=3, padx=(10, 0)
            )

        ttk.Label(actions_card, text="Actions", style="Section.TLabel").pack(anchor="w")
        ttk.Button(actions_card, text="Start Monitoring", style="Accent.TButton", command=self.start_monitoring).pack(
            fill="x", pady=(14, 8)
        )
        ttk.Button(actions_card, text="Stop Monitoring", style="Dark.TButton", command=self.stop_monitoring).pack(
            fill="x", pady=8
        )
        ttk.Button(actions_card, text="Run Check Now", style="Dark.TButton", command=self.run_check).pack(
            fill="x", pady=8
        )
        ttk.Button(actions_card, text="Dry Run", style="Dark.TButton", command=self.run_dry_run).pack(
            fill="x", pady=8
        )
        ttk.Button(actions_card, text="Force Notify", style="Dark.TButton", command=self.force_notify).pack(
            fill="x", pady=8
        )
        ttk.Label(actions_card, text="Status", style="Body.TLabel").pack(anchor="w", pady=(18, 0))
        ttk.Label(actions_card, textvariable=self.status_var, style="Section.TLabel").pack(anchor="w", pady=(4, 0))
        ttk.Label(actions_card, textvariable=self.next_check_var, style="Body.TLabel", wraplength=330).pack(
            anchor="w", pady=(8, 0)
        )

        ttk.Label(log_card, text="Activity Log", style="Section.TLabel").pack(anchor="w")
        self.log_text = tk.Text(
            log_card,
            height=14,
            bg="#020617",
            fg="#e2e8f0",
            insertbackground="#e2e8f0",
            relief="flat",
            font=("Consolas", 10),
            wrap="word",
        )
        self.log_text.pack(fill="both", expand=True, pady=(14, 0))
        self.log_text.configure(state="disabled")

    def _append_log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _pump_events(self) -> None:
        try:
            while True:
                event = self.event_queue.get_nowait()
                if event.kind == "log":
                    self._append_log(event.message)
                elif event.kind == "error":
                    self._append_log("ERROR: " + event.message)
                    self._set_status("Error")
                elif event.kind == "status":
                    self._set_status(event.message)
                elif event.kind == "next":
                    self.next_check_var.set(event.message)
        except Empty:
            pass
        self.after(120, self._pump_events)

    def _run_in_thread(self, target) -> None:
        if self.worker and self.worker.is_alive():
            return
        self.worker = threading.Thread(target=target, daemon=True)
        self.worker.start()

    def _default_config(self) -> Config:
        return self.config_data

    def _schedule_next_check(self) -> None:
        self.monitor_interval_seconds = pick_random_interval(
            self.config_data.check_interval_min,
            self.config_data.check_interval_max,
        )
        self.next_check_at = datetime.now() + timedelta(seconds=self.monitor_interval_seconds)
        self.next_check_var.set(f"Next check in {format_duration(self.monitor_interval_seconds)}.")

    def _refresh_countdown(self) -> None:
        if self.stop_event.is_set() or self.next_check_at is None:
            return
        remaining = max(0, int((self.next_check_at - datetime.now()).total_seconds()))
        if remaining == 0:
            self.next_check_var.set("Next check due now.")
        else:
            self.next_check_var.set(f"Next check in {format_duration(remaining)}.")
        self.after(1000, self._refresh_countdown)

    def start_monitoring(self) -> None:
        if self.worker and self.worker.is_alive():
            return
        self.stop_event.clear()
        self._set_status("Monitoring")
        self.event_queue.put(UiEvent("log", "Application started from GUI"))
        self._schedule_next_check()
        self._refresh_countdown()
        self._run_in_thread(self._monitor_loop)

    def stop_monitoring(self) -> None:
        self.stop_event.set()
        self._set_status("Stopped")
        self.event_queue.put(UiEvent("log", "Monitoring stopped"))

    def run_check(self) -> None:
        self._set_status("Checking now")
        self._run_in_thread(lambda: self._one_shot(dry_run=False))

    def run_dry_run(self) -> None:
        self._set_status("Dry run")
        self._run_in_thread(lambda: self._one_shot(dry_run=True))

    def force_notify(self) -> None:
        self._set_status("Sending notification")
        self._run_in_thread(self._force_notify_worker)

    def _one_shot(self, dry_run: bool) -> None:
        try:
            check_once(self._default_config(), self.logger, dry_run=dry_run)
            self.event_queue.put(UiEvent("status", "Idle"))
        except Exception as exc:
            self.event_queue.put(UiEvent("error", str(exc)))

    def _force_notify_worker(self) -> None:
        try:
            notification = format_notification(["Test Theatre"], click_url=self.config_data.bookmyshow_url)
            send_notification(self.config_data.ntfy_url, notification, self.logger.logger, dry_run=False)
            self.event_queue.put(UiEvent("log", "Force notification sent"))
            self.event_queue.put(UiEvent("status", "Idle"))
        except Exception as exc:
            self.event_queue.put(UiEvent("error", str(exc)))

    def _monitor_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                check_once(self._default_config(), self.logger, dry_run=False)
            except Exception as exc:
                self.event_queue.put(UiEvent("error", f"Monitoring error: {exc}"))
            delay = self.monitor_interval_seconds
            self.event_queue.put(UiEvent("next", f"Next check in {format_duration(delay)}."))
            self._schedule_next_check()
            for _ in range(delay):
                if self.stop_event.is_set():
                    break
                time.sleep(1)


def launch_gui() -> None:
    """Start the Tkinter application."""
    app = MovieWatcherApp()
    app.mainloop()
