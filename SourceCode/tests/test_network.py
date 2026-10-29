import socket
import threading
import pytest
from netmonitor.core import Probe
from netmonitor.network import bounded_call, classify_reply, discover, ping, resolve_target


def fake(ip, timeout, sequence):
    return Probe(sequence, "reply", sequence * 10) if ip.endswith(".1") else Probe(sequence, "timeout")


def test_ping_success():
    run = ping("192.168.2.1", authorized=True, allowed_network="192.168.2.0/24", transport=fake, provenance="mocked")
    assert len(run.probes) == 4 and run.probes[3].latency_ms == 40
    assert run.provenance == "mocked"


def test_ping_failure():
    run = ping("192.168.2.2", authorized=True, allowed_network="192.168.2.0/24", transport=fake)
    assert all(p.status == "timeout" for p in run.probes)


@pytest.mark.parametrize("kwargs,error", [({}, PermissionError), ({"authorized": True}, PermissionError),
    ({"authorized": True, "count": 5}, ValueError), ({"authorized": True, "count": 0}, ValueError),
    ({"authorized": True, "timeout_ms": 1}, ValueError), ({"authorized": True, "count": True}, ValueError)])
def test_ping_limits(kwargs, error):
    with pytest.raises(error):
        ping("192.168.2.1", transport=lambda *a: pytest.fail("must not probe"), **kwargs)


def test_resolved_target_cannot_escape_scope():
    with pytest.raises(PermissionError):
        ping("router.local", authorized=True, allowed_network="192.168.2.0/24", resolver=lambda _: "8.8.8.8", transport=fake)


def test_hostname_resolution_mock(monkeypatch):
    monkeypatch.setattr(socket, "gethostbyname", lambda _: "192.168.2.1")
    assert resolve_target("router.local") == "192.168.2.1"


def test_dns_failure(monkeypatch):
    def fail(_):
        raise socket.gaierror("mocked unknown name")
    monkeypatch.setattr(socket, "gethostbyname", fail)
    with pytest.raises(socket.gaierror):
        resolve_target("missing.local")


def test_bounded_timeout():
    release = threading.Event()
    try:
        with pytest.raises(TimeoutError):
            bounded_call(release.wait, timeout=0.01)
    finally:
        release.set()


@pytest.mark.parametrize("code,status", [(0, "reply"), (11010, "timeout"), (11003, "unreachable"), (5, "error")])
def test_icmp_status(code, status):
    assert classify_reply(1, code, 8).status == status


def test_transport_error_not_packet_loss():
    def fail(*args):
        raise OSError("mock transport denied")
    run = ping("192.168.2.1", authorized=True, allowed_network="192.168.2.0/24", transport=fail)
    assert all(p.status == "error" for p in run.probes)


def test_discovery_mocked():
    result = discover("192.168.2.0/30", authorized=True, local_network="192.168.2.0/24", transport=fake, namer=lambda _: "test-router", provenance="mocked")
    assert len(result.runs) == 2
    assert [x.ip for x in result.devices] == ["192.168.2.1"]
    assert result.devices[0].hostname == "test-router"
    assert all(len(r.probes) == 4 for r in result.runs)


def test_discovery_requires_authorization_and_local_scope():
    with pytest.raises(PermissionError):
        discover("192.168.2.0/24")
    with pytest.raises(PermissionError):
        discover("192.168.2.0/24", authorized=True, local_network="10.1.1.0/24")


def test_cancellation():
    event = threading.Event()
    event.set()
    result = discover("192.168.2.0/30", authorized=True, local_network="192.168.2.0/24", cancel=event, transport=lambda *a: pytest.fail("cancelled"))
    assert result.cancelled and not result.runs


@pytest.mark.parametrize("ip", ["192.168.2.0", "192.168.2.255"])
def test_network_broadcast_rejected(ip):
    with pytest.raises(ValueError):
        ping(ip, authorized=True, allowed_network="192.168.2.0/24", transport=fake)
