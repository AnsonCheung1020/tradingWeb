"""
Bulk downloader for yfinance designed to stay under Yahoo's rate limit (HTTP 429).

Why not asyncio around yfinance?
--------------------------------
yfinance is a *blocking* library built on top of `requests`. Putting
`yf.download()` inside an `async def` and awaiting `asyncio.gather()` does NOT
make the calls concurrent: each call blocks the single event-loop thread, so the
calls run serially anyway, and they still trigger Yahoo's rate limit because the
HTTP requests are still fired.

To get true concurrency you would need `asyncio.to_thread` / `run_in_executor`,
but high thread-concurrency against Yahoo triggers *more* HTTP 429 errors.

The idiomatic, rate-limit-friendly way to bulk fetch with yfinance is to pass
MANY tickers to a single `yf.download()` call (the library reuses one session and
batches the requests internally via its own thread pool), chunk the symbol list
into batches, and sleep a little between batches. The analysis is then performed
on the in-memory data with zero network calls.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, Iterable, List

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


def _download_batch(
    tickers: List[str],
    start,
    end,
    *,
    max_retries: int = 3,
    **kwargs,
) -> pd.DataFrame:
    """Download one batch of tickers with exponential backoff on failure.

    yfinance/Yahoo occasionally returns HTTP 429 (Too Many Requests). We retry
    the whole batch with increasing delay instead of failing the whole run.
    """
    backoff = 2.0
    last_exc: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            df = yf.download(
                tickers,
                start=start,
                end=end,
                threads=True,          # let yfinance manage internal concurrency
                group_by="column",     # (field, ticker) columns -> easy per-ticker slice
                progress=False,
                ignore_tz=True,
                **kwargs,
            )
            return df
        except Exception as exc:  # noqa: BLE001 - we want to retry on any error
            last_exc = exc
            logger.warning(
                "Batch %s attempt %d/%d failed: %s",
                tickers[:3],
                attempt,
                max_retries,
                exc,
            )
            if attempt < max_retries:
                time.sleep(backoff)
                backoff *= 2
    # Out of retries: return empty frame rather than killing the whole run.
    logger.error("Batch %s permanently failed after %d attempts: %s",
                 tickers[:3], max_retries, last_exc)
    return pd.DataFrame()


def bulk_download(
    symbols: Iterable[str],
    start,
    end,
    *,
    batch_size: int = 100,
    inter_batch_delay: float = 0.75,
    auto_adjust: bool = True,
    **kwargs,
) -> Dict[str, pd.DataFrame]:
    """Bulk-download OHLCV for many symbols and return ``{symbol: DataFrame}``.

    Strategy
    --------
    Chunk the symbols into batches of ``batch_size`` and call ``yf.download``
    ONCE per batch. This drastically reduces the number of HTTP sessions compared
    to per-ticker calls and lets yfinance's internal thread pool + session reuse
    manage concurrency, which keeps us under Yahoo's rate limit. A short sleep
    between batches further throttles request volume.

    Parameters
    ----------
    symbols : iterable of str
        Tickers, e.g. taken from the Excel/CSV symbol list.
    start, end : datetime-like
        Date range passed straight to ``yf.download``.
    batch_size : int
        Tickers per ``yf.download`` call. ~100 is a safe sweet spot.
    inter_batch_delay : float
        Seconds to sleep between batches to respect rate limits.

    Returns
    -------
    dict
        Mapping ``symbol -> per-ticker DataFrame`` with flat columns
        ``['Open', 'High', 'Low', 'Close', 'Volume']`` (matching the shape a
        single-ticker ``yf.download`` returns, so existing analysis code works
        unchanged).
    """
    symbols = [str(s).strip() for s in symbols if str(s).strip()]
    result: Dict[str, pd.DataFrame] = {}

    for i in range(0, len(symbols), batch_size):
        batch = symbols[i : i + batch_size]
        logger.info(
            "Fetching batch %d-%d / %d (%d tickers)",
            i + 1,
            i + len(batch),
            len(symbols),
            len(batch),
        )

        wide = _download_batch(batch, start, end, auto_adjust=auto_adjust, **kwargs)

        # Multi-ticker download -> columns are (field, ticker). Single-ticker
        # or empty result -> nothing to split.
        if wide is None or wide.empty or wide.columns.nlevels < 2:
            logger.warning("Batch starting at %d returned no usable data", i)
            if i + batch_size < len(symbols):
                time.sleep(inter_batch_delay)
            continue

        for symbol in batch:
            try:
                # xs on the 'Ticker' level yields flat OHLCV columns for one symbol.
                sub = wide.xs(symbol, level="Ticker", axis=1)
            except KeyError:
                # Ticker was not present in the response (delisted / invalid).
                continue
            if sub.dropna(how="all").empty:
                continue
            result[symbol] = sub

        if i + batch_size < len(symbols):
            time.sleep(inter_batch_delay)

    return result