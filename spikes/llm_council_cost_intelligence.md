# LLM Council: Intelligence vs Cost (2026-06-12)

Question: best model(s) to run the daily pipeline forever; whether a
multi-model council with a chair beats single-model; what the ROI-optimal
structure looks like. Sources: [Artificial Analysis](https://artificialanalysis.ai/models)
(Intelligence Index v6, June 2026) + our measured pipeline load
(88k-token context; 222M input + ~10M output tokens/yr at 5 calls x 2
runs x 252 days).

## The field (AA Intelligence Index + our-pipeline annual cost)

| Model | AA Index | $/1M in/out | Our pipeline $/yr | Index per $100/yr |
|---|---|---|---|---|
| **deepseek-v4-flash** (current) | 47 | 0.14 / 0.28 | **$34** | 138 |
| gemini-2.5-flash | ~44 (est) | 0.15 / 0.60 | $39 | ~113 |
| gpt-5-mini (price unverified) | ~48 (est) | ~0.25 / 2.00 | ~$76 | ~63 |
| glm-5 | 49.8 | 0.60 / 1.92 | $152 | 33 |
| glm-5.1 | 51.4 | 0.98 / 3.08 | $249 | 21 |
| kimi-k2.6 | **54** (#1 open) | 0.95 / 4.00 | $251 | 22 |
| deepseek-v4-pro | 52 | 1.74 / 3.48 | $421 | 12 |
| claude-haiku-4.5 | ~50 (est) | 1.00 / 5.00 | $272 | 18 |
| claude-sonnet-4.6 | ~47-52 | 3.00 / 15.00 | $742 | 7 |

Notes: (a) user's hunch checked - GLM is NOT the smartest of the group by
AA: Kimi K2.6 (54) > V4 Pro (52) > GLM-5.1 (51.4) > GLM-5 (49.8) > V4
Flash (47). (b) Reasoning verbosity is a hidden cost: V4 Flash burned 240M
output tokens on AA's benchmark suite - thinking tokens bill as output.
Our output estimate uses 10M/yr to account for this. (c) V4 Pro pricing
differs by source ($0.435/0.87 off-peak vs $1.74/3.48 standard) - table
uses standard.

## Which benchmarks proxy OUR task

Our task = long-context financial reasoning + instruction following +
structured JSON output + synthesis across reports. Best proxies:
1. **GDPval-AA** (real-world agentic work tasks): V4 Pro 1554 > GLM-5.1
   1535 > Kimi K2.6 1484. This is the closest analogue to "be a good
   analyst on a big context" - and V4 Pro LEADS it despite Kimi's higher
   composite index.
2. AA composite index (general reasoning) - table above.
3. Long-context handling: all listed handle 128k+; our 88k context is
   within range for all.
NOT useful proxies: coding benchmarks (SWE-bench), math olympiad scores.

## Council-with-chair designs (annual cost, our measured load)

Role calls (Risk/Tech/Macro): 1512/yr; chair calls (PM + Sentinel): 1008/yr.

| Design | Council | Chair | $/yr | Verdict |
|---|---|---|---|---|
| A. Status quo | v4-flash x all | v4-flash | $34 | fine; 47-level decisions |
| **B. Smart chair (recommended)** | v4-flash x3 roles | **v4-pro** PM+Sentinel | **~$120** | 52-level + GDPval-best decisions where they matter; cheap analysis where it doesn't |
| C. Diverse council + smart chair | v4-flash + gemini-flash + glm-5 (one role each) | v4-pro | ~$190 | adds provider diversity; silicon-crowd caveat says correlated errors limit the gain |
| D. Max council | 3 providers + kimi chair + v4-pro sentinel | | ~$280 | diminishing returns |

## Recommendation

**Design B.** The evidence stack: (1) decision quality concentrates in the
chair (PM picks trades, Sentinel grades the thesis) - that's where index
points pay; (2) role-agent output is commentary consumed BY the chair -
47-level is adequate; (3) silicon-crowd finding: provider diversity buys
less than it looks (correlated errors) - so C's extra $70/yr is the first
thing to cut; (4) GDPval says V4 Pro is specifically best at the
agentic-work shape of the chair's job, and it's same-provider (one API
key, one bill). Self-consistency on the chair (sample 2x, reconcile,
~+$60/yr) is the better next dollar than a second provider.

Config change when approved: PM_MODEL + sentinel -> deepseek/deepseek-v4-pro
in the workflow env. ~$10/mo total. Revisit at the monthly thesis review
alongside AA index updates.


## ADDENDUM 2026-06-12: corrected pricing (user-supplied table)

Corrections vs the table above: Kimi K2.6 is $0.60/$2.50 (the $0.95/$4.00
was K2.7-Code); GLM-5.1 is $1.40/$4.40. Chair economics recomputed
(~89M in + 4M out/yr):

| Chair | Index | GDPval | $/yr |
|---|---|---|---|
| deepseek-v4-pro (applied) | 52 | 1554 | $168 |
| **kimi-k2.6** | **54** | 1484 | **$63** |
| glm-5.1 | 51 | 1535 | $142 (dominated by Kimi) |
| gemini-3.1-pro | 57.2 | - | $225 (frontier value) |
| sonnet-4.6 | ~54 | - | $326 (dominated) |
| gpt-5.5 | 60.2 | - | $563 (ceiling-ish; Opus 4.8 61.4 unpriced) |

Revised view: **Kimi K2.6 chair dominates v4-pro on index and cost**;
v4-pro retains the GDPval edge (1554 vs 1484 ~ 60/40 head-to-head on
agentic tasks) and same-provider simplicity. Either defensible; Kimi adds
cross-provider judge-vs-analyst decorrelation for free. The monthly thesis
review (12 runs/yr, cost rounds to zero) should use the smartest available
model regardless - frontier intelligence is effectively free at monthly
cadence. GLM eliminated: Kimi is smarter AND cheaper.


## ADDENDUM 2 (2026-06-12): PRIMARY-SOURCE VERIFIED - final numbers

Lesson learned: aggregator pricing was wrong twice. Verified directly from
provider docs (api-docs.deepseek.com, platform.kimi.ai):

| Model | Fresh in | Cached in | Out | Chair $/yr |
|---|---|---|---|---|
| deepseek-v4-pro | $0.435 | $0.003625 | $0.87 | ~$42 |
| kimi-k2.6 | $0.95 | $0.16 | $4.00 | ~$100 |

- AA's $1.74/$3.48 for V4-Pro: wrong/stale. First user table's $0.60/$2.50
  "K2.6" was actually K2.5.
- **FINAL: v4-pro chair dominates** - cheaper than Kimi, GDPval-best,
  same-provider. Design B as applied stands; Kimi's case is +2 AA index
  points at 2.4x price.
- Caching kicker: v4-pro cache-hit input is a 99.2% discount and our 88k
  context is ~80% static. Reordering build_context (static prefix first)
  drops the chair to ~$10-15/yr. Flagged as a touch-it-next-time tweak.
- Process rule going forward: MODEL PRICING ONLY FROM PROVIDER DOCS.
