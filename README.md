# DCF Valuation Model

An automated Discounted Cash Flow model built in Python that pulls live financials for any public company and outputs an implied price per share with full transparency on assumptions, projections, and valuation drivers.

## What It Does

- Pulls income statement, balance sheet, and cash flow data via yfinance for any ticker
- Auto-suggests reasonable DCF assumptions based on company sector, beta, recent revenue growth, and profit margins
- Calculates effective tax rate, unlevered free cash flow, and 5-year projections with fading growth toward terminal rate
- Discounts cash flows back to present using WACC and computes terminal value via Gordon Growth Model
- Outputs Enterprise Value, Equity Value, and Implied Price Per Share

## How It Works

1. User inputs a ticker (e.g. AAPL)
2. Function pulls 5 years of historical financials and most recent net debt and share count
3. Suggested assumptions function pulls real metrics (revenue growth, profit margin, beta, sector) to recommend defaults
4. DCF function projects UFCF with linearly fading growth from year 1 rate to terminal rate
5. Each projected cash flow is discounted by (1 + WACC)^year
6. Terminal value calculated using Gordon Growth Model and discounted back
7. Enterprise Value summed, Net Debt subtracted, divided by diluted shares for implied price per share

## Tech Stack

- Python 3.14
- yfinance for live financial data
- pandas for data manipulation
- Jupyter Notebook for interactive analysis

## Example Output

DCF VALUATION: AAPL

Implied Price Per Share: $174.66

Enterprise Value: $2,683.5B

Equity Value: $2,620.7B

## Author

Marvin Patel  
Finance, Rutgers Business School  
[LinkedIn](https://www.linkedin.com/in/patelmarvin)
