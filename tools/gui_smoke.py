"""Offline integration exercise of real widgets and queue, with mocked data."""
import json
from pathlib import Path
import tkinter as tk
from netmonitor.gui import MonitorApp
from netmonitor.core import PingRun, Probe

root = tk.Tk()
app = MonitorApp(root)
root.update()
assert len(app.book.tabs()) == 6
assert not app.busy and not app.authorized.get()
assert 'N/A' in app.stats_text.get('1.0', 'end')
fixture = PingRun('mock-device', '192.0.2.1', [Probe(1, 'reply', 20), Probe(2, 'timeout')], provenance='mocked')
app.events.put(('ping', fixture))
app.poll()
assert '50.00%' in app.stats_text.get('1.0', 'end')
assert 'mocked' in app.report_text.get('1.0', 'end')
assert 'Weak connectivity' in app.advice_text.get('1.0', 'end')
app.runs.clear()
app.refresh_views()
assert 'No probes sent' in app.ping_text.get('1.0', 'end')
folder = Path('Evidence/offline')
folder.mkdir(parents=True, exist_ok=True)
(folder/'gui-smoke.json').write_text(json.dumps({'result':'passed','checks':['six tabs','no automatic probing','empty statistics','worker queue presentation','mocked provenance','rule display','clear state'], 'network_access':False}, indent=2))
print('Offline GUI integration passed; 7 checks, no network access.', flush=True)
app.close()
