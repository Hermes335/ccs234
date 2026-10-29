import math
import pytest
from netmonitor.core import PingRun, Probe, recommendations, statistics, validate_scope, validate_target


@pytest.mark.parametrize("target", ["192.168.2.1", "router", "my-router.local", "example.com."])
def test_valid_targets(target):
    assert validate_target(target) == target.rstrip(".")


@pytest.mark.parametrize("target", ["", "999.1.2.3", "1.2.3", "-bad", "x;whoami", "a/b", "::1", "0.0.0.0", "224.0.0.1", "255.255.255.255", "a..b", "a" * 64 + ".com"])
def test_invalid_targets(target):
    with pytest.raises(ValueError):
        validate_target(target)


@pytest.mark.parametrize("cidr", ["192.168.0.0/16", "192.168.2.1/24", "::/64", "bad", "127.0.0.0/24", "224.0.0.0/24"])
def test_invalid_scope(cidr):
    with pytest.raises(ValueError):
        validate_scope(cidr)


def test_exact_statistics():
    s = statistics([Probe(1, "reply", 10), Probe(2, "reply", 30), Probe(3, "timeout"), Probe(4, "error")])
    assert s["average_ms"] == 20
    assert s["maximum_ms"] == 30
    assert s["loss_percent"] == pytest.approx(100 / 3)
    assert s["attempted"] == 3 and s["local_errors"] == 1


def test_zero_latency_preserved():
    assert statistics([Probe(1, "reply", 0)])["average_ms"] == 0


@pytest.mark.parametrize("probes,loss", [([], None), ([Probe(1, "error")], None), ([Probe(1, "timeout")], 100)])
def test_missing_measurements(probes, loss):
    s = statistics(probes)
    assert s["average_ms"] is None and s["maximum_ms"] is None
    assert s["loss_percent"] == loss


@pytest.mark.parametrize("status,latency", [("reply", None), ("reply", -1), ("reply", math.nan), ("reply", math.inf), ("timeout", 0), ("invented", None)])
def test_invalid_probe_data(status, latency):
    with pytest.raises(ValueError):
        Probe(1, status, latency)


def test_recommendations_thresholds():
    run = PingRun("x", "192.168.1.1", [Probe(1, "reply", 100), Probe(2, "timeout")], provenance="mocked")
    advice = " ".join(recommendations(run))
    assert "loss >=20%" in advice and "average >=100 ms" in advice
    assert "No firewall configuration" in advice
    assert "No echo reply" in " ".join(recommendations(PingRun("x", "192.168.1.1", [Probe(1, "timeout")])))
    assert "No connectivity" in recommendations()[0]


def test_healthy_sample_is_not_security_claim():
    advice = " ".join(recommendations(PingRun("x", "192.168.1.1", [Probe(1, "reply", 3)])))
    assert "did not trigger" in advice and "does not establish" in advice
