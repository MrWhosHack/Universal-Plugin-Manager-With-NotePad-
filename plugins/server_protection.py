"""
Server Protection Plugin
Real-time lightweight monitoring: system metrics, rule file integrity, process scan, report export.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import platform
import json
import hashlib
from pathlib import Path
from datetime import datetime
import threading
import time

RULES_DIR = Path("NotePad++ rules")
BASELINE_FILE = Path("plugins/server_protection_baseline.json")
REPORT_DIR = Path(".")
CPU_WARN = 85.0
MEM_WARN = 80.0
DISK_WARN = 85.0
TOP_PROCESS_LIMIT = 10
REFRESH_INTERVAL_SECONDS = 5

class Plugin:
    def __init__(self, parent_frame, app):
        self.parent = parent_frame
        self.app = app
        self.tab_name = "Server Protection"
        self.metrics_running = True
        self.baseline = {}
        self.events = []  # rolling log
        # Build UI first so logging and widgets are available
        self._build_ui()
        # Load baseline after UI exists so _log() can write to the event log
        self._load_baseline()
        # Start metrics/refresh loop
        self._start_refresh_loop()

    # ---------- UI ----------
    def _build_ui(self):
        header = tk.Frame(self.parent, bg='#2a2a4e', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text="🛡 SERVER PROTECTION DASHBOARD", bg='#2a2a4e', fg='#00ffff',
                 font=('Segoe UI', 16, 'bold')).pack(side='left', padx=20)
        tk.Button(header, text="Generate Report", bg='#00ff88', fg='#1a1a2e', bd=0,
                  font=('Segoe UI', 11, 'bold'), command=self.generate_report).pack(side='right', padx=10, pady=10)
        tk.Button(header, text="Rebuild Baseline", bg='#ffaa00', fg='#1a1a2e', bd=0,
                  font=('Segoe UI', 11, 'bold'), command=self.rebuild_baseline).pack(side='right', padx=10, pady=10)

        body = tk.Frame(self.parent, bg='#1a1a2e')
        body.pack(fill='both', expand=True, padx=15, pady=15)

        # Metrics frame
        metrics_frame = tk.LabelFrame(body, text="Live Metrics", bg='#1a1a2e', fg='#00ffff', padx=10, pady=10)
        metrics_frame.pack(fill='x')
        self.cpu_var = tk.StringVar()
        self.mem_var = tk.StringVar()
        self.disk_var = tk.StringVar()
        self.integrity_var = tk.StringVar()
        tk.Label(metrics_frame, textvariable=self.cpu_var, bg='#1a1a2e', fg='#ffffff', font=('Consolas', 11)).pack(anchor='w')
        tk.Label(metrics_frame, textvariable=self.mem_var, bg='#1a1a2e', fg='#ffffff', font=('Consolas', 11)).pack(anchor='w')
        tk.Label(metrics_frame, textvariable=self.disk_var, bg='#1a1a2e', fg='#ffffff', font=('Consolas', 11)).pack(anchor='w')
        tk.Label(metrics_frame, textvariable=self.integrity_var, bg='#1a1a2e', fg='#ffffff', font=('Consolas', 11)).pack(anchor='w')

        # Process frame
        proc_frame = tk.LabelFrame(body, text="Top Processes", bg='#1a1a2e', fg='#00ffff', padx=10, pady=10)
        proc_frame.pack(fill='both', expand=True, pady=(15,0))
        self.proc_list = tk.Listbox(proc_frame, height=12, bg='#0f0f1a', fg='#d4d4d4', font=('Consolas', 10))
        self.proc_list.pack(fill='both', expand=True)

        # Event log
        log_frame = tk.LabelFrame(body, text="Event Log", bg='#1a1a2e', fg='#00ffff', padx=10, pady=10)
        log_frame.pack(fill='both', expand=True, pady=(15,0))
        self.log_text = tk.Text(log_frame, height=10, bg='#0f0f1a', fg='#aaaaaa', font=('Consolas', 9))
        self.log_text.pack(fill='both', expand=True)
        self.log_text.config(state='disabled')

        self._log("INFO", "Server Protection UI initialized")

    # ---------- Baseline / Integrity ----------
    def _hash_file(self, path: Path):
        try:
            data = path.read_bytes()
            return hashlib.sha256(data).hexdigest()
        except Exception:
            return None

    def _collect_rule_hashes(self):
        hashes = {}
        if RULES_DIR.exists():
            for f in RULES_DIR.glob("*.md"):  # monitor policy markdown
                h = self._hash_file(f)
                if h:
                    hashes[f.name] = h
            # also watch the protection guidelines txt
            txt = RULES_DIR / "SERVER_PROTECTION_APPLICATION.txt"
            if txt.exists():
                h = self._hash_file(txt)
                if h:
                    hashes[txt.name] = h
        return hashes

    def _load_baseline(self):
        if BASELINE_FILE.exists():
            try:
                self.baseline = json.loads(BASELINE_FILE.read_text(encoding='utf-8'))
                self._log("INFO", "Baseline loaded")
            except Exception:
                self.baseline = {}
                self._log("WARN", "Failed to load baseline; starting empty")
        else:
            self.baseline = {}
            self._log("INFO", "No baseline file; will create on first rebuild")

    def rebuild_baseline(self):
        self.baseline = self._collect_rule_hashes()
        try:
            BASELINE_FILE.write_text(json.dumps(self.baseline, indent=2), encoding='utf-8')
            self._log("INFO", f"Baseline rebuilt ({len(self.baseline)} items)")
            messagebox.showinfo("Baseline", "Integrity baseline rebuilt successfully.")
        except Exception as e:
            self._log("CRITICAL", f"Baseline write failed: {e}")
            messagebox.showerror("Baseline Error", str(e))

    def _integrity_status(self):
        current = self._collect_rule_hashes()
        missing = []
        changed = []
        new = []
        for name, hashv in self.baseline.items():
            if name not in current:
                missing.append(name)
            elif current[name] != hashv:
                changed.append(name)
        for name in current.keys():
            if name not in self.baseline:
                new.append(name)
        status = []
        if not self.baseline:
            status.append("NO BASELINE")
        if missing:
            status.append(f"MISSING:{len(missing)}")
        if changed:
            status.append(f"CHANGED:{len(changed)}")
        if new:
            status.append(f"NEW:{len(new)}")
        if not status:
            status.append("OK")
        level = "INFO"
        if missing or changed:
            level = "ALERT"
        elif new:
            level = "WARN"
        if level != "INFO":
            self._log(level, f"Integrity anomalies -> missing={missing} changed={changed} new={new}")
        return ", ".join(status)

    # ---------- Metrics Loop ----------
    def _start_refresh_loop(self):
        def loop():
            while self.metrics_running:
                try:
                    self._refresh_metrics()
                except Exception as e:
                    self._log("WARN", f"Metrics refresh error: {e}")
                time.sleep(REFRESH_INTERVAL_SECONDS)
        threading.Thread(target=loop, daemon=True).start()

    def _refresh_metrics(self):
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage(Path('.')).percent
        integrity = self._integrity_status()

        self.cpu_var.set(f"CPU Usage: {cpu:.1f}%")
        self.mem_var.set(f"Memory Usage: {mem:.1f}%")
        self.disk_var.set(f"Disk Usage: {disk:.1f}%")
        self.integrity_var.set(f"Integrity: {integrity}")

        if cpu > CPU_WARN:
            self._log("WARN", f"High CPU {cpu:.1f}%")
        if mem > MEM_WARN:
            self._log("WARN", f"High Memory {mem:.1f}%")
        if disk > DISK_WARN:
            self._log("WARN", f"High Disk {disk:.1f}%")
        self._refresh_process_list()

    def _refresh_process_list(self):
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = p.info
                procs.append(info)
            except Exception:
                pass
        # Sort by memory
        procs.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
        top = procs[:TOP_PROCESS_LIMIT]
        self.proc_list.delete(0, tk.END)
        for pr in top:
            name = pr.get('name') or '???'
            cpu = pr.get('cpu_percent', 0.0)
            mem = pr.get('memory_percent', 0.0)
            mark = ''
            if cpu > CPU_WARN or mem > MEM_WARN:
                mark = '!'
            self.proc_list.insert(tk.END, f"{mark}{name} (PID {pr['pid']}) CPU:{cpu:.1f}% MEM:{mem:.1f}%")

    # ---------- Reporting ----------
    def generate_report(self):
        ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = REPORT_DIR / f"server_protection_report_{ts}.txt"
        try:
            cpu = self.cpu_var.get()
            mem = self.mem_var.get()
            disk = self.disk_var.get()
            integrity = self.integrity_var.get()
            sysinfo = f"OS={platform.system()} {platform.release()} | Python={platform.python_version()} | Cores={psutil.cpu_count()}"
            lines = [
                "SERVER PROTECTION REPORT",
                f"Timestamp UTC: {ts}",
                sysinfo,
                cpu,
                mem,
                disk,
                integrity,
                "", "Top Processes:" ]
            for i in range(self.proc_list.size()):
                lines.append(self.proc_list.get(i))
            lines.append("\nRecent Events:")
            for lvl, msg, t in self.events[-50:]:
                lines.append(f"[{t}] {lvl} {msg}")
            filename.write_text("\n".join(lines), encoding='utf-8')
            self._log("INFO", f"Report generated: {filename.name}")
            messagebox.showinfo("Report", f"Protection report saved to {filename}")
        except Exception as e:
            self._log("CRITICAL", f"Report generation failed: {e}")
            messagebox.showerror("Report Error", str(e))

    # ---------- Logging ----------
    def _log(self, level, message):
        ts = datetime.utcnow().strftime('%H:%M:%S')
        self.events.append((level, message, ts))
        # keep log short
        if len(self.events) > 250:
            self.events = self.events[-250:]
        self.log_text.config(state='normal')
        self.log_text.insert('end', f"[{ts}] {level}: {message}\n")
        self.log_text.see('end')
        self.log_text.config(state='disabled')
        # update status bar lightly
        if level in ("ALERT", "CRITICAL"):
            self.app.status_label.config(text=f"{level}: {message}")

    # ---------- Cleanup ----------
    def cleanup(self):
        self.metrics_running = False
        self._log("INFO", "Server Protection plugin stopped")
