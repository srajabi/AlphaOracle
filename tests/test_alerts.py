"""Contract tests for the signal-change alerting layer.

The failure modes that matter here are quiet ones: alerting on every key
during the first run (which trains you to ignore the channel), staying
silent when a mandate flips, or treating a missing signal file as "no
change" and hiding a pipeline failure.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
ALERTS_PY = REPO / "src" / "alerts.py"


def signals_doc(slow="risk_on", fast="clear", credit="clear",
                canary="half_defensive", mandate="SLEEVE_INVESTED"):
    return {
        "generated_at_utc": "2026-08-08T12:00:00+00:00",
        "signals": {
            "slow_channel": {"state": slow, "distance_pct": 7.82},
            "fast_channel": {"state": fast, "vix_vix3m_5d_median": 0.858},
            "credit": {"state": credit, "hyg_lqd_63d_relmom": 0.0204},
            "canary": {"state": canary, "negative_canaries": ["TLT"]},
        },
        "mandates": {
            "P_sleeve": mandate,
            "Y_core_sleeve": mandate,
            "Y_satellite": "see registered champion state",
        },
    }


def run_alerts(workdir, outputs_file=None):
    env = dict(os.environ)
    if outputs_file:
        env["GITHUB_OUTPUT"] = str(outputs_file)
    else:
        env.pop("GITHUB_OUTPUT", None)
    proc = subprocess.run([sys.executable, str(ALERTS_PY)], cwd=workdir,
                          capture_output=True, text=True, env=env)
    return proc


def parse_outputs(path):
    if not Path(path).exists():
        return {}
    out = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k] = v
    return out


@pytest.fixture
def workdir(tmp_path):
    (tmp_path / "data").mkdir()
    return tmp_path


def write_signals(workdir, doc):
    (workdir / "data" / "family_signals.json").write_text(
        json.dumps(doc), encoding="utf-8")


def test_first_run_establishes_baseline_without_alerting(workdir):
    """Day one must be silent, or the channel is noise from the start."""
    write_signals(workdir, signals_doc())
    out = workdir / "gh_out"
    proc = run_alerts(workdir, out)

    assert proc.returncode == 0, proc.stderr
    assert parse_outputs(out)["has_alerts"] == "false"
    assert parse_outputs(out)["tier"] == "BASELINE"
    assert not (workdir / "data" / "alert_message.md").exists()
    state = json.loads((workdir / "data" / "alert_state.json").read_text())
    assert state["states"]["mandate:P_sleeve"] == "SLEEVE_INVESTED"


def test_no_change_produces_no_message(workdir):
    write_signals(workdir, signals_doc())
    run_alerts(workdir)
    out = workdir / "gh_out"
    proc = run_alerts(workdir, out)

    assert proc.returncode == 0
    assert parse_outputs(out)["has_alerts"] == "false"
    assert not (workdir / "data" / "alert_message.md").exists()


def test_mandate_flip_is_action_tier(workdir):
    write_signals(workdir, signals_doc())
    run_alerts(workdir)

    write_signals(workdir, signals_doc(slow="risk_off",
                                       mandate="SLEEVE_TO_TREASURIES"))
    out = workdir / "gh_out"
    proc = run_alerts(workdir, out)

    outputs = parse_outputs(out)
    assert outputs["has_alerts"] == "true"
    assert outputs["tier"] == "ACTION"
    assert "SLEEVE_INVESTED -> SLEEVE_TO_TREASURIES" in outputs["subject"]

    payload = json.loads((workdir / "data" / "alerts.json").read_text())
    assert payload["alerts"][0]["tier"] == "ACTION", \
        "ACTION must sort first so it survives a truncated preview"
    body = (workdir / "data" / "alert_message.md").read_text()
    assert "instruction for a real account" in body


def test_signal_move_without_mandate_change_is_info(workdir):
    write_signals(workdir, signals_doc())
    run_alerts(workdir)

    # Credit deteriorates but the mandate is unchanged.
    write_signals(workdir, signals_doc(credit="stressed"))
    out = workdir / "gh_out"
    run_alerts(workdir, out)

    outputs = parse_outputs(out)
    assert outputs["has_alerts"] == "true"
    assert outputs["tier"] == "INFO"
    payload = json.loads((workdir / "data" / "alerts.json").read_text())
    assert [a["key"] for a in payload["alerts"]] == ["signal:credit"]


def test_missing_signal_file_fails_loudly(workdir):
    """A missing input is a pipeline failure, not an all-clear."""
    out = workdir / "gh_out"
    proc = run_alerts(workdir, out)

    assert proc.returncode == 1
    assert parse_outputs(out)["has_alerts"] == "false"
    assert "missing or unreadable" in proc.stdout


def test_corrupt_state_file_is_treated_as_baseline(workdir):
    write_signals(workdir, signals_doc())
    (workdir / "data" / "alert_state.json").write_text("{not json",
                                                       encoding="utf-8")
    out = workdir / "gh_out"
    proc = run_alerts(workdir, out)

    assert proc.returncode == 0
    assert parse_outputs(out)["tier"] == "BASELINE"


def test_heartbeat_fires_after_a_quiet_stretch(workdir):
    write_signals(workdir, signals_doc())
    run_alerts(workdir)

    # Backdate the last message beyond the heartbeat window.
    state_path = workdir / "data" / "alert_state.json"
    state = json.loads(state_path.read_text())
    state["last_message_utc"] = "2026-01-01T00:00:00+00:00"
    state_path.write_text(json.dumps(state), encoding="utf-8")

    out = workdir / "gh_out"
    run_alerts(workdir, out)

    outputs = parse_outputs(out)
    assert outputs["has_alerts"] == "true"
    assert outputs["tier"] == "HEARTBEAT"
    body = (workdir / "data" / "alert_message.md").read_text()
    assert "silence stays meaningful" in body


def test_state_advances_so_a_transition_alerts_once(workdir):
    """An alert must not repeat every run until the signal moves back."""
    write_signals(workdir, signals_doc())
    run_alerts(workdir)

    changed = signals_doc(slow="risk_off", mandate="SLEEVE_TO_TREASURIES")
    write_signals(workdir, changed)
    first = workdir / "gh_out1"
    run_alerts(workdir, first)
    assert parse_outputs(first)["has_alerts"] == "true"

    second = workdir / "gh_out2"
    run_alerts(workdir, second)
    assert parse_outputs(second)["has_alerts"] == "false", \
        "same state on the next run must be silent"
