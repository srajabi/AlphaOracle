# Papers Library

Academic and practitioner research underpinning AlphaOracle's strategies.
Each note records: citation, where to get it, the paper's claims, known
criticisms, and - most importantly - **what happened when we tested it on our
own data** (with pointers to the backtest results).

PDFs live in `pdfs/` where a freely-hosted copy exists; SSRN-gated papers are
notes-only with links.

## Index

| Note | Paper | Our implementation | Our verdict |
|---|---|---|---|
| [beyond_status_quo.md](beyond_status_quo.md) | Anarkulova, Cederburg & O'Doherty (2023) | `entry_strategies.py` decumulation mode | Equity edge real at long horizons; ruin tail matches critics; SMA overlay fixes the behavioral problem |
| [faber_qtaa.md](faber_qtaa.md) | Faber (2007, upd. 2013) | `gtaa_5_faber`, `sma200_monthly_spy` | Confirmed: -12% maxDD over 21y; monthly beats daily |
| [time_series_momentum.md](time_series_momentum.md) | Moskowitz, Ooi & Pedersen (2012) | `tsmom_12_1_spy` | Works: Sharpe 0.71 vs 0.56 B&H over 33y |
| [volatility_managed_portfolios.md](volatility_managed_portfolios.md) | Moreira & Muir (2017) | `vol_target_spy_15`, `vol_target_qqq_2x` | Only leverage scheme that survived dot-com |
| [keller_vaa.md](keller_vaa.md) | Keller & Keuning (2017) | `keller_vaa_lite` | Underperformed with our proxies (Sharpe 0.49) |
| [keller_daa.md](keller_daa.md) | Keller & Keuning (2018) | `canary_daa_lite` + variants | Best idea in the strategy lab (Sharpe 1.06-1.21) |
| [keller_baa.md](keller_baa.md) | Keller (2022) | not yet implemented | Candidate: BAA's dual-momentum refinement |
| [antonacci_dual_momentum.md](antonacci_dual_momentum.md) | Antonacci (2012) | `gem_dual_momentum` | Weak with EWA proxy (Sharpe 0.45); needs better intl data |
| [deflated_sharpe.md](deflated_sharpe.md) | Bailey & López de Prado (2014) | not yet - flagged | Aimed at us: 27 tested strategies = selection bias; DSR over the scoreboard is the next step |
| [tug_of_war_overnight.md](tug_of_war_overnight.md) | Lou, Polk & Skouras (2019) | not yet - round-4 candidate | Overnight premium; testable with our OHLC data |
| [jegadeesh_titman_momentum.md](jegadeesh_titman_momentum.md) | Jegadeesh & Titman (1993) | momentum family ancestor | Our results: momentum selection needs a trend filter to remove the left tail |
| [cash_overlay_filters.md](cash_overlay_filters.md) | Xiong (2026, arXiv) | not yet - round-4 candidate | Continuous slow+fast cash overlay; retest on 2004+ before trusting |
| [factor_zoo_census.md](factor_zoo_census.md) | Harvey & Liu (2019) | meta-source | 400+ factor catalog + t>3 multiple-testing bar; use to vet new ideas |
| [lazy_prices.md](lazy_prices.md) | Cohen, Malloy & Nguyen (2020) | not implementable (long-only ETFs) | Filing-change alpha; possible future LLM-analyst risk signal |
| [asness_why_not_100_equities.md](asness_why_not_100_equities.md) | Asness (1996, upd. 2023) | `hfea_lite_2x`, `spy_tlt_60_40` | Diversify-then-lever beats concentration on Sharpe - confirmed; needs a crisis gate (2022) |
| [lo_quants_august_2007.md](lo_quants_august_2007.md) | Khandani & Lo (2007) | warning label | Factor crowding risk; pairs with deflated Sharpe as the two live-failure modes |
| [peterson_strategy_development.md](peterson_strategy_development.md) | Peterson (2017) | methodology bible | Exposes our gaps: parameter-stability tests, DSR, cost stress tests. His 60-entry .bib included |
| [slow_momentum_fast_reversion.md](slow_momentum_fast_reversion.md) | Wood, Roberts & Zohren (2021) | not yet - round-4 candidate | Changepoint gate fixes trend's regime-turn bleed (our COVID failure mode) |
| [volatility_effect_low_vol.md](volatility_effect_low_vol.md) | Blitz & van Vliet (2007) | tested - honest negative at sector granularity | Low-vol is a single-stock effect; sectors diversify it away |
| [day_trading_evidence.md](day_trading_evidence.md) | Barber/Lee/Liu/Odean (2014), Chague et al (2020) | out of scope, by evidence | 97-99% of persistent day traders lose; winners run institutional mechanics |
| [gao_intraday_momentum.md](gao_intraday_momentum.md) | Gao, Han, Li & Zhou (2018) | blocked on intraday data | First half-hour predicts last; Alpaca bars flagged for future replication |
| [rockafellar_uryasev_cvar.md](rockafellar_uryasev_cvar.md) | Rockafellar & Uryasev (2000) | adopted - `cvar()` in validation.py | Expected shortfall now on every scoreboard row |

## Books (`books/`)

