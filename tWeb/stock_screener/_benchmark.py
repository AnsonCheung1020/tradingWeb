"""Benchmark: original serial yf.download loop vs new bulk_download().

Picks a representative sample of valid tickers, runs BOTH approaches on the SAME
data, and reports wall-clock time + per-ticker average. Uses a modest sample so
we don't hammer Yahoo / trip the rate limit during the test.
"""
import os
import sys
import time
import datetime as dt
import yfinance as yf

# Make the Django project dir (parent of stock_screener/) importable as a package root.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
from stock_screener.bulk_fetch import bulk_download

# A sample of liquid, definitely-valid US tickers (avoids delisted noise).
SAMPLE = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AMD", "INTC", "NFLX",
    "JPM", "V", "JNJ", "WMT", "PG", "MA", "UNH", "HD", "DIS", "BAC",
    "XOM", "CVX", "PFE", "KO", "PEP", "MRK", "ABBV", "T", "VZ", "ORCL",
]

start = dt.datetime.now() - dt.timedelta(days=150)
end = dt.datetime.now()

print(f"Benchmarking {len(SAMPLE)} tickers over ~150 days...\n")

# ---------- Approach A: original serial per-ticker loop ----------
t0 = time.perf_counter()
serial_ok = 0
for sym in SAMPLE:
    try:
        df = yf.download(sym, start=start, end=end, auto_adjust=True,
                         progress=False, ignore_tz=True)
        if df is not None and not df.empty and len(df) >= 80:
            serial_ok += 1
    except Exception as e:
        print(f"  {sym} error: {e}")
t_serial = time.perf_counter() - t0
print(f"[A] Serial per-ticker: {t_serial:6.2f}s total | "
      f"{t_serial/len(SAMPLE)*1000:5.0f} ms/ticker | {serial_ok}/{len(SAMPLE)} ok")

# Be gentle with Yahoo between the two runs.
time.sleep(3)

# ---------- Approach B: new batched bulk_download ----------
t0 = time.perf_counter()
data = bulk_download(SAMPLE, start, end, batch_size=100, inter_batch_delay=0.75)
t_bulk = time.perf_counter() - t0
print(f"[B] Batched bulk_download: {t_bulk:6.2f}s total | "
      f"{t_bulk/len(SAMPLE)*1000:5.0f} ms/ticker | {len(data)}/{len(SAMPLE)} ok")

# ---------- Summary ----------
speedup = t_serial / t_bulk if t_bulk > 0 else float("inf")
print(f"\nSpeedup: {speedup:.2f}x  ({t_serial:.1f}s -> {t_bulk:.1f}s for {len(SAMPLE)} tickers)")
print(f"Projected for 5,482 symbols:")
print(f"  Serial  ~{t_serial/len(SAMPLE)*5482/60:6.1f} min")
print(f"  Batched ~{t_bulk/len(SAMPLE)*5482/60:6.1f} min")