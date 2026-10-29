"""One authorized capture; never invoked by the automated test suite."""
import json
from pathlib import Path
from netmonitor.network import discover, local_interfaces
from netmonitor.reports import snapshot, save_report
from netmonitor.core import statistics, timestamp

folder = Path('Evidence/live')
folder.mkdir(parents=True, exist_ok=True)
interfaces = local_interfaces()
wifi = next(x for x in interfaces if x['adapter'] == 'Wi-Fi')
# Fail closed if the adapter changed since the user's scope confirmation.
if wifi['network'] != '192.168.254.0/24':
    raise SystemExit('Adapter subnet changed: obtain scope confirmation before capture.')
consent = {
    'recorded_at': timestamp(),
    'source': 'Explicit user confirmation in this conversation on 2026-10-27',
    'network_name': 'GlobeAtHome_712d0',
    'windows_profile': 'Public; user explicitly confirmed this is the authorized home network',
    'scope': wifi['network'],
    'per_target_packets': 4,
    'restrictions': 'Local ICMP discovery only; no intrusive scanning or other networks',
    'interface': wifi,
}
(folder/'authorization.json').write_text(json.dumps(consent, indent=2), encoding='utf-8')
print('Starting authorized bounded discovery at', timestamp(), flush=True)
def progress(done, total):
    if done % 20 == 0 or done == total:
        print(f'{done}/{total} targets complete', flush=True)
result = discover(wifi['network'], authorized=True, local_network=wifi['network'], progress=progress)
router_runs = [r for r in result.runs if r.ip == '192.168.254.254']
data = snapshot(interfaces, result, router_runs)
for suffix in ['json', 'txt', 'pdf']:
    save_report(folder/f'network-report.{suffix}', data)
summary = {
    'started_at': result.started_at, 'finished_at': timestamp(),
    'tested': len(result.runs), 'responding': len(result.devices),
    'router': statistics(router_runs[0].probes) if router_runs else None,
    'local_errors': sum(statistics(r.probes)['local_errors'] for r in result.runs),
    'note': 'Router result reuses its four discovery probes. No extra probe was sent.',
}
(folder/'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps(summary, indent=2), flush=True)