| File | What it is | Status |
|---|---|---|
| `kakushadze_151_trading_strategies_es.pdf` | Kakushadze & Serur, *151 Trading Strategies* - 150+ strategies with 550+ formulas across all asset classes. The arXiv-hosted edition ([1912.04492](https://arxiv.org/abs/1912.04492)) is the Spanish translation - formulas are language-independent; English edition is Springer/SSRN-gated | strategy idea catalog for future rounds |
| `rao_jelvis_rl_finance.pdf` | Rao & Jelvis, *Foundations of RL with Applications in Finance* - free final draft from [Stanford](https://stanford.edu/~ashlearn/RLForFinanceBook/book.pdf), 500+ pages | reference for any future ML/RL work; out of current scope |

Also book-class but linked-only: Lopez de Prado's AFML seminar slides
([quantresearch.org](https://www.quantresearch.org/Lectures.htm)), the
Quantopian lecture series ([GitHub](https://github.com/quantopian/research_public)),
QuantEcon ([quantecon.org](https://quantecon.org)).

## Paper sources (recurring hunting grounds)

- **vince.quant** ([Instagram](https://www.instagram.com/vince.quant/)) - daily
  paper explainers with full citations in captions; consistently real papers
- **arXiv [q-fin](https://arxiv.org/archive/q-fin)** - especially q-fin.PM
  (portfolio management); all PDFs free
- **r/quant** favorite-papers threads ([1](https://www.reddit.com/r/quant/comments/1czq24r/what_are_your_favorite_quant_papers_ranked_by/),
  [2](https://www.reddit.com/r/quant/comments/vb4suz/what_are_some_examples_of_academic_papers_that/))
  and [r/algotrading](https://www.reddit.com/r/algotrading/) - practitioner
  canon (Jegadeesh-Titman, pairs trading, Almgren-Chriss, López de Prado)
- **[Allocate Smartly](https://allocatesmartly.com/)** - independent
  out-of-sample tracking of published TAA strategies (Keller, Faber, etc.)
- **Author sites** for legal PDFs: davidhbailey.com, LSE/NYU personal pages,
  NBER working papers, mebfaber.com
- **Internet Archive**: [scholar.archive.org](https://scholar.archive.org)
  full-text searches open-access journal papers; the
  [Wayback Machine](https://web.archive.org) recovers PDFs from dead
  author-page links. Tested 2026-06: neither unlocks SSRN-only working papers
  (Keller/Antonacci remain gated) - SSRN landing pages are archived, the
  Delivery.cfm PDFs are not.
- **Reddit**: unauthenticated access is fully closed (web, old.reddit, and
  .json all blocked). Reading r/quant / r/algotrading programmatically needs
  official API OAuth credentials (free personal app at reddit.com/prefs/apps).
  Workaround that works fine: paste thread contents into the chat.
- **WifeyAlpha paper board** ([miro](https://miro.com/app/board/uXjVOynzlbI=/)) -
  community compilation of papers from WifeyAlpha's threads. Canvas-rendered,
  so browse manually and bring papers back by citation. (The companion GitHub
  repo from the r/quant thread is gone.)
- **Peterson's bibliography** ([peterson_bibliography.bib](peterson_bibliography.bib),
  60 entries) - curated practitioner reading list from the quantstrat author;
  the braverock.com HTML version 403s but the source lives in
  [braverock/quantstrat](https://github.com/braverock/quantstrat/tree/master/sandbox/backtest_musings)
- **Oxford-Man Institute** ([selected publications](https://oxford-man.ox.ac.uk/selected-publications/)) -
  ML-heavy momentum/vol/regime research; mostly arXiv-free PDFs
- **AQR Insights/Research** ([aqr.com](https://www.aqr.com/Insights)) -
  accessible practitioner whitepapers (Asness et al.)
- **#QuantLinkADay roundups** ([Turnleaf Analytics](https://turnleafanalytics.com/hundreds-of-quant-papers-from-quantlinkaday-in-2025/)) -
  Saeed Amen's ~365 papers/year, compiled annually since 2016; heavy on
  macro/FX/ML but includes TAA and trend-following
- **[Quantpedia](https://quantpedia.com/)** - encyclopedia of published
  strategies with backtest summaries; free tier covers strategy descriptions
- **Robeco's [most important quant papers](https://www.robeco.com/en-us/about-us/key-strengths/quant/our-most-important-quant-papers)** -
  the low-vol/conservative-investing canon (Blitz, van Vliet)
- **Journals**: [PM-Research](https://www.pm-research.com/topic/quantitative-finance)
  (JPM etc., paywalled - notes-with-links), Journal of Financial Data Science,
  JFE/JF/RFS via author preprint pages
- **Blocked-site technique**: prefer OFFICIAL APIs over scraping -
  Hacker News via `hn.algolia.com/api/v1/items/<id>`, StackExchange via
  `api.stackexchange.com` (both tested, work from plain curl), Reddit via
  OAuth app. Scrapers that fight anti-bot walls are fragile and usually
  against ToS; if there's no API, paste content into chat or browse manually.
- **Policy: legal sources only.** No sci-hub - author pages, arXiv, NBER,
  SSRN-ungated, and publisher OA cover nearly everything we need; gated
  papers get notes-with-links.
- **Out of scope for AlphaOracle** (noted so we stop re-evaluating them):
  market-making (Avellaneda-Stoikov), optimal execution (Almgren-Chriss),
  rough-volatility option pricing, Cartea's HFT book, institutional intraday
  stat-arb (Kakushadze mean-reversion - PDF kept for reference) - all require
  order-book access / infrastructure we don't have.

## Conventions

- File name: short slug of the paper, `.md`
- Note structure: Citation / Links / Claims / Criticisms / AlphaOracle verdict
- When a strategy from a paper is implemented, link the note from the
  strategy's docstring and record the backtest verdict here after running it
- Add PDFs only when freely/legally hosted (arXiv, NBER, author sites)
