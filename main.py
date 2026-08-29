"""Backtest a 50-day/200-day moving-average crossover on 50 stocks.

The program downloads adjusted daily prices, creates one signal per stock,
combines the stocks with equal weights, and writes easy-to-read result files.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf


# This is a fixed, reproducible universe. It is deliberately written down
# instead of asking for today's biggest companies, which would change later.
TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "AVGO", "GOOG",
    "TSLA", "BRK-B", "LLY", "JPM", "WMT", "V", "ORCL", "XOM", "MA",
    "COST", "JNJ", "HD", "PG", "BAC", "ABBV", "CVX", "NFLX", "KO",
    "CRM", "MRK", "AMD", "PEP", "TMO", "LIN", "ACN", "MCD", "CSCO",
    "ABT", "IBM", "GE", "ADBE", "WFC", "CAT", "PM", "QCOM", "VZ",
    "INTU", "TXN", "AMGN", "ISRG", "GS", "RTX",
]
DOWNLOAD_TICKERS = TICKERS + ["SPY"]


def download_prices(start: str, end: str) -> pd.DataFrame:
    """Download adjusted closing prices, including one year of warm-up data."""
    warmup_start = (pd.Timestamp(start) - pd.Timedelta(days=370)).strftime("%Y-%m-%d")
    prices = yf.download(
        DOWNLOAD_TICKERS,
        start=warmup_start,
        end=end,
        auto_adjust=False,
        progress=False,
        group_by="column",
    )

    if prices.empty:
        raise RuntimeError("No price data was downloaded. Check your internet connection.")

    # yfinance returns a two-level table for multiple tickers.
    if isinstance(prices.columns, pd.MultiIndex):
        prices = prices["Adj Close"]
    else:
        prices = prices[["Adj Close"]].rename(columns={"Adj Close": DOWNLOAD_TICKERS[0]})

    return prices.sort_index().ffill()


def crossover_position(prices: pd.Series, fast: int = 50, slow: int = 200) -> pd.Series:
    """Return 0/1 holdings, shifted one day to prevent look-ahead bias."""
    fast_average = prices.rolling(fast, min_periods=fast).mean()
    slow_average = prices.rolling(slow, min_periods=slow).mean()

    crossed_up = (fast_average > slow_average) & (fast_average.shift(1) <= slow_average.shift(1))
    crossed_down = (fast_average < slow_average) & (fast_average.shift(1) >= slow_average.shift(1))

    # A cross changes the desired holding. Forward-fill keeps that decision
    # until the next cross; shifting means today's close is not traded today.
    desired = pd.Series(pd.NA, index=prices.index, dtype="Int64")
    desired.loc[crossed_up] = 1
    desired.loc[crossed_down] = 0
    return desired.ffill().fillna(0).shift(1).fillna(0).astype(float)


def backtest(prices: pd.DataFrame, start: str, end: str, cost_bps: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build daily strategy returns and one summary row per stock plus portfolio."""
    prices = prices.loc[start:end]
    stock_returns = prices.pct_change().fillna(0)
    strategy_prices = prices[[ticker for ticker in TICKERS if ticker in prices.columns]]
    strategy_returns = {}
    positions = {}

    for ticker in strategy_prices.columns:
        position = crossover_position(strategy_prices[ticker])
        turnover = position.diff().abs().fillna(position)
        strategy_returns[ticker] = position * stock_returns[ticker] - turnover * cost_bps / 10_000
        positions[ticker] = position

    strategy_returns = pd.DataFrame(strategy_returns).fillna(0)
    positions = pd.DataFrame(positions)
    portfolio = strategy_returns.mean(axis=1)
    benchmark = stock_returns.get("SPY", pd.Series(0.0, index=prices.index))

    returns = strategy_returns.copy()
    returns["PORTFOLIO"] = portfolio
    returns["BUY_AND_HOLD_SPY"] = benchmark

    rows = []
    for name in returns.columns:
        rows.append(summary_row(name, returns[name], positions.get(name)))
    summary = pd.DataFrame(rows).set_index("name")
    return returns, summary


def summary_row(name: str, returns: pd.Series, position: pd.Series | None) -> dict[str, float | int | str]:
    """Calculate common performance measurements from a daily return series."""
    equity = (1 + returns).cumprod()
    years = max(len(returns) / 252, 1 / 252)
    total_return = equity.iloc[-1] - 1
    annual_return = equity.iloc[-1] ** (1 / years) - 1
    annual_volatility = returns.std(ddof=1) * 252**0.5
    sharpe = annual_return / annual_volatility if annual_volatility else 0.0
    drawdown = equity / equity.cummax() - 1
    trades = int(position.diff().abs().sum()) if position is not None else 0
    return {
        "name": name,
        "total_return": total_return,
        "annual_return": annual_return,
        "annual_volatility": annual_volatility,
        "sharpe": sharpe,
        "max_drawdown": drawdown.min(),
        "trades": trades,
    }


def save_results(returns: pd.DataFrame, summary: pd.DataFrame, output: Path) -> None:
    """Write CSV files and a simple equity-curve chart."""
    output.mkdir(parents=True, exist_ok=True)
    equity = (1 + returns).cumprod()
    returns.to_csv(output / "daily_returns.csv", index_label="date")
    equity.to_csv(output / "equity_curve.csv", index_label="date")
    summary.to_csv(output / "summary.csv")

    ax = equity[["PORTFOLIO", "BUY_AND_HOLD_SPY"]].plot(figsize=(12, 6), logy=True)
    ax.set_title("50/200 Moving-Average Crossover")
    ax.set_ylabel("Growth of $1 (log scale)")
    ax.set_xlabel("Date")
    ax.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(output / "equity_curve.png", dpi=150)
    plt.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2016-01-01")
    parser.add_argument("--end", default="2026-08-29", help="End date is exclusive; this default includes data through 2026-08-28.")
    parser.add_argument("--cost-bps", type=float, default=5.0, help="Trading cost per buy/sell in basis points.")
    parser.add_argument("--output", type=Path, default=Path("results"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    prices = download_prices(args.start, args.end)
    returns, summary = backtest(prices, args.start, args.end, args.cost_bps)
    save_results(returns, summary, args.output)
    print(summary[["total_return", "annual_return", "sharpe", "max_drawdown", "trades"]].round(4).to_string())
    print(f"\nSaved results to {args.output}/")


if __name__ == "__main__":
    main()
