"""Pure measurement models, input validation, statistics and transparent rules."""
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import ipaddress
import math
import re


def timestamp():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def validate_target(value):
    value = value.strip()
    if not value or len(value) > 253:
        raise ValueError("Enter an IPv4 address or hostname (1-253 characters).")
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        if re.fullmatch(r"[\d.]+", value) or ":" in value:
            raise ValueError("Invalid IPv4 address; IPv6 is not supported.") from None
        labels = value.rstrip(".").split(".")
        if not all(re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", x) for x in labels):
            raise ValueError("Invalid hostname. Use letters, numbers, dots and internal hyphens.")
        return value.rstrip(".")
    if address.version != 4 or address.is_multicast or address.is_unspecified or str(address) == "255.255.255.255":
        raise ValueError("Enter a unicast IPv4 address.")
    return str(address)


def validate_scope(cidr):
    try:
        network = ipaddress.ip_network(cidr, strict=True)
    except ValueError:
        raise ValueError("Enter a canonical IPv4 subnet, for example 192.168.10.0/24.") from None
    if network.version != 4 or network.num_addresses > 256:
        raise ValueError("Discovery is limited to IPv4 subnets of at most 256 addresses (/24 or smaller).")
    if network.is_multicast or network.is_unspecified or network.is_loopback or network.is_link_local:
        raise ValueError("Select a normal local IPv4 subnet.")
    return network


@dataclass(frozen=True)
class Probe:
    sequence: int
    status: str
    latency_ms: float | None = None
    detail: str = ""
    measured_at: str = field(default_factory=timestamp)

    def __post_init__(self):
        if self.status not in {"reply", "timeout", "unreachable", "error"}:
            raise ValueError("Unknown probe status")
        if self.status == "reply" and (self.latency_ms is None or not math.isfinite(self.latency_ms) or self.latency_ms < 0):
            raise ValueError("Reply must include a nonnegative measured latency")
        if self.status != "reply" and self.latency_ms is not None:
            raise ValueError("Failed probes have no measured latency")


@dataclass
class PingRun:
    target: str
    ip: str
    probes: list[Probe]
    hostname: str = ""
    started_at: str = field(default_factory=timestamp)
    provenance: str = "live"
    requested_count: int = 4
    cancelled: bool = False


def statistics(probes):
    replies = [p.latency_ms for p in probes if p.status == "reply"]
    attempted = sum(p.status != "error" for p in probes)
    errors = len(probes) - attempted
    return {
        "attempted": attempted, "received": len(replies), "local_errors": errors,
        "average_ms": sum(replies) / len(replies) if replies else None,
        "maximum_ms": max(replies) if replies else None,
        "loss_percent": 100 * (attempted - len(replies)) / attempted if attempted else None,
        "status": "reachable" if replies else ("unreachable / no echo reply" if attempted else "not measured"),
    }


def recommendations(run=None):
    advice = []
    if run is None:
        advice.append("No connectivity measurements yet. Run an authorized test before assessing connectivity.")
    else:
        stats = statistics(run.probes)
        if stats["attempted"] and not stats["received"]:
            advice.append("No echo reply: check device power, route and ICMP policy. This does not prove the host is offline.")
        if stats["loss_percent"] is not None and stats["loss_percent"] >= 20:
            advice.append("Weak connectivity alert: loss >=20% (project heuristic). Check signal/cabling and repeat the bounded test.")
        if stats["average_ms"] is not None and stats["average_ms"] >= 100:
            advice.append("Latency alert: average >=100 ms (project heuristic). Compare with the same target and inspect congestion.")
        if stats["local_errors"]:
            advice.append("Local probe errors occurred; packet loss excludes these unknown send attempts.")
        if stats["received"] and stats["loss_percent"] < 20 and stats["average_ms"] < 100:
            advice.append("This sample did not trigger the configured connectivity alerts; it does not establish overall network health.")
    advice.extend([
        "General firewall reminder: keep the firewall enabled and permit only needed traffic; review ICMP policy with the owner.",
        "General password reminder: use unique strong passwords, change default router credentials and enable MFA where supported.",
        "These rules assess connectivity only. No firewall configuration, passwords or vulnerabilities were inspected.",
    ])
    return advice


def run_dict(run):
    return {**asdict(run), "statistics": statistics(run.probes), "recommendations": recommendations(run)}
