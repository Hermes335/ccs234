"""Tkinter desktop UI. Workers communicate exclusively through a queue."""
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .core import recommendations, statistics
from .network import discover, local_interfaces, ping
from .reports import save_report, snapshot, text_report, value


class MonitorApp:
    def __init__(self, root):
        self.root = root
        root.title("CCS 234 | Network Monitor")
        root.geometry("1140x780")
        root.minsize(1100, 700)
        root.configure(bg="#eef2f6")
        self.events = queue.Queue()
        self.stop = threading.Event()
        self.busy = False
        self.closed = False
        self.interfaces, self.runs, self.discovery = [], [], None
        self.actions = []
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TFrame", background="#eef2f6")
        style.configure("TLabel", background="#eef2f6", foreground="#17283b", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 23, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 8))
        style.configure("TNotebook.Tab", padding=(12, 10), font=("Segoe UI", 10))
        style.configure("Treeview", rowheight=29, font=("Segoe UI", 10))
        top = ttk.Frame(root, padding=(24, 18))
        top.pack(fill="x")
        ttk.Label(top, text="Network Monitor", style="Title.TLabel").pack(anchor="w")
        ttk.Label(top, text="CCS 234   /   Discover devices, test connectivity, review evidence").pack(anchor="w", pady=(5, 0))
        self.book = ttk.Notebook(root)
        self.tabs = {}
        for title in ["Dashboard", "Network Discovery", "Connectivity Testing", "Network Statistics", "Report Generator", "Security Recommendations"]:
            frame = ttk.Frame(self.book, padding=18)
            self.book.add(frame, text=title)
            self.tabs[title] = frame
        self.status = tk.StringVar(value="Ready. No probes run. Confirm your authorized network before testing.")
        bottom = ttk.Frame(root, padding=(20, 12))
        bottom.pack(side="bottom", fill="x")
        self.book.pack(fill="both", expand=True, padx=20)
        ttk.Label(bottom, textvariable=self.status, wraplength=890).pack(side="left")
        self.cancel_button = ttk.Button(bottom, text="Cancel operation", command=self.stop.set, state="disabled")
        self.cancel_button.pack(side="right")
        self.build_dashboard()
        self.build_discovery()
        self.build_ping()
        self.stats_text = self.text_box(self.tabs["Network Statistics"])
        self.build_reports()
        self.advice_text = self.text_box(self.tabs["Security Recommendations"])
        self.refresh_views()
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.poll_id = root.after(80, self.poll)

    def button(self, parent, text, command):
        button = ttk.Button(parent, text=text, command=command)
        self.actions.append(button)
        return button

    def text_box(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, pady=8)
        box = tk.Text(frame, wrap="word", font=("Consolas", 10), padx=15, pady=15,
                      bg="white", fg="#17283b", relief="flat", state="disabled")
        scrollbar = ttk.Scrollbar(frame, command=box.yview)
        box.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        box.pack(fill="both", expand=True)
        return box

    @staticmethod
    def write(box, content):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", content)
        box.configure(state="disabled")

    def build_dashboard(self):
        tab = self.tabs["Dashboard"]
        ttk.Label(tab, text="Local adapter and authorized scope", font=("Segoe UI", 15, "bold")).pack(anchor="w")
        ttk.Label(tab, text="Refresh reads local configuration only. No discovery runs automatically.").pack(anchor="w", pady=6)
        row = ttk.Frame(tab)
        row.pack(fill="x", pady=8)
        self.button(row, "Refresh local adapters", self.refresh_adapters).pack(side="left")
        self.adapter = ttk.Combobox(row, state="readonly", width=65)
        self.adapter.pack(side="left", padx=12)
        self.adapter.bind("<<ComboboxSelected>>", self.select_adapter)
        self.local_text = tk.StringVar(value="No adapter information collected.")
        ttk.Label(tab, textvariable=self.local_text, wraplength=990).pack(anchor="w", pady=12)
        self.authorized = tk.BooleanVar(value=False)
        ttk.Checkbutton(tab, text="I confirm this is my home/authorized network and I may test the selected subnet and targets.",
                        variable=self.authorized).pack(anchor="w", pady=12)
        ttk.Label(tab, text="Do not enable this on public, university, workplace or guest networks without explicit permission.\n"
                  "Discovery is limited to the selected IPv4 adapter subnet, at most 256 addresses and 4 packets per target.\n"
                  "IP addresses and hostnames stay local unless you choose to share a saved report.", wraplength=990).pack(anchor="w", pady=10)
        self.dashboard_text = self.text_box(tab)

    def build_discovery(self):
        tab = self.tabs["Network Discovery"]
        ttk.Label(tab, text="Discover responding devices", font=("Segoe UI", 15, "bold")).pack(anchor="w")
        ttk.Label(tab, text="ICMP filtering can hide active devices. This is a sample, not a complete device inventory.").pack(anchor="w", pady=8)
        row = ttk.Frame(tab)
        row.pack(fill="x", pady=8)
        ttk.Label(row, text="Subnet").pack(side="left")
        self.scope = tk.StringVar()
        ttk.Entry(row, textvariable=self.scope, width=25).pack(side="left", padx=8)
        self.button(row, "Discover devices", self.start_discovery).pack(side="left")
        self.button(row, "Test selected device", self.choose_device).pack(side="left", padx=8)
        device_frame = ttk.Frame(tab)
        device_frame.pack(fill="both", expand=True, pady=12)
        self.devices = ttk.Treeview(device_frame, columns=("ip", "host", "mean", "loss"), show="headings")
        for column, heading in [("ip", "IPv4 address"), ("host", "Hostname when available"), ("mean", "Average RTT (ms)"), ("loss", "Loss (%)")]:
            self.devices.heading(column, text=heading)
            self.devices.column(column, width=210)
        device_scroll = ttk.Scrollbar(device_frame, command=self.devices.yview)
        self.devices.configure(yscrollcommand=device_scroll.set)
        device_scroll.pack(side="right", fill="y")
        self.devices.pack(fill="both", expand=True)
        self.devices.bind("<Double-1>", lambda event: self.choose_device())

    def build_ping(self):
        tab = self.tabs["Connectivity Testing"]
        ttk.Label(tab, text="Bounded connectivity test", font=("Segoe UI", 15, "bold")).pack(anchor="w")
        row = ttk.Frame(tab)
        row.pack(fill="x", pady=14)
        ttk.Label(row, text="IPv4 or hostname").pack(side="left")
        self.target = tk.StringVar()
        ttk.Entry(row, textvariable=self.target, width=32).pack(side="left", padx=8)
        ttk.Label(row, text="Packets").pack(side="left")
        self.count = tk.StringVar(value="4")
        ttk.Spinbox(row, from_=1, to=4, textvariable=self.count, width=4).pack(side="left", padx=8)
        self.button(row, "Run ping test", self.start_ping).pack(side="left", padx=8)
        ttk.Label(tab, text="800 ms timeout per probe. Hostnames must resolve inside the selected local subnet.\n"
                  "Windows reports whole milliseconds; a 0 ms reply is below timer resolution.").pack(anchor="w")
        self.ping_text = self.text_box(tab)

    def build_reports(self):
        tab = self.tabs["Report Generator"]
        row = ttk.Frame(tab)
        row.pack(fill="x")
        self.button(row, "Save report (TXT / JSON / PDF)", self.export).pack(side="left")
        ttk.Label(row, text="Reports contain local addresses. Review before sharing.").pack(side="left", padx=14)
        self.report_text = self.text_box(tab)

    def selected_interface(self):
        i = self.adapter.current()
        if i < 0 or i >= len(self.interfaces):
            raise ValueError("Refresh and select a local adapter on the Dashboard first.")
        return self.interfaces[i]

    def select_adapter(self, _event=None):
        item = self.selected_interface()
        self.scope.set(item["network"])
        self.authorized.set(False)
        self.local_text.set(f"Host: {item['hostname']}     IP: {item['ip']}     Mask: {item['netmask']}     Network: {item['network']}")

    def refresh_adapters(self):
        self.launch("adapters", local_interfaces)

    def launch(self, kind, function):
        if self.busy:
            return
        self.busy = True
        self.stop.clear()
        for button in self.actions:
            button.configure(state="disabled")
        self.adapter.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.status.set(f"Working: {kind}. You can continue viewing tabs or cancel.")
        def worker():
            try:
                self.events.put((kind, function()))
            except Exception as exc:
                self.events.put(("error", f"{type(exc).__name__}: {exc}"))
        threading.Thread(target=worker, daemon=True).start()

    def start_discovery(self):
        try:
            interface = self.selected_interface()
            cidr, authorized = self.scope.get(), self.authorized.get()
            if not authorized:
                raise PermissionError("Confirm the authorized home network on the Dashboard.")
            self.launch("discovery", lambda: discover(cidr, authorized=authorized,
                local_network=interface["network"], cancel=self.stop,
                progress=lambda done, total: self.events.put(("progress", f"Discovery: {done}/{total} targets completed"))))
        except (ValueError, PermissionError) as exc:
            messagebox.showerror("Cannot start discovery", str(exc))

    def start_ping(self):
        try:
            interface = self.selected_interface()
            target, count, authorized = self.target.get(), int(self.count.get()), self.authorized.get()
            if not authorized:
                raise PermissionError("Confirm the authorized home network on the Dashboard.")
            self.launch("ping", lambda: ping(target, authorized=authorized,
                allowed_network=interface["network"], count=count, cancel=self.stop))
        except (ValueError, PermissionError) as exc:
            messagebox.showerror("Cannot start ping", str(exc))

    def choose_device(self):
        selected = self.devices.selection()
        if selected:
            self.target.set(self.devices.item(selected[0], "values")[0])
            self.book.select(self.tabs["Connectivity Testing"])

    def poll(self):
        if self.closed:
            return
        try:
            while True:
                kind, result = self.events.get_nowait()
                if kind == "progress":
                    self.status.set(result)
                    continue
                self.busy = False
                for button in self.actions:
                    button.configure(state="normal")
                self.adapter.configure(state="readonly")
                self.cancel_button.configure(state="disabled")
                self.status.set(f"Completed: {kind}.")
                if kind == "error":
                    self.status.set(result)
                    messagebox.showerror("Operation failed", result)
                elif kind == "adapters":
                    self.interfaces = result
                    self.authorized.set(False)
                    self.adapter["values"] = [f"{x['adapter']}  /  {x['ip']}  /  {x['network']}" for x in result]
                    if result:
                        preferred = next((i for i, x in enumerate(result) if "wi-fi" in x["adapter"].lower()), 0)
                        self.adapter.current(preferred)
                        self.select_adapter()
                    else:
                        self.adapter.set("")
                        self.scope.set("")
                        self.local_text.set("No active IPv4 adapters found.")
                elif kind == "discovery":
                    self.discovery = result
                    self.devices.delete(*self.devices.get_children())
                    for run in result.devices:
                        s = statistics(run.probes)
                        self.devices.insert("", "end", values=(run.ip, run.hostname or "Unavailable", value(s["average_ms"]), value(s["loss_percent"])))
                    self.status.set(f"Discovery {'cancelled' if result.cancelled else 'complete'}: {len(result.devices)} responding / {len(result.runs)} tested.")
                elif kind == "ping":
                    self.runs.append(result)
                    self.status.set(f"Ping {'cancelled' if result.cancelled else 'complete'}: {statistics(result.probes)['status']}.")
                self.refresh_views()
        except queue.Empty:
            pass
        self.poll_id = self.root.after(80, self.poll)

    def refresh_views(self):
        last = self.runs[-1] if self.runs else None
        self.write(self.dashboard_text,
                   f"Responding devices: {len(self.discovery.devices) if self.discovery else 'Not scanned'}\n\n"
                   f"Connectivity sessions: {len(self.runs)}\n\n"
                   f"Latest status: {statistics(last.probes)['status'] if last else 'Not measured'}\n\n"
                   "Workflow: select an adapter and confirm scope, discover devices, run a bounded test, then save the report.\n\n"
                   "No scanning starts when the application opens.")
        data = snapshot(self.interfaces, self.discovery, self.runs)
        self.write(self.report_text, text_report(data))
        self.write(self.advice_text, "\n\n".join(recommendations(last)))
        if last:
            s = statistics(last.probes)
            self.write(self.stats_text, f"Target: {last.target}\nHostname: {last.hostname or 'Unavailable'}\nIPv4: {last.ip}\n"
                       f"Measured: {last.started_at}\nProvenance: {last.provenance}\n\n"
                       f"Average latency: {value(s['average_ms'], ' ms')}\nMaximum latency: {value(s['maximum_ms'], ' ms')}\n"
                       f"Packet loss: {value(s['loss_percent'], '%')}\nReplies: {s['received']} / {s['attempted']}\n"
                       f"Local errors: {s['local_errors']}\nStatus: {s['status']}\n\n"
                       "Latency uses replies only. Loss excludes unconfirmed local errors.\n"
                       "A missing value stays N/A; a 0 ms measured reply is below timer resolution.")
            self.write(self.ping_text, "\n".join(f"#{p.sequence}  {p.status:<12} {value(p.latency_ms, ' ms')}\n{p.detail}\n" for p in last.probes))
        else:
            self.write(self.stats_text, "No connectivity test yet.\n\nHostname: N/A\nIP address: N/A\nAverage latency: N/A\nMaximum latency: N/A\nPacket loss: N/A")
            self.write(self.ping_text, "No probes sent. Select an authorized target to begin.")

    def export(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="network_report.txt",
                 filetypes=[("Text report", "*.txt"), ("JSON evidence", "*.json"), ("PDF report", "*.pdf")])
        if path:
            data = snapshot(self.interfaces, self.discovery, self.runs)
            self.launch("report saved", lambda: save_report(path, data))

    def close(self):
        self.closed = True
        self.stop.set()
        self.root.after_cancel(self.poll_id)
        self.root.destroy()


def main():
    root = tk.Tk()
    MonitorApp(root)
    root.mainloop()
