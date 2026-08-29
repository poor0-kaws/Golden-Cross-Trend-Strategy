# Vertex

## Strategy

The backtest applies a simple trend-following rule to 50 large, liquid US
stocks:

1. Calculate each stock's 50-trading-day moving average.
2. Calculate its 200-trading-day moving average.
3. Buy when the 50-day average crosses above the 200-day average.
4. Sell when it crosses below.

The portfolio gives each stock the same weight. It uses split- and
dividend-adjusted prices, charges 5 basis points whenever a position changes,
and waits until the next trading day after a signal before trading. That delay
prevents the backtest from using information that would not have been known at
the time of the trade.

## Historical results

The run below covers January 1, 2016 through August 28, 2026, which is the
available 2026 year-to-date period used here.

| Portfolio | Total return | Annualized return | Sharpe ratio | Max drawdown |
| --- | ---: | ---: | ---: | ---: |
| Moving-average strategy | 187.6% | 10.5% | 0.89 | −27.7% |
| Buy-and-hold SPY | 355.0% | 15.3% | 0.86 | −33.7% |

The strategy returned less than SPY over this period, although its largest
drawdown was smaller. These figures are historical estimates, not a promise of
future results.

## Run it yourself

Create the local environment, install the packages, then run the script:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

The script downloads fresh Yahoo Finance data and writes the results to
`results/`. Use `--start`, `--end`, or `--cost-bps` to test different dates or
trading costs. The end date is exclusive.
