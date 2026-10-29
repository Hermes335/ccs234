"""Windows ICMP and bounded authorized IPv4 discovery.

IcmpSendEcho avoids parsing localized ping.exe text. The OS supplies integer
milliseconds; zero is preserved and described as below timer resolution.
"""
import ctypes
import ipaddress
import os
import queue
import socket
import struct
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from .core import PingRun, Probe, timestamp, validate_scope, validate_target


def bounded_call(function, *args, timeout=2):
    """Bound UI-facing DNS waits; a timed-out OS resolver thread is daemonized."""
    results = queue.Queue(maxsize=1)
    def worker():
        try:
            results.put((True, function(*args)))
        except Exception as exc:
            results.put((False, exc))
    threading.Thread(target=worker, daemon=True).start()
    try:
        ok, result = results.get(timeout=timeout)
    except queue.Empty:
        raise TimeoutError("Name resolution timed out.") from None
    if not ok:
        raise result
    return result


def resolve_target(target):
    target = validate_target(target)
    try:
        return str(ipaddress.IPv4Address(target))
    except ipaddress.AddressValueError:
        return validate_target(bounded_call(socket.gethostbyname, target))


def reverse_name(ip):
    try:
        return bounded_call(socket.gethostbyaddr, ip, timeout=0.6)[0]
    except (OSError, TimeoutError):
        return ""


def local_interfaces():
    """Read local adapter metadata only; no socket connection or probe is sent."""
    import psutil
    result = []
    status = psutil.net_if_stats()
    for name, addresses in psutil.net_if_addrs().items():
        if name not in status or not status[name].isup:
            continue
        for item in addresses:
            if item.family == socket.AF_INET and item.netmask:
                ip = ipaddress.IPv4Address(item.address)
                if ip.is_loopback or ip.is_link_local:
                    continue
                network = ipaddress.IPv4Network(f"{ip}/{item.netmask}", strict=False)
                result.append({"adapter": name, "ip": str(ip), "netmask": item.netmask,
                               "network": str(network), "hostname": socket.gethostname()})
    return result


class IPOptions(ctypes.Structure):
    _fields_ = [("ttl", ctypes.c_ubyte), ("tos", ctypes.c_ubyte),
                ("flags", ctypes.c_ubyte), ("size", ctypes.c_ubyte), ("data", ctypes.c_void_p)]


class EchoReply(ctypes.Structure):
    _fields_ = [("address", ctypes.c_uint32), ("status", ctypes.c_uint32),
                ("rtt", ctypes.c_uint32), ("size", ctypes.c_ushort),
                ("reserved", ctypes.c_ushort), ("data", ctypes.c_void_p), ("options", IPOptions)]


def classify_reply(sequence, status, rtt=None):
    if status == 0:
        return Probe(sequence, "reply", float(rtt), "Windows ICMP RTT in whole ms; 0 means below timer resolution.")
    if status == 11010:
        return Probe(sequence, "timeout", detail="ICMP timeout (11010)")
    if status in {11002, 11003, 11004, 11005, 11013}:
        return Probe(sequence, "unreachable", detail=f"ICMP status {status}")
    return Probe(sequence, "error", detail=f"Windows ICMP error {status}; send/measurement not confirmed")


