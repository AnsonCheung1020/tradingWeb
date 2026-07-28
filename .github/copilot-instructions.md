# Copilot Instructions for Trading Web Application

## Project Overview
This is a Django-based web application for technical analysis and stock screening. The application allows users to scan stocks based on various technical indicators and patterns.

## Project Structure
- Django project root: `/Users/tszshuncheung/Desktop/tradingWeb/tWeb/`
- Main apps:
  - `EMA821`: Screens stocks based on EMA (8, 21) golden cross patterns

## Key Workflows

### Stock Screening Process
1. Read stock symbols from CSV data files
2. Use `yfinance` to fetch historical price data
3. Apply technical indicators and pattern recognition algorithms
4. Return matching stocks to the frontend

### Adding New Screeners
Follow the pattern in `EMA821/views.py`:
1. Create a Django form for user inputs
2. Implement a view function that processes the form and runs the screener
3. Create templates for displaying results

## Technical Components

### Data Retrieval
- Stock data is fetched using `yfinance` library
- Error handling with retry logic is implemented for data fetching
- Example:
```python
max_retries = 3
for attempt in range(max_retries):
    try:
        df = yf.download(stock, start, now)
        if df.empty:
            raise ValueError("No data returned")
        break
    except Exception as e:
        print(f"Error retrieving data for {stock} on attempt {attempt + 1}: {e}")
```

### Technical Analysis
- Common technical indicators are calculated using pandas operations:
  - Exponential Moving Averages (EMA): `df['Close'].ewm(span=8).mean()`
  - MACD: Calculated as difference between fast and slow EMAs
- Helper functions like `cross()`, `increasing()`, and `cross_within_period()` are used for pattern detection

### Data Validation
- Check for sufficient data points before analysis
- Validate data quality and handle missing values
- Skip stocks with insufficient trading volume

## Conventions

### Function Naming
- `cross()`: Detects crossover between two parameters
- `increasing()`: Checks if parameter is increasing over a period
- `cross_within_period()`: Finds crossover within specified time range

### Error Handling
- Use try/except blocks for external API calls
- Implement retry logic for network operations
- Print informative error messages that include stock symbol and error details

## Project Dependencies
- Django: Web framework
- pandas: Data manipulation
- yfinance: Yahoo Finance data retrieval
- numpy: Numerical operations
- matplotlib (likely used for charts, though not visible in provided code)

## Data Files
- Stock lists are stored in CSV format: `data/3B_Total.csv`

## Common Tasks
- To run a stock screener, post a form with parameters to the appropriate view
- To add new technical indicators, implement them as functions that operate on pandas DataFrames
