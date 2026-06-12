# Wisdom of the Silicon Crowd (LLM Ensembles for Forecasting)

**Citation:** Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, V.,
& Tetlock, P. E. (2024). *Wisdom of the Silicon Crowd: LLM Ensemble
Prediction Capabilities Rival Human Crowd Accuracy.* Science Advances.

**Links:** [arXiv 2402.19379](https://arxiv.org/abs/2402.19379)
| PDF: [pdfs/silicon_crowd_2024.pdf](pdfs/silicon_crowd_2024.pdf)

## Claims

- 12-LLM ensemble vs 925 human forecasters on 31 binary questions over 3
  months: the LLM crowd was statistically indistinguishable from the human
  crowd (and beat no-information benchmarks).
- Individual LLMs underperform human crowds; AGGREGATION closes the gap -
  the wisdom-of-crowds mechanism transfers to machines.
- Companion finding: exposing LLMs to human crowd medians improved them
  (hybrid > either alone).

## Criticisms / boundaries

- Diversity is the engine, and LLMs share training data: cross-model error
  correlation is far higher than cross-human, so 12 LLMs buy less diversity
  than 12 independent humans. Ensembles of near-identical models converge
  to the same blind spots.
- Binary resolvable questions != open-ended market commentary; the transfer
  to "write me a market analysis" is plausible but unproven.
- Costs scale linearly with ensemble size; the marginal model adds less
  than the first.

## AlphaOracle verdict

Directly shaped pipeline design (2026-06): our agents already get most of
the cheap ensemble value from ROLE diversity (Risk/Tech/Macro/Sentinel see
the same data through different prompts) rather than provider diversity.
The evidence supports adding sampling diversity at the DECISION step
(PM self-consistency: sample 2-3x, reconcile) before paying for a second
provider; provider diversity buys mostly outage redundancy, not wisdom,
because cross-LLM errors correlate. Single cheap model (deepseek-v4-flash,
~$33/yr measured) + role diversity + rule-based signals as the
authoritative layer = our configuration.