def windows_probe(ip, timeout_ms, sequence):
    if os.name != "nt":
        return Probe(sequence, "error", detail="Live ICMP transport requires Windows.")
    # Declare pointer widths explicitly for both 32-bit and 64-bit Python.
    api = ctypes.WinDLL("iphlpapi.dll", use_last_error=True)
    api.IcmpCreateFile.restype = ctypes.c_void_p
    api.IcmpCreateFile.argtypes = []
    api.IcmpCloseHandle.argtypes = [ctypes.c_void_p]
    api.IcmpCloseHandle.restype = ctypes.c_int
    api.IcmpSendEcho.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p,
                                ctypes.c_ushort, ctypes.c_void_p, ctypes.c_void_p,
                                ctypes.c_uint32, ctypes.c_uint32]
    api.IcmpSendEcho.restype = ctypes.c_uint32
    handle = api.IcmpCreateFile()
    if handle == ctypes.c_void_p(-1).value or not handle:
        return Probe(sequence, "error", detail=f"Cannot open ICMP handle: {ctypes.get_last_error()}")
    try:
        payload = ctypes.create_string_buffer(b"CCS234 network monitor")
        reply = ctypes.create_string_buffer(ctypes.sizeof(EchoReply) + len(payload) + 8)
        destination = struct.unpack("=I", socket.inet_aton(ip))[0]
        received = api.IcmpSendEcho(handle, destination, payload, len(payload), None,
                                    reply, len(reply), timeout_ms)
        if not received:
            return classify_reply(sequence, ctypes.get_last_error())
        parsed = EchoReply.from_buffer(reply)
        return classify_reply(sequence, parsed.status, parsed.rtt)
    finally:
        api.IcmpCloseHandle(handle)


def ping(target, *, authorized=False, allowed_network=None, count=4, timeout_ms=800,
         transport=None, resolver=None, cancel=None, provenance="live"):
    if not authorized:
        raise PermissionError("Confirm authorization for this target before testing.")
    if not isinstance(count, int) or isinstance(count, bool) or not 1 <= count <= 4:
        raise ValueError("Use 1-4 packets per target.")
    if not isinstance(timeout_ms, int) or not 100 <= timeout_ms <= 2000:
        raise ValueError("Timeout must be 100-2000 ms.")
    target = validate_target(target)
    ip = (resolver or resolve_target)(target)
    address = ipaddress.IPv4Address(validate_target(ip))
    if allowed_network is None or address not in ipaddress.IPv4Network(allowed_network):
        raise PermissionError("Resolved target is outside the authorized IPv4 subnet.")
    net = ipaddress.IPv4Network(allowed_network)
    if net.prefixlen < 31 and address in {net.network_address, net.broadcast_address}:
        raise ValueError("Network and broadcast addresses cannot be ping targets.")
    run = PingRun(target, str(address), [], hostname=target if target != ip else "",
                  provenance=provenance, requested_count=count)
    for sequence in range(1, count + 1):
        if cancel and cancel.is_set():
            run.cancelled = True
            break
        try:
            probe = (transport or windows_probe)(str(address), timeout_ms, sequence)
        except (OSError, TimeoutError) as exc:
            probe = Probe(sequence, "error", detail=str(exc))
        run.probes.append(probe)
    return run


@dataclass
class Discovery:
    network: str
    runs: list[PingRun] = field(default_factory=list)
    started_at: str = field(default_factory=timestamp)
    cancelled: bool = False
    provenance: str = "live"
    method: str = "ICMP echo; at most 4 packets per target"

    @property
    def devices(self):
        return [r for r in self.runs if any(p.status == "reply" for p in r.probes)]


def discover(cidr, *, authorized=False, local_network=None, transport=None,
             namer=None, cancel=None, provenance="live", progress=None):
    if not authorized:
        raise PermissionError("Confirm that you own or may test this subnet.")
    network = validate_scope(cidr)
    if local_network is None or not network.subnet_of(ipaddress.IPv4Network(local_network)):
        raise PermissionError("Discovery must stay inside the selected local adapter subnet.")
    result = Discovery(str(network), provenance=provenance)
    stop = cancel or threading.Event()
    # Eight concurrent bounded jobs, at most 256 candidate addresses.
    def scan(address):
        run = ping(str(address), authorized=True, allowed_network=str(network),
                   transport=transport, cancel=stop, provenance=provenance)
        if not stop.is_set() and any(p.status == "reply" for p in run.probes):
            run.hostname = (namer or reverse_name)(str(address))
        return run
    hosts = list(network.hosts())
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(scan, address) for address in hosts}
        for future in as_completed(futures):
            run = future.result()
            if run.probes:
                result.runs.append(run)
            if progress:
                progress(len(result.runs), len(hosts))
    result.cancelled = stop.is_set()
    result.runs.sort(key=lambda r: ipaddress.IPv4Address(r.ip))
    return result
