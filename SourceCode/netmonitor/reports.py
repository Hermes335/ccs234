"""Local report export with measured values and evidence provenance."""
import json
import os
from pathlib import Path
from xml.sax.saxutils import escape

from .core import recommendations, run_dict, timestamp


def snapshot(interfaces, discovery, runs):
    return {
        "title": "CCS 234 Network Monitoring Report", "generated_at": timestamp(),
        "interfaces": interfaces,
        "discovery": None if discovery is None else {
            "network": discovery.network, "started_at": discovery.started_at,
            "cancelled": discovery.cancelled, "provenance": discovery.provenance,
            "method": discovery.method,
            "tested_count": len(discovery.runs),
            "devices": [run_dict(r) for r in discovery.devices],
            "all_results": [run_dict(r) for r in discovery.runs],
        },
        "ping_runs": [run_dict(r) for r in runs],
        "general_recommendations": recommendations(),
        "limitations": [
            "ICMP discovery can miss active devices. No echo reply does not prove a host is offline.",
            "This report is a bounded sample, not a complete inventory or security audit.",
            "Local errors are excluded from packet-loss denominators because sending is unconfirmed.",
            "Windows integer RTT of 0 ms is below timer resolution, not proof of zero latency.",
            "IP addresses and hostnames may be private. Review before sharing.",
        ],
    }


def value(number, suffix=""):
    return "N/A" if number is None else f"{number:.2f}{suffix}"


def text_report(data):
    lines = [data["title"], f"Generated: {data['generated_at']}", "", "LOCAL INTERFACES"]
    for item in data["interfaces"]:
        lines.append(f"{item['adapter']}: {item['hostname']} / {item['ip']} / {item['network']}")
    if not data["interfaces"]:
        lines.append("No interface information collected.")
    discovery = data["discovery"]
    lines.extend(["", "DISCOVERY"])
    if discovery is None:
        lines.append("Not performed.")
    else:
        lines.append(f"{discovery['network']} at {discovery['started_at']} [{discovery['provenance']}]")
        lines.append(f"Tested {discovery['tested_count']}; responding devices {len(discovery['devices'])}; cancelled {discovery['cancelled']}")
        lines.extend(f"{r['ip']} {r['hostname'] or '(hostname unavailable)'}" for r in discovery["devices"])
    lines.extend(["", "PING RESULTS AND PERFORMANCE SUMMARY"])
    all_runs = (discovery["all_results"] if discovery else []) + data["ping_runs"]
    if not all_runs:
        lines.append("No measurements available. Latency and packet loss are N/A.")
    for run in all_runs:
        s = run["statistics"]
        lines.extend(["", f"{run['target']} ({run['ip']}) {run['hostname']} [{run['provenance']}]",
                      f"Started: {run['started_at']}; requested {run['requested_count']}; cancelled {run['cancelled']}",
                      f"Status: {s['status']}; attempted {s['attempted']}; replies {s['received']}; local errors {s['local_errors']}",
                      f"Average {value(s['average_ms'], ' ms')}; maximum {value(s['maximum_ms'], ' ms')}; loss {value(s['loss_percent'], '%')}"])
        for p in run["probes"]:
            lines.append(f"  #{p['sequence']} {p['measured_at']}: {p['status']}, RTT {value(p['latency_ms'], ' ms')} {p['detail']}")
        lines.extend(run["recommendations"])
    lines.extend(["", "GENERAL RECOMMENDATIONS", *data["general_recommendations"][1:], "", "LIMITATIONS", *data["limitations"]])
    return "\n".join(lines) + "\n"


def save_report(path, data):
    path = Path(path)
    if path.suffix.lower() not in {".txt", ".json", ".pdf"}:
        raise ValueError("Choose .txt, .json or .pdf.")
    # Replace atomically after a successful write, preserving an existing report on failure.
    temporary = path.with_name(path.name + ".tmp")
    try:
        if path.suffix.lower() == ".json":
            temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        elif path.suffix.lower() == ".txt":
            temporary.write_text(text_report(data), encoding="utf-8")
        else:
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            style = getSampleStyleSheet()["BodyText"]
            style.fontSize, style.leading = 9, 13
            content = [Paragraph(escape(line), style) if line else Spacer(1, 10)
                       for line in text_report(data).splitlines()]
            SimpleDocTemplate(str(temporary), title=data["title"]).build(content)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
