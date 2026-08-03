"""
Static catalog of quantitative research entries for the Quant Lab showcase.

Each entry is a plain dict (no YAML, no DB) so the demo site stays
dependency-free and trivially hostable. Metrics are PRE-BAKED:

* provenance == "actual"   -> numbers/charts came from running the script
* provenance == "simulated"-> representative values for demo; clearly labelled
                              on the page so nothing is misrepresented

Edit this file (or the chart images under catalog_assets/) to refresh content.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Entry:
    slug: str
    title: str
    category: str                      # "strategy" | "toolkit"
    source_file: str                   # original .py / .ipynb in the Algo folder
    thesis: str                        # economical reasoning / story (markdown-ish)
    tags: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    chart: Optional[str] = None        # filename under catalog_assets/<slug>/
    provenance: str = "simulated"      # "actual" | "simulated"
    summary: Optional[str] = None      # one-liner for the index card


# --------------------------------------------------------------------------- #
#  STRATEGIES  (idea-driven backtests)
# --------------------------------------------------------------------------- #
STRATEGIES: List[Entry] = [
    Entry(
        slug="hsi_mean_reversion",
        title="HSI Futures Mean-Reversion — HKSST Short-Seller Exhaustion",
        category="strategy",
        source_file="HSI_mean_revision.py",
        provenance="actual",
        summary="Fade HSI drops when short-selling volume fails to expand (exhaustion).",
        thesis=(
            "公開數據「港股短倉成交額」(HKSST) is usually read as a bearish signal, "
            "but this strategy takes the opposite angle.\n\n"
            "**Thesis:** when the market falls yet short-selling turnover does *not* "
            "expand (short-seller exhaustion), and recent volatility has already "
            "compressed, selling pressure is likely spent — so the next session tends "
            "to mean-revert upward.\n\n"
            "**Rules:**\n"
            "1. z-score of HKSST below −0.5 (no surge in shorting)\n"
            "2. HSI daily return < 0 (down day)\n"
            "3. Vol-compression ratio A/C < 75% (stress has subsided)\n"
            "→ Go long T+1 close → exit T+2 close (1-day hold).\n\n"
            "**Economic intuition:** bears stop pressing into already-stressed, "
            "low-vol tape; with sellers absent, the path of least resistance is up. "
            "The strategy is only long ~5% of days, so its *calendar* Sharpe is modest "
            "but its *active-day* (exposure-quoted) Sharpe is materially higher."
        ),
        tags=["mean-reversion", "HSI", "short-interest", "vol-compression"],
        metrics={
            "Total Return": 0.45,
            "CAGR": 0.065,
            "Sharpe (calendar)": 0.62,
            "Sharpe (active-day)": 4.76,
            "Sharpe (exposure-adj)": 1.06,
            "Max Drawdown": -0.07,
            "Exposure": 0.052,
            "Win Rate": 0.51,
        },
        chart="equity_curve.png",
    ),
    Entry(
        slug="nikkei_usd_jpy",
        title="Nikkei / USD-JPY Macro Pairing",
        category="strategy",
        source_file="Nikkei_USD_JPY.py",
        provenance="actual",
        summary="Trade the Nikkei–USDJPY linkage on divergence of the FX-equity carry.",
        thesis=(
            "Nikkei-225 and USD/JPY are tightly linked by the export carry trade: a "
            "weaker yen lifts Japanese exporters and the equity index together.\n\n"
            "**Thesis:** when the two temporarily decouple (equity runs ahead of FX, "
            "or vice-versa), the lagging leg tends to snap back — a classic "
            "statistical-arbitrage mean-reversion across asset classes.\n\n"
            "**Rules:**\n"
            "1. Compute the rolling spread between normalised Nikkei returns and "
            "   normalised USD/JPY returns.\n"
            "2. z-score the spread over a 60-day window.\n"
            "3. Long the underperforming leg / short the overperforming leg when "
            "   |z| > 2; unwind when |z| < 0.5.\n\n"
            "**Economic intuition:** the carry trade is enforced by real capital "
            "flows (export hedging, foreign inflows), so persistent divergence is "
            "rare — the spread is bounded."
        ),
        tags=["macro", "FX", "equities", "stat-arb", "mean-reversion"],
        metrics={
            "Total Return": 0.38,
            "CAGR": 0.055,
            "Sharpe (12m)": 1.10,
            "Max Drawdown": -0.09,
            "Exposure": 0.48,
            "Win Rate": 0.55,
        },
        chart="equity_curve.png",
    ),
    Entry(
        slug="news_driven",
        title="News-Heat Sentiment Strategy (RavenPack)",
        category="strategy",
        source_file="news_driven_strategy.py",
        provenance="simulated",
        summary="Long HSI futures when 15-day news heat drops into the low percentile band.",
        thesis=(
            "Bloomberg's `NEWS_HEAT_PUB_DAVG` captures how 'unexpected' the news flow "
            "is. RavenPack's `EVENT_SENTIMENT_SCORE` and its volatility proxy the same "
            "idea.\n\n"
            "**Thesis:** low unexpected-news regimes precede calm, upward-drifting "
            "tape — the market has digested the narrative and there is no fresh "
            "negative catalyst.\n\n"
            "**Rules:**\n"
            "1. Build a composite *news-heat* score: 70% rolling-volatility percentile "
            "   + 30% inverse sentiment percentile (both `rank(pct=True)` so the two "
            "   scales are comparable).\n"
            "2. Take a 15-day MA, then its 50-day rolling percentile.\n"
            "3. Go long when the percentile ≤ 10; enter at next day's close.\n"
            "4. Net of 2 bps one-way transaction cost.\n\n"
            "**Why `rank(pct=True)`:** sentiment (−1..+1) and volatility (~0..0.3) "
            "live on different scales; ranking both to a uniform 0–1 puts them on a "
            "common footing so neither dominates by sheer magnitude."
        ),
        tags=["sentiment", "news", "alternative-data", "HSI"],
        metrics={
            "Total Return": 0.52,
            "CAGR": 0.082,
            "Sharpe (12m)": 0.95,
            "Max Drawdown": -0.11,
            "Exposure": 0.31,
            "Win Rate": 0.54,
        },
        chart="equity_curve.svg",
    ),
    Entry(
        slug="asq_market_making",
        title="Avellaneda–Stoikov Market Making w/ Inventory Cap",
        category="strategy",
        source_file="ASQ.py",
        provenance="simulated",
        summary="AS(2008) reservation-spread pricing on real L2 ticks, with a hard Q-cap.",
        thesis=(
            "Implements Avellaneda & Stoikov (2008) on Tardis L2 book-ticker data for "
            "`ZECUSDT`, with a hard inventory quota cap (`Q_MAX`).\n\n"
            "**Thesis / economic intuition:**\n"
            "The AS half-spread has two terms:\n"
            "* reservation spread `(1/γ)·ln(1+γ/k)` — the risk-neutral optimal markup\n"
            "* inventory skew proportional to `(2q+1)/2`\n\n"
            "So when long inventory (`q>0`), the bid widens and ask narrows — the MM "
            "cheapens the ask to attract buyers and offload. That is the entire "
            "economic intuition in two lines of code.\n\n"
            "**Engineering choices:**\n"
            "* Event-driven scalar loop (not vectorised) — inventory `q` is "
            "  path-dependent, so vectorisation would break causal fill semantics.\n"
            "* Tick rounding *toward* mid (conservative) — never claims edge that "
            "  doesn't survive the tick grid.\n"
            "* Two Sharpes on purpose: a step-based (2.5s) number that is "
            "  mathematically correct but financially misleading, and the daily "
            "  Sharpe an LP would actually feel.\n\n"
            "See `ASQ_ENGINEERING_DEEPDIVE.md` in the Algo folder for the full "
            "layered-architecture write-up."
        ),
        tags=["market-making", "HFT", "crypto", "inventory-management"],
        metrics={
            "PnL (per day, net fees)": 142.3,
            "Daily Sharpe": 2.31,
            "Step Sharpe (2.5s)": 6.84,
            "Max Drawdown": -0.04,
            "Inventory turnover (/day)": 96.0,
            "Fill rate": 0.38,
        },
        chart="equity_curve.svg",
    ),
]


# --------------------------------------------------------------------------- #
#  RESEARCH TOOLKITS  (methodology / factor-research notebooks)
# --------------------------------------------------------------------------- #
TOOLKITS: List[Entry] = [
    Entry(
        slug="beta_cross_sectional",
        title="Cross-Sectional Beta — Summary Statistics",
        category="toolkit",
        source_file="A01_Calculate_Beta_Walkthrough.ipynb",
        provenance="actual",
        summary="Per-year CAPM beta for Russell 1000 stocks; cross-sectional summary stats.",
        thesis=(
            "Reproduces Chapter 2 (Summary Statistics) of Bali, Engle & Murray's "
            "*Empirical Asset Pricing*.\n\n"
            "**Pipeline:**\n"
            "1. Estimate each stock's CAPM beta per calendar year using daily returns "
            "   and Kenneth French factor data.\n"
            "2. For each year compute cross-sectional summary statistics — mean, std, "
            "   skew, kurtosis, min, max, and the 5/25/50/75/95 percentiles — of the "
            "   betas across stocks.\n"
            "3. Take the *time-series average* of those summary statistics to produce "
            "   a single stable table.\n\n"
            "**Usage / demonstration purpose:** this is the canonical lens for "
            "inspecting any cross-sectional characteristic (size, value, momentum, "
            "beta, …) before sorting portfolios or running Fama-MacBeth. The notebook "
            "is the starting template for every other factor notebook (`A03b`, `A04`, "
            "`A07`)."
        ),
        tags=["factor-research", "CAPM", "cross-section", "summary-stats"],
    ),
    Entry(
        slug="beta_persistence",
        title="Beta Persistence — Hedge Decay Diagnostics",
        category="toolkit",
        source_file="A02_Persistence_Analysis.ipynb",
        provenance="actual",
        summary="Cross-sectional rank correlation of Beta across 1–5yr lags → hedge half-life.",
        thesis=(
            "Reproduces Chapter 3 (Persistence) of Bali, Engle & Murray and re-frames "
            "it as a **live-hedge risk-management primitive** rather than an academic "
            "summary statistic.\n\n"
            "## Why this matters in one sentence\n"
            "When you hedge with Beta, you are *betting that today's Beta will still "
            "be roughly correct tomorrow*. **Persistence is the number that tells you "
            "how safe that bet is.**\n\n"
            "## The failure mode it exposes\n"
            "A market-neutral book sizes its short-hedge as `Beta × Position`, "
            "computed *once* at inception. If the true Beta drifts (e.g. 1.5 → 0.8 "
            "over a quarter) and you don't re-hedge, you silently accumulate an "
            "**unintended directional bet** (net short $7M in that example). Ex-post, "
            "hedging P&L looks worse than the stock pick — and the PM usually "
            "misattributes the leak to *alpha decay* instead of a broken hedge.\n\n"
            "## Pipeline\n"
            "1. Estimate each stock's CAPM Beta per year (from `A01`).\n"
            "2. For each lag τ ∈ {1, 2, 3, 4, 5} years, compute the **cross-sectional "
            "   rank correlation** ρ(τ) between year-t and year-(t+τ) Betas.\n"
            "3. Average ρ(τ) across years → the persistence curve.\n"
            "4. **Half-life** = the lag where ρ decays to ~0.5.\n\n"
            "## How the persistence number converts into a desk decision\n"
            "* `ρ₁ = 0.84` → the average stock's Beta ranking is ~84% preserved after "
            "  one year → an annual re-hedge keeps drift bounded.\n"
            "* `ρ₃ = 0.60` → only 60% of the signal survives three years → re-hedging "
            "  every three years leaves ~40% of hedges mis-sized.\n"
            "* **Rule of thumb:** re-hedge at least twice per half-life.\n\n"
            "## Why it's a universal diagnostic\n"
            "The same persistence logic governs *any* factor hedge (size, value, "
            "momentum, stat-arb signals) and even options delta-hedging (Gamma is just "
            "the rate of Delta drift). Pre-computing persistence turns invisible hedge "
            "leakage into a measurable quantity the risk committee can budget: *'our "
            "market-neutral book carries ≈X% residual Beta drift per quarter.'*"
        ),
        tags=["factor-research", "persistence", "hedging", "risk-management", "half-life"],
    ),
    Entry(
        slug="fama_macbeth",
        title="Fama–MacBeth Two-Pass Regression",
        category="toolkit",
        source_file="A04_Fama-Macbeth_Regression.ipynb",
        provenance="actual",
        summary="Two-pass cross-sectional regression with Newey-West standard errors.",
        thesis=(
            "Implements the Fama–MacBeth (1973) procedure to estimate risk premia.\n\n"
            "**Pipeline:**\n"
            "1. **First pass (time-series):** regress each asset's returns on factors "
            "   → asset betas / factor loadings.\n"
            "2. **Second pass (cross-sectional):** for each period, regress returns "
            "   on the estimated loadings → period-by-period risk premia.\n"
            "3. Average the period premia and compute Newey–West standard errors to "
            "   handle serial correlation in the second-pass estimates.\n\n"
            "**Demonstration purpose:** the standard workhorse for testing whether a "
            "candidate factor is *priced*. Use it after `beta_cross_sectional` to "
            "decide whether beta, size, momentum, etc. actually carry a premium in "
            "your sample."
        ),
        tags=["factor-research", "Fama-MacBeth", "risk-premia", "regression"],
    ),
    Entry(
        slug="bivariate_portfolio_analysis",
        title="Bivariate Portfolio Sorts (Controlling for a 2nd Factor)",
        category="toolkit",
        source_file="A03b_Bivariate_Portfolio_Analysis.ipynb",
        provenance="actual",
        summary="Independent 5×5 sorts to isolate a factor's effect net of a confounder.",
        thesis=(
            "Bivariate (two-way) independent portfolio sorts — the method used to "
            "show that an effect survives after controlling for a related factor.\n\n"
            "**Pipeline:**\n"
            "1. Sort stocks into quintiles on factor A (e.g. size).\n"
            "2. *Independently* sort into quintiles on factor B (e.g. book-to-market).\n"
            "3. Form the 5×5 intersection portfolios; compute value-weighted returns.\n"
            "4. Average within each B-quintile across A-quintiles to get the "
            "   'B-effect controlling for A'.\n\n"
            "**Demonstration purpose:** answers the classic question 'is momentum just "
            "size?' or 'is the value premium just a beta artefact?'. Pairs naturally "
            "with `fama_maceth` as a non-parametric cross-check."
        ),
        tags=["factor-research", "portfolio-sorts", "bivariate", "controls"],
    ),
    Entry(
        slug="short_term_reversal",
        title="Short-Term Reversal Factor",
        category="toolkit",
        source_file="A07_Short_Term_Reversal.ipynb",
        provenance="actual",
        summary="1-month reversal portfolio: long last month's losers, short winners.",
        thesis=(
            "Constructs and tests the short-term-reversal (STR) anomaly.\n\n"
            "**Pipeline:**\n"
            "1. Rank stocks by prior 1-month return.\n"
            "2. Form decile portfolios; the long-short is the top-minus-bottom "
            "   (long losers, short winners) portfolio.\n"
            "3. Compute returns, alphas vs. CAPM / FF3 / FF5, and the decay profile "
            "   over 1, 3, 6, 12-month horizons.\n\n"
            "**Demonstration purpose:** STR is one of the oldest documented "
            "anomalies and the cleanest illustration of liquidity-provision / "
            "overreaction reversal. It is also a prime candidate for studying how "
            "anomaly strength decays post-publication."
        ),
        tags=["factor-research", "reversal", "anomaly", "portfolio-sorts"],
    ),
    Entry(
        slug="alpha1_rolling",
        title="Alpha #1 — HSI Rolling Expansion",
        category="toolkit",
        source_file="alpha1_HSI_expand_rolling.ipynb",
        provenance="simulated",
        summary="Custom HSI alpha signal under an expanding/rolling window design.",
        thesis=(
            "A bespoke alpha signal built on HSI constituents, evaluated under both "
            "expanding and rolling estimation windows to study signal stability.\n\n"
            "**Demonstration purpose:** showcases the full research lifecycle — signal "
            "idea → construction → IC / decay analysis → portfolio backtest → "
            "robustness across estimation windows. The notebook is the template for "
            "`alpha5` and `alpha8` variants in the folder."
        ),
        tags=["alpha-research", "HSI", "rolling-window", "IC-analysis"],
    ),
]


# --------------------------------------------------------------------------- #
#  GitHub source links (private repo; the button links to the file for demo)
# --------------------------------------------------------------------------- #
GITHUB_REPO = "https://github.com/AnsonCheung1020/Algo"


def github_url(entry: Entry) -> str:
    """Permalink to the entry's source file in the GitHub repo.

    Falls back to the repo root if no source file is set.
    """
    if entry.source_file:
        return f"{GITHUB_REPO}/blob/main/{entry.source_file}"
    return GITHUB_REPO


# --------------------------------------------------------------------------- #
#  Loader helpers
# --------------------------------------------------------------------------- #
def all_entries() -> List[Entry]:
    """Return strategies first, then toolkits (index page ordering)."""
    return STRATEGIES + TOOLKITS


def get_entry(slug: str) -> Optional[Entry]:
    for entry in all_entries():
        if entry.slug == slug:
            return entry
    return None


def by_category(category: str) -> List[Entry]:
    return [e for e in all_entries() if e.category == category]


# --------------------------------------------------------------------------- #
#  File-backed thesis override (self-editable in browser, no code edits)
# --------------------------------------------------------------------------- #
import os

_THESIS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "thesis")


def thesis_dir() -> str:
    """Absolute path to the folder holding per-slug thesis markdown overrides."""
    return _THESIS_DIR


def thesis_path(slug: str) -> str:
    return os.path.join(_THESIS_DIR, f"{slug}.md")


def get_thesis_text(slug: str) -> str:
    """Markdown text for an entry's "Idea & Economic Reasoning" section.

    A per-slug markdown file (quant_lab/thesis/<slug>.md) overrides the default
    baked into the catalog Entry, so you can edit the section in your browser
    or a text editor without touching Python.
    """
    path = thesis_path(slug)
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    entry = get_entry(slug)
    return entry.thesis if entry else ""


def save_thesis_text(slug: str, text: str) -> None:
    """Persist edited thesis markdown to thesis/<slug>.md."""
    os.makedirs(_THESIS_DIR, exist_ok=True)
    with open(thesis_path(slug), "w", encoding="utf-8") as fh:
        fh.write(text)
