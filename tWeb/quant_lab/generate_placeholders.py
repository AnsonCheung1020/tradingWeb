"""Generate clearly-labelled placeholder equity-curve SVGs for simulated
strategy entries that have no pre-computed chart yet.

Pure-Python (no matplotlib / Pillow) so it runs in any environment.

Run once (offline):  python quant_lab/generate_placeholders.py
"""
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(HERE, "..", "static", "quant_lab")

# slug -> (final multiple, annualised vol, label)
SPECS = {
    "news_driven": (1.52, 0.11, "News-Heat Sentiment (illustrative)"),
    "asq_market_making": (1.85, 0.06, "ASQ Market-Making PnL (illustrative)"),
}


def synthetic_equity(final_multiple: float, vol: float, days: int = 252, seed: int = 42):
    """Geometric-Brownian-motion-style curve ending exactly at final_multiple."""
    rng = random.Random(seed)
    target_cagr = final_multiple ** (252 / days) - 1
    mu_daily = target_cagr / 252
    sigma_daily = vol / math.sqrt(252)
    cum = 1.0
    series = [cum]
    for _ in range(days - 1):
        # Box-Muller for a normal sample
        u1 = rng.random() or 1e-9
        u2 = rng.random()
        z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
        cum *= 1 + mu_daily + sigma_daily * z
        series.append(cum)
    # Rescale so the endpoint matches exactly (honest shape, honest endpoint).
    end = series[-1]
    return [v * final_multiple / end for v in series]


def write_svg(path: str, series, title: str):
    w, h, pad = 720, 320, 44
    plot_w, plot_h = w - 2 * pad, h - 2 * pad
    n = len(series)
    ymin, ymax = min(min(series), 1.0), max(series)
    span = ymax - ymin or 1.0
    ymin -= span * 0.08
    ymax += span * 0.08

    def x(i):
        return pad + (i / (n - 1)) * plot_w

    def y(v):
        return pad + plot_h - ((v - ymin) / (ymax - ymin)) * plot_h

    points = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(series))
    baseline = y(1.0)

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="Arial, sans-serif">
  <rect width="{w}" height="{h}" fill="#ffffff"/>
  <text x="{w/2:.0f}" y="26" text-anchor="middle" font-size="15" font-weight="bold" fill="#111827">{title}</text>
  <line x1="{pad}" y1="{baseline:.1f}" x2="{w-pad}" y2="{baseline:.1f}" stroke="#9ca3af" stroke-width="1" stroke-dasharray="5,4"/>
  <text x="{pad}" y="{baseline-6:.1f}" font-size="10" fill="#9ca3af">1.0</text>
  <polyline points="{points}" fill="none" stroke="#2563eb" stroke-width="2"/>
  <text x="{w-pad}" y="{h-12}" text-anchor="end" font-size="10" font-style="italic" fill="#92400e">Illustrative — simulated placeholder, not a live backtest</text>
</svg>
"""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(svg)


def main():
    for slug, (mult, vol, label) in SPECS.items():
        eq = synthetic_equity(mult, vol)
        out_dir = os.path.join(STATIC, slug)
        os.makedirs(out_dir, exist_ok=True)
        out = os.path.join(out_dir, "equity_curve.svg")
        write_svg(out, eq, label)
        print(f"  wrote {out}")


if __name__ == "__main__":
    main()