import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from fredapi import Fred
from pandas_datareader import data as pdr
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import streamlit as st

# Try to load from .env file (local development)
load_dotenv()

# Get FRED API key from environment or Streamlit secrets
fred_api_key = os.getenv('FRED_API_KEY') or st.secrets.get("FRED_API_KEY")
if not fred_api_key:
    raise ValueError("FRED API key not found. Please set it in .env file or Streamlit secrets.")

# Initialize API clients
fred = Fred(api_key=fred_api_key)

def get_categories():
    """Return the categories and their corresponding metrics."""
    return {
        "Consumption": [
            "GDP Growth Rate",
            "Non-Farm Payroll",
            "Employment Data",
            "Personal Finance",
            "Housing Sales",
            "Auto Sales",
            "Retail Sales"
        ],
        "Supply": [
            "Manufacturing PMI",
            "Services PMI",
            "Housing Supply",
            "Manufacturing Orders",
            "Weekly Economic Index (WEI)",
            "Copper/Gold Ratio",
            "Oil/Gold Ratio"
        ],
        "Interest Rate": [
            "Key Interest Rates",
            "Credit Spread",
            "VIX Index"
        ],
        "Market": [
            "AAII Investor Sentiment Survey",
            "NAAIM Manager Sentiment",
            "Put/Call Ratio",
            "CFTC Commitments of Traders",
            "Market Breadth",
            "Sector Relative Strength"
        ]
    }

def calculate_yoy_growth(data):
    """Calculate year-over-year growth for a time series."""
    try:
        # Resample to ensure we have data for every day
        daily_data = data.asfreq('D', method='ffill')
        # Calculate YoY growth
        yoy_growth = daily_data.pct_change(periods=365) * 100
        return yoy_growth
    except Exception as e:
        print(f"Error calculating YoY growth: {e}")
        return None

def get_fred_data(series_id, days=365):
    """Helper function to fetch data from FRED."""
    try:
        end_date = datetime.now()
        # Add extra year to calculate YoY growth
        start_date = end_date - timedelta(days=days+365)
        data = fred.get_series(series_id, start_date, end_date)
        # Convert to float64 and handle NaN values
        return pd.Series(data.astype(float), index=data.index).fillna(method='ffill')
    except Exception as e:
        print(f"Error fetching FRED data for {series_id}: {e}")
        return None

def get_ratio_data(numerator_ticker, denominator_ticker, days=365):
    """Helper function to calculate ratio between two assets."""
    try:
        end_date = datetime.now()
        # Add extra year to calculate YoY growth
        start_date = end_date - timedelta(days=days+365)
        
        numerator = yf.download(numerator_ticker, start=start_date, end=end_date, progress=False)['Close']
        denominator = yf.download(denominator_ticker, start=start_date, end=end_date, progress=False)['Close']
        
        # Align dates and calculate ratio
        ratio = numerator.div(denominator)
        return ratio.astype(float).fillna(method='ffill')
    except Exception as e:
        print(f"Error calculating ratio: {e}")
        return None

def get_market_data(ticker, days=365):
    """Helper function to fetch market data."""
    try:
        end_date = datetime.now()
        # Add extra year to calculate YoY growth
        start_date = end_date - timedelta(days=days+365)
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)['Close']
        return data.astype(float).fillna(method='ffill')
    except Exception as e:
        print(f"Error fetching market data for {ticker}: {e}")
        return None

def get_real_data(metric_name, days=365):
    """
    Get real data for each metric from various sources.
    Returns a tuple of (level_data, yoy_growth)
    """
    try:
        data = None
        
        # Consumption
        if metric_name == "GDP Growth Rate":
            data = get_fred_data('GDPC1', days)  # Real GDP
            
        elif metric_name == "Non-Farm Payroll":
            data = get_fred_data('PAYEMS', days)  # Total Nonfarm Payroll
            
        elif metric_name == "Employment Data":
            data = get_fred_data('ICSA', days)
            
        elif metric_name == "Personal Finance":
            data = get_fred_data('PSAVERT', days)
            
        elif metric_name == "Housing Sales":
            data = get_fred_data('HSN1F', days)
            
        elif metric_name == "Auto Sales":
            data = get_fred_data('TOTALSA', days)
            
        elif metric_name == "Retail Sales":
            data = get_fred_data('RSXFS', days)
            
        # Supply
        elif metric_name == "Manufacturing PMI":
            data = get_fred_data('NAPM', days)  # ISM Manufacturing PMI
            
        elif metric_name == "Services PMI":
            data = get_fred_data('NMFCI', days)  # ISM Services PMI
            
        elif metric_name == "Housing Supply":
            data = get_fred_data('PERMIT', days)
            
        elif metric_name == "Manufacturing Orders":
            data = get_fred_data('DGORDER', days)
            
        elif metric_name == "Weekly Economic Index (WEI)":
            data = get_fred_data('WEI', days)
            
        elif metric_name == "Copper/Gold Ratio":
            data = get_ratio_data('HG=F', 'GC=F', days)
            
        elif metric_name == "Oil/Gold Ratio":
            data = get_ratio_data('CL=F', 'GC=F', days)
            
        # Interest Rate
        elif metric_name == "Key Interest Rates":
            data = get_fred_data('DFF', days)
            
        elif metric_name == "Credit Spread":
            baa = get_fred_data('BAA', days)
            treasury = get_fred_data('DGS10', days)
            if baa is not None and treasury is not None:
                data = (baa - treasury).fillna(method='ffill')
            
        elif metric_name == "VIX Index":
            data = get_market_data('^VIX', days)
            
        # Market (default to S&P 500 for market metrics)
        else:
            data = get_market_data('^GSPC', days)
        
        if data is not None:
            # Calculate YoY growth
            yoy_growth = calculate_yoy_growth(data)
            # Trim both series to requested time range
            if len(data) > days:
                data = data.iloc[-days:]
            if yoy_growth is not None and len(yoy_growth) > days:
                yoy_growth = yoy_growth.iloc[-days:]
            return data, yoy_growth
            
        return None, None
            
    except Exception as e:
        print(f"Error fetching data for {metric_name}: {e}")
        return None, None 