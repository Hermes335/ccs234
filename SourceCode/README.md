# CCS 234 Network Monitoring and Performance Analysis System

Windows desktop application using Python 3.10 or newer and Tkinter. Authors supplied: Ralph Martin Chua, Herald Kent Amolong, Ivan Clyde Sagala. The course PDFs describe an individual project; confirm group submission with the instructor.

## Install and run

Open a PowerShell terminal in this SourceCode folder:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

If `py` is unavailable, substitute `python` on the first line. Install the standard Windows Python distribution with Tcl/Tk support. No administrator shell is normally needed. The application uses the Windows IPv4 ICMP API, not raw sockets or localized ping text. It does not install or change firewall rules.

## Use

1. Dashboard: refresh local adapters and select the authorized Wi-Fi/LAN adapter. The actual IPv4 mask determines the network range. No /24 is assumed.
2. Confirm authorization only for a network and devices you own or may test. Do not authorize public, school, workplace or guest networks without permission.
3. Network Discovery: keep the detected subnet, or enter a smaller subnet within it. Discovery allows at most 256 addresses and sends at most four ICMP packets to each candidate. Eight workers keep it bounded. An 800 ms timeout applies per packet.
4. Select a responding device, or enter an authorized IP/hostname in Connectivity Testing. Choose 1-4 probes. Name resolution is bounded; the resolved IP must remain within the selected adapter subnet.
5. Review individual responses, statistics and rule-based advice. Reports can be saved as TXT, JSON or PDF. Saving happens locally. Review addresses/hostnames before sharing.
6. Cancel stops new probes; in-flight probes finish within their timeout. Closing the window requests cancellation. No continuous monitoring runs.

For networks larger than /24, select a /24 or smaller portion of the real detected network. IPv6 discovery is outside this version's scope. For multi-adapter hosts, Windows chooses the route to a destination; adapter selection constrains destination scope but does not bind the outgoing interface.

## Interpretation

Average and maximum latency use replies only. Packet loss is `(attempted - replies) / attempted * 100`. Local API errors may not have sent packets and are excluded from the denominator. Empty/unmeasured data is N/A. Windows returns integer milliseconds: 0 means below timer resolution, not physically zero latency. No echo reply can mean filtering, isolation, loss or an unavailable host. Discovery is not guaranteed to find every active device.

Connectivity rules flag loss >=20% or mean RTT >=100 ms. These are project heuristics, not universal standards. Advice never claims that a password is weak or a firewall is disabled; no such settings are inspected.

## Test

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q --junitxml=test-results.xml
```

Unit tests use mocked inputs and never scan your network. Verified baseline: 64 passed on Windows/Python 3.10 on 2026-10-27. Evidence is under `verification/` in the packaged copy. Real validation is documented separately; it is not part of pytest.

## Structure

- `netmonitor/core.py`: data validation, statistics and recommendation rules.
- `netmonitor/network.py`: local metadata, DNS, Windows ICMP and bounded discovery.
- `netmonitor/reports.py`: report snapshots and atomic TXT/JSON/PDF saves.
- `netmonitor/gui.py`: six views, background workers and main-thread event polling.
- `tests/`: deterministic unit tests.

Known limitations: IPv4/Windows only; no throughput, jitter, port scan, Wireshark or password audit; no persistence across application sessions other than exports; report filenames are chosen by the user and reports include timestamps. DNS replies can expose hostnames and may be unavailable. A four-packet sample is too small for long-term reliability conclusions.

## Troubleshooting

- Missing tkinter: repair the Python installation and enable Tcl/Tk.
- Missing psutil/reportlab: install requirements using the same Python that launches the app.
- No adapters: confirm Wi-Fi/LAN is connected, then refresh.
- No responses: inspect connectivity and ICMP policy without disabling the firewall indiscriminately.
- PDF save error: check dependencies, folder permissions and whether the file is open elsewhere.
- Out-of-scope error: select the correct authorized adapter and ensure the target resolves inside it.
