import json
from datetime import datetime
import pytest
from netmonitor.core import PingRun, Probe
from netmonitor.network import Discovery
from netmonitor.reports import save_report, snapshot, text_report


def fixture():
    run = PingRun("192.168.2.1", "192.168.2.1", [Probe(1, "reply", 12), Probe(2, "timeout")], hostname="mock-router", provenance="mocked")
    return snapshot([], Discovery("192.168.2.0/30", [run], provenance="mocked"), [run])


def test_report_has_results_and_provenance():
    data = fixture()
    assert datetime.fromisoformat(data["generated_at"]).tzinfo is not None
    text = text_report(data)
    for expected in ["mocked", "mock-router", "12.00 ms", "50.00%", "timeout", "No firewall configuration"]:
        assert expected in text


def test_empty_report_has_no_invented_numbers():
    assert "Latency and packet loss are N/A" in text_report(snapshot([], None, []))


@pytest.mark.parametrize("suffix", [".txt", ".json", ".pdf"])
def test_save(tmp_path, suffix):
    path = tmp_path / ("report" + suffix)
    data = fixture()
    save_report(path, data)
    assert path.stat().st_size > 100
    assert not path.with_name(path.name + ".tmp").exists()
    if suffix == ".json":
        assert json.loads(path.read_text(encoding="utf-8")) == data
    if suffix == ".pdf":
        assert path.read_bytes().startswith(b"%PDF")


def test_export_rejects_unknown_extension(tmp_path):
    with pytest.raises(ValueError):
        save_report(tmp_path / "report.exe", fixture())


def test_export_missing_directory(tmp_path):
    with pytest.raises(OSError):
        save_report(tmp_path / "missing" / "report.txt", fixture())
