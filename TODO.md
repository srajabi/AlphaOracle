# AlphaOracle TODO

Working list. Agent tasks and user actions in one place so nothing is
lost between sessions. Newest context at the bottom of each section.

Convention: `[ ]` open, `[x]` done, `[~]` in progress, `[!]` blocked.

## Yours (user actions - nothing else can start these)

- [ ] **Dedicated Gmail sender + `MAIL_*` secrets.** Use a *separate*
  account, not your primary: a Google App Password authenticates for
  Mail, which includes IMAP **read**, and bypasses 2FA. Secrets:
  `MAIL_TO`, `MAIL_USERNAME`, `MAIL_PASSWORD` (16-char App Password),
  optional `MAIL_SERVER`.
- [ ] **Telegram bot + `TELEGRAM_*` secrets.** @BotFather -> `/newbot`
  -> token. Message the bot once (bots cannot initiate). Read `chat.id`
  from `https://api.telegram.org/bot<TOKEN>/getUpdates`. Secrets:
  `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
- [ ] **Provider funding / chain order.** DeepSeek is confirmed at zero.
  The other four are *unknown* - checking dashboards. Chain order is the
  drain order: put the balance nearest expiry first, then tell me and I
  will set `RISK/TECH/MACRO/PM_MODELS`.
- [ ] **healthchecks.io check + `HEALTHCHECK_URL` secret.** Free tier.
  Period ~1 day, grace ~6h (the EOD cron runs weekdays 20:30 UTC and has
  been arriving up to ~80 min late). This is the only thing that can
  detect the pipeline not running at all.

## Verification pending (needs a real scheduled run)

- [ ] **Monday 2026-08-10, 20:30 UTC** does triple duty:
  1. Proves the EOD gate fix - accounts 1-5 should report success, not
     skipped.
  2. Reveals which providers in the fallback chain actually answer.
  3. Establishes the alerting baseline (first run is silent by design).

## Minute-data track (spike: `spikes/minute_data.md`)

- [x] Audit the OHLCV-1m dataset - schema, tickers, coverage, traps.
- [x] `src/minute_data.py` access layer handling **five** traps (a fifth,
      bad prints, surfaced only once we looked at the tail).
- [x] Multi-ticker single-pass loader - the archive is I/O-bound and
      per-ticker passes re-read the same hundreds of GB.
- [~] Measure the real overnight gap distribution; validate or refute
      finding 14's assumed 15%.
- [ ] Stop-loss backtests on true intraday path.
- [ ] LETF path-dependency vs the daily approximation.

## Strategy research (the manifesto's actual question)

- [x] **H7 contribution-aware backtests** (finding 23). Contributions
      widen the overlay's shortfall by ~2pp - real but second-order.
      Rankings do not flip. Caught a `signal[T]` vs `returns[T]`
      causality bug that produced +271% / -8% maxDD; that pattern is now
      a detector.
- [x] **Check frequency** (finding 24). Bands invert the answer. Without
      them monthly beats daily; with 5% bands daily wins by 193% at 3x.
      1x has NO edge on terminal wealth, but loses cheaply enough
      (0.23pp CAGR to halve drawdown) that it makes leverage survivable.
      Band plateau 2-6%, cliff at 8%.
- [x] **Findings verification** (finding 25). findings.md is LLM prose;
      `tests/test_findings_reproduce.py` now re-derives claims. Finding
      3's buy-hold reproduces exactly, its overlay claim does not
      (-34.8% vs claimed -19%) - almost certainly an unrecorded check
      frequency.
- [~] **H2 leveraged trend on REAL LETF data.** The 1474x result uses
      SIMULATED 3x. Real TQQQ/UPRO start ~2010, so they cannot see
      dot-com or the GFC. Plan: validate the simulator against real fund
      prices over the overlap, then trust it on the longer window only
      if it matches.
- [ ] **H1 verify `canary_daa_2x`** (the 18% champion) with live warmup
      and walk-forward, judged on terminal wealth.
- [ ] **H3 yield curve as a leading signal** - the one macro shape
      findings 19/20 did not rule out (it is a price, no publication lag).
- [ ] **H8 regularised linear baseline** before any ML.

## Research track

- [x] 11 macro/cross-asset price series added (curve, copper/gold,
      crude, USD/CAD, dollar index to 1971, JNK, AGG).
- [x] FRED ingestion. Earlier "unreachable" call was **wrong**:
      `fred.stlouisfed.org` is Akamai-fronted and tarpits Python's TLS
      fingerprint, while curl succeeds from the same machine.
      `api.stlouisfed.org` is clean and answers Python directly.
- [x] ALFRED point-in-time layer (`src/vintage_data.py`) + finding 19:
      lookahead costs -0.06pp CAGR but **5.55pp of maxDD**.
- [ ] Per-sleeve signal outputs (gold/SPY/TQQQ -> bullish/bearish/bonds).
- [ ] Backtest the canary-gates-core variant (user's inverted 80/20).
- [ ] Cross-source data validator (yfinance vs HuggingFace vs the tar).
      Two known errors to catch: `BAMLH0A0HYM2` truncated to 2023-08
      when the series starts 1996, and UPRO claiming a 2000 start when
      the fund launched 2009. **The tar has never been opened.**

## Plumbing

- [x] Port the LLM fallback harness into `tests/`.
- [x] External dead-man's switch - the in-workflow heartbeat cannot
      detect its own absence.

## Done

- [x] Multi-provider LLM fallback chains (`PM_MODEL` -> `PM_MODELS`).
- [x] EOD gate keyed to cron identity, not wall clock.
- [x] `force_eod` dispatch input.
- [x] `scipy` declared in requirements (three test files could not
      collect on a clean checkout).
- [x] Repo-local `.venv` (no system Python was reachable).
- [x] XEQT US-listed proxy - VT 77% / EWC 23%, finding 17.
- [x] Signal-change alerting, upstream of the LLM step.
