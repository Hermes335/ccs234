"""Capture actual Tkinter windows displaying saved genuine measurements.

No probes are sent by this script. Screenshots are application evidence with
recorded live data, not a recording of the discovery operation itself.
"""
import ctypes
import json
from pathlib import Path
import tkinter as tk
from PIL import ImageGrab
from netmonitor.gui import MonitorApp
from netmonitor.core import PingRun, Probe
from netmonitor.network import Discovery

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except (OSError, AttributeError):
    pass
root = tk.Tk()
app = MonitorApp(root)
root.geometry('1140x780+20+20')
root.deiconify()
root.attributes('-topmost', True)
out = Path('Evidence/screenshots')
out.mkdir(parents=True, exist_ok=True)

def capture(name):
    root.update_idletasks()
    root.update()
    x, y = root.winfo_rootx(), root.winfo_rooty()
    ImageGrab.grab(bbox=(x, y, x+root.winfo_width(), y+root.winfo_height())).save(out/name)

def restore_run(data):
    return PingRun(data['target'], data['ip'], [Probe(**p) for p in data['probes']],
                   hostname=data['hostname'], started_at=data['started_at'], provenance=data['provenance'],
                   requested_count=data['requested_count'], cancelled=data['cancelled'])

def phase1():
    capture('01-startup-unmeasured.png')
    data = json.loads(Path('Evidence/live/network-report.json').read_text(encoding='utf-8'))
    d = data['discovery']
    discovery = Discovery(d['network'], [restore_run(r) for r in d['all_results']],
                          started_at=d['started_at'], cancelled=d['cancelled'])
    app.events.put(('adapters', data['interfaces']))
    app.events.put(('discovery', discovery))
    app.events.put(('ping', restore_run(data['ping_runs'][0])))
    root.after(500, phase2)

def phase2():
    app.status.set('Evidence review: saved live measurements from 2026-10-27. No new probes sent by this capture helper.')
    app.book.select(app.tabs['Network Discovery'])
    root.after(400, phase3)

def phase3():
    capture('02-discovery-recorded-live.png')
    app.book.select(app.tabs['Network Statistics'])
    root.after(400, phase4)

def phase4():
    capture('03-statistics-recorded-live.png')
    app.book.select(app.tabs['Connectivity Testing'])
    root.after(400, phase5)

def phase5():
    capture('04-probes-recorded-live.png')
    app.book.select(app.tabs['Security Recommendations'])
    root.after(400, phase6)

def phase6():
    capture('05-recommendations-recorded-live.png')
    (out/'PROVENANCE.txt').write_text('Actual Tkinter window captures. 01 shows unmeasured startup. 02-05 display the saved genuine live capture from Evidence/live/network-report.json through the application worker-event presentation path. No data was invented and no additional probes were sent for screenshots. Captured with PIL ImageGrab because the Computer Use native pipe was unavailable.\n', encoding='utf-8')
    print('Captured five actual application images.', flush=True)
    app.close()

root.after(1200, phase1)
root.mainloop()
