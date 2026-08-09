#!/usr/bin/env python3
"""Turn signal STATE CHANGES into alerts.

Why transitions and not levels: a daily "here is the state" message
becomes wallpaper within a fortnight, and the one message that matters
arrives looking exactly like the 200 that didn't. So this only speaks
when something actually moved.

Where this sits: immediately after family_signals.py and BEFORE
llm_agents.py. That ordering is deliberate - the LLM step has failed for
ten consecutive runs on an unfunded provider, and an alert about a
million dollars must not be downstream of an API balance. Everything
here is deterministic arithmetic over a JSON file.

Tiers:
  ACTION - a mandate changed. You have something to do in a real account.
  INFO   - an underlying signal moved but no mandate changed. Context.

Reads   data/family_signals.json, data/alert_state.json
Writes  data/alerts.json, data/alert_message.md, data/alert_state.json
Emits   GitHub step outputs: has_alerts, tier, subject
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SIGNALS = Path("data/family_signals.json")
STATE = Path("data/alert_state.json")
ALERTS = Path("data/alerts.json")
MESSAGE = Path("data/alert_message.md")

# Days of quiet before we send a heartbeat, so that silence is never
# ambiguous. See the caveat in main() - this cannot detect its own
# absence; that needs an external dead-man's switch.
HEARTBEAT_DAYS = 7

# Human labels for the keys we watch.
LABELS = {
    "mandate:P_sleeve": "Mandate P equity sleeve",
    "mandate:Y_core_sleeve": "Mandate Y core sleeve",
    "mandate:Y_satellite": "Mandate Y satellite",
    "signal:slow_channel": "Trend (monthly 200dma)",
    "signal:fast_channel": "VIX term structure",
    "signal:credit": "Credit (HYG/LQD 63d)",
    "signal:canary": "Canary breadth",
}


def load(path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"WARNING: {path} unreadable ({exc}); treating as absent.")
        return default


def extract_states(signals):
    """Flatten the signal document into a {key: state} mapping.

    Mandates are prefixed differently from signals because the prefix is
    what decides the tier - a mandate moving is an instruction, a signal
    moving underneath an unchanged mandate is context.
    """
    states = {}
    for name, value in (signals.get("mandates") or {}).items():
        states[f"mandate:{name}"] = str(value)
    for name, block in (signals.get("signals") or {}).items():
        if isinstance(block, dict) and "state" in block:
            states[f"signal:{name}"] = str(block["state"])
    return states


def detail_for(key, signals):
    """A number to go with the transition, so the alert is auditable."""
    name = key.split(":", 1)[1]
    block = (signals.get("signals") or {}).get(name)
    if not isinstance(block, dict):
        return ""
    for field in ("distance_pct", "vix_vix3m_5d_median", "hyg_lqd_63d_relmom"):
        if field in block:
            return f"{field}={block[field]}"
    if block.get("negative_canaries"):
        return f"negative={','.join(block['negative_canaries'])}"
    return ""


def diff(previous, current, signals):
    """Transitions only. Keys that appear or vanish are not transitions."""
    out = []
    for key, now in sorted(current.items()):
        before = previous.get(key)
        if before is None or before == now:
            continue
        out.append({
            "key": key,
            "label": LABELS.get(key, key),
            "from": before,
            "to": now,
            "tier": "ACTION" if key.startswith("mandate:") else "INFO",
            "detail": detail_for(key, signals),
        })
    # ACTION first - if the message is truncated by a notification
    # preview, the actionable line should be the one that survives.
    out.sort(key=lambda a: (a["tier"] != "ACTION", a["key"]))
    return out


def render(alerts, states, signals, heartbeat):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = []
    if alerts:
        top = "ACTION" if any(a["tier"] == "ACTION" for a in alerts) else "INFO"
        lines.append(f"# [{top}] AlphaOracle signal change - {now}")
        lines.append("")
        for a in alerts:
            detail = f" ({a['detail']})" if a["detail"] else ""
            lines.append(f"- **{a['label']}**: `{a['from']}` -> "
                         f"`{a['to']}`{detail}")
        if top == "ACTION":
            lines.append("")
            lines.append("A mandate changed. This is an instruction for a "
                         "real account, not commentary.")
    else:
        lines.append(f"# AlphaOracle heartbeat - {now}")
        lines.append("")
        lines.append(f"No signal changes in the last {HEARTBEAT_DAYS} days. "
                     "This message exists so that silence stays meaningful.")

    lines.append("")
    lines.append("## Current state")
    lines.append("")
    lines.append("| Signal | State |")
    lines.append("|---|---|")
    for key, value in sorted(states.items()):
        lines.append(f"| {LABELS.get(key, key)} | `{value}` |")

    generated = signals.get("generated_at_utc", "unknown")
    lines.append("")
    lines.append(f"Signals generated {generated}. Paper trading research, "
                 "not advice.")
    return "\n".join(lines) + "\n"


def emit_outputs(**kwargs):
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as fh:
        for key, value in kwargs.items():
            fh.write(f"{key}={value}\n")


def main():
    signals = load(SIGNALS)
    if not signals:
        # Do not invent a state. A missing signal file is a pipeline
        # failure, and inventing "no change" would hide it.
        print(f"ERROR: {SIGNALS} missing or unreadable; cannot diff.")
        emit_outputs(has_alerts="false", tier="NONE", subject="")
        return 1

    current = extract_states(signals)
    if not current:
        print("ERROR: no states found in signal document.")
        emit_outputs(has_alerts="false", tier="NONE", subject="")
        return 1

    prior = load(STATE)
    now = datetime.now(timezone.utc)

    if prior is None:
        # First run establishes the baseline. Alerting on every key here
        # would fire a wall of false transitions on day one and teach you
        # to ignore the channel immediately.
        print(f"Baseline established from {len(current)} states; "
              "no alerts on first run.")
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps({
            "updated_at_utc": now.isoformat(),
            "last_message_utc": now.isoformat(),
            "states": current,
        }, indent=2), encoding="utf-8")
        emit_outputs(has_alerts="false", tier="BASELINE", subject="")
        return 0

    alerts = diff(prior.get("states", {}), current, signals)

    last_msg = prior.get("last_message_utc")
    quiet_days = None
    if last_msg:
        try:
            quiet_days = (now - datetime.fromisoformat(last_msg)).days
        except ValueError:
            quiet_days = None
    heartbeat = not alerts and (quiet_days is None
                                or quiet_days >= HEARTBEAT_DAYS)

    tier = "NONE"
    if alerts:
        tier = "ACTION" if any(a["tier"] == "ACTION" for a in alerts) else "INFO"
    elif heartbeat:
        tier = "HEARTBEAT"

    ALERTS.parent.mkdir(parents=True, exist_ok=True)
    ALERTS.write_text(json.dumps({
        "generated_at_utc": now.isoformat(),
        "tier": tier,
        "alerts": alerts,
        "states": current,
    }, indent=2), encoding="utf-8")

    send = bool(alerts) or heartbeat
    if send:
        MESSAGE.write_text(render(alerts, current, signals, heartbeat),
                           encoding="utf-8")
        if alerts:
            lead = alerts[0]
            subject = (f"[{tier}] {lead['label']}: {lead['from']} -> "
                       f"{lead['to']}")
            if len(alerts) > 1:
                subject += f" (+{len(alerts) - 1} more)"
        else:
            subject = "[HEARTBEAT] AlphaOracle: no signal changes"
    else:
        subject = ""

    STATE.write_text(json.dumps({
        "updated_at_utc": now.isoformat(),
        "last_message_utc": now.isoformat() if send else last_msg,
        "states": current,
    }, indent=2), encoding="utf-8")

    for a in alerts:
        print(f"{a['tier']}: {a['label']} {a['from']} -> {a['to']}")
    if not alerts:
        print(f"No transitions (quiet {quiet_days} days); "
              f"heartbeat={'yes' if heartbeat else 'no'}")

    emit_outputs(has_alerts=str(send).lower(), tier=tier, subject=subject)
    return 0


if __name__ == "__main__":
    sys.exit(main())
