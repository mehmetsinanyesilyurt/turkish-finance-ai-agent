# simple finance data fetcher for turkish stocks
# fetches data from yahoo finance and runs basic analysis

import logging
import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)


def get_stock_data(symbol: str = "GARAN.IS", period: str = "30d") -> pd.Series:
    """
    Download stock closing prices from Yahoo Finance.
    
    Args:
        symbol: Stock ticker symbol (e.g. "GARAN.IS" for Garanti Bankası)
        period: Time period to fetch (e.g. "30d", "3mo", "1y")
    
    Returns:
        pandas Series of closing prices
    
    Raises:
        ValueError: If no data is returned for the given symbol
        ConnectionError: If unable to connect to Yahoo Finance
    """
    try:
        logger.info(f"Fetching data for {symbol} (period: {period})")
        data = yf.download(symbol, period=period, progress=False)
    except Exception as e:
        logger.error(f"Failed to fetch data for {symbol}: {e}")
        raise ConnectionError(f"Could not fetch data for {symbol}. Check your internet connection.") from e
    
    if data.empty:
        raise ValueError(f"No data found for symbol '{symbol}'. Is it a valid ticker?")
    
    return data["Close"].squeeze()


def basic_analysis(prices: pd.Series) -> dict:
    """
    Run basic price trend analysis on a stock.
    
    Args:
        prices: pandas Series of closing prices
    
    Returns:
        Dictionary with start_price, end_price, change, pct_change
    """
    if len(prices) < 2:
        raise ValueError("Need at least 2 data points for analysis")
    
    start = float(prices.iloc[0])
    end = float(prices.iloc[-1])
    change = end - start
    pct = (change / start) * 100
    
    result = {
        "start_price": start,
        "end_price": end,
        "change": change,
        "pct_change": pct
    }
    
    logger.info(f"Analysis complete: {pct:+.2f}% change")
    return result

