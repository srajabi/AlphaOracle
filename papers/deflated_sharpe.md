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

**Next step (flagged):** implement DSR over the lab scoreboard
(`backtesting/results_lab_final/scoreboard.csv`) and report deflated Sharpes
alongside raw ones. Until then, treat scoreboard rankings as ordinal, not as
expected live performance.
