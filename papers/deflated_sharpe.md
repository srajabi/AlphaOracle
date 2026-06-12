# The Deflated Sharpe Ratio / Probability of Backtest Overfitting

**Citation:** Bailey, D. H., & López de Prado, M. (2014). *The Deflated Sharpe
Ratio: Correcting for Selection Bias, Backtest Overfitting and
Non-Normality.* Journal of Portfolio Management. Companion: Bailey, Borwein,
López de Prado & Zhu (2017), *The Probability of Backtest Overfitting,*
Journal of Computational Finance; López de Prado, *Advances in Financial
Machine Learning* (2018) for CPCV.

**Links:** [Author PDF](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)
| PDF: [pdfs/deflated_sharpe_2014.pdf](pdfs/deflated_sharpe_2014.pdf)
| Found via vince.quant's CPCV explainer.

## Claims

- When you test N strategies and report the best one, the expected maximum
  Sharpe under the null (no skill) grows with N - most "discoveries" are
  selection bias.
- The Deflated Sharpe Ratio (DSR) corrects the observed Sharpe for the number
  of trials, non-normality (skew/kurtosis), and track-record length.
- CPCV (combinatorial purged cross-validation) generates a DISTRIBUTION of
  backtest paths instead of one, enabling a Probability of Backtest
  Overfitting (PBO) estimate.

## Criticisms

- Requires an honest count of trials N - researchers undercount (every
  parameter tweak is a trial).
- DSR assumes trials are roughly independent; correlated strategy variants
  (ours are highly correlated) inflate the effective N less than the raw N.

## AlphaOracle verdict

**This paper is aimed directly at us.** The strategy lab tested 27 strategies
and reported the best (Sharpe 1.21). Under multiple testing, the expected max
Sharpe from 27 correlated-but-distinct trials on ~21y of data is materially
above 0 - some of our scoreboard edge is selection bias by construction.

Mitigating factors: our strategies are implementations of PUBLISHED rules
(hypotheses fixed before seeing our data, mostly), not parameter sweeps; and
the top performers replicate their papers' claims out-of-sample relative to
the papers' own samples.

**IMPLEMENTED (2026-06, `backtesting/validation.py` + `run_validation.py`):**
DSR, stationary-bootstrap Monte Carlo, circular-shift permutation tests, and
CSCV PBO now run over every registered strategy on one uniform 21y window
(scoreboard: `backtesting/results_validation/scoreboard_v2.csv`). Findings:

- **PBO = 0.36** across 48 strategies - below the 0.5 noise level: in-sample
  winners genuinely tend to stay above-median out-of-sample. Selection bias
  exists but the rankings carry real signal.
- The top strategies (lab_winners_blend, canary family, dual-channel
  overlay, risk parity) survive deflation with DSR prob >= 0.998 and have
  bootstrap 5th-percentile Sharpes of 0.67-0.85.
- Permutation tests split real timing (canary p~0.01, vol-target p=0.007,
  blend p=0.000) from structureless luck (vix_spike_buyer p=0.977).
- 46 pytest tests cover the framework, including per-strategy no-lookahead
  causality checks - which immediately caught a real engine bug (initial
  entry cost never charged).
