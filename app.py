import streamlit as st
import plotly.graph_objects as go
from utils import get_categories, get_real_data
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from plotly.subplots import make_subplots

# Page config
st.set_page_config(
    page_title="Economic Metrics Dashboard",
    page_icon="📈",
    layout="wide"
)

# Title and description
st.title("📈 Economic Metrics Dashboard")
st.markdown("""
This dashboard displays various economic metrics categorized by their type.
Use the sidebar to filter metrics and adjust the time range.
""")

# Metric definitions
METRIC_DEFINITIONS = {
    # Consumption
    "GDP Growth Rate": "Real Gross Domestic Product (FRED: GDPC1) - Inflation-adjusted measure of the total value of goods and services produced in the US.",
    "Non-Farm Payroll": "Total Nonfarm Payroll (FRED: PAYEMS) - Number of U.S. workers in the economy excluding proprietors, private household employees, and farm employees.",
    "Employment Data": "Initial Unemployment Claims (FRED: ICSA) - Number of new jobless claims filed by individuals seeking unemployment benefits.",
    "Personal Finance": "Personal Savings Rate (FRED: PSAVERT) - Percentage of disposable personal income saved by individuals.",
    "Housing Sales": "New Home Sales (FRED: HSN1F) - Number of new single-family houses sold and for sale.",
    "Auto Sales": "Total Vehicle Sales (FRED: TOTALSA) - Total number of light weight vehicles sold.",
    "Retail Sales": "Retail Sales (FRED: RSXFS) - Total sales for retail and food services.",
    # Supply
    "Manufacturing PMI": "ISM Manufacturing PMI (FRED: NAPM) - Index based on surveys of manufacturing businesses, values over 50 indicate expansion.",
    "Services PMI": "ISM Services PMI (FRED: NMFCI) - Index based on surveys of service sector businesses, values over 50 indicate expansion.",
    "Housing Supply": "Building Permits (FRED: PERMIT) - Number of new housing units authorized by building permits.",
    "Manufacturing Orders": "Durable Goods Orders (FRED: DGORDER) - New orders for manufactured durable goods.",
    "Weekly Economic Index (WEI)": "NY Fed Weekly Economic Index (FRED: WEI) - An index of real economic activity using timely high-frequency data.",
    "Copper/Gold Ratio": "Ratio between Copper and Gold futures prices - A measure of economic health and inflation expectations.",
    "Oil/Gold Ratio": "Ratio between Crude Oil and Gold futures prices - An indicator of economic activity and inflation.",
    # Interest Rate
    "Key Interest Rates": "Federal Funds Rate (FRED: DFF) - The interest rate at which banks lend money to each other overnight.",
    "Credit Spread": "BAA Corporate Bond Yield minus 10-Year Treasury Yield - Measures market risk perception.",
    "VIX Index": "CBOE Volatility Index (^VIX) - Measures market's expectation of 30-day volatility.",
    # Market
    "AAII Investor Sentiment Survey": "S&P 500 as proxy - Measures individual investor sentiment (bullish vs bearish).",
    "NAAIM Manager Sentiment": "S&P 500 as proxy - Reflects professional money managers' current equity exposure.",
    "Put/Call Ratio": "S&P 500 as proxy - Ratio of put options to call options, indicating market sentiment.",
    "CFTC Commitments of Traders": "S&P 500 as proxy - Shows positions of large institutional traders.",
    "Market Breadth": "S&P 500 as proxy - Percentage of stocks above their moving averages.",
    "Sector Relative Strength": "S&P 500 as proxy - Relative performance of different market sectors."
}

def calculate_change(data):
    """Calculate percentage change safely."""
    try:
        if isinstance(data, pd.Series):
            first_value = data.iloc[0]
            last_value = data.iloc[-1]
            if isinstance(first_value, (pd.Series, pd.DataFrame)):
                first_value = first_value.iloc[0]
            if isinstance(last_value, (pd.Series, pd.DataFrame)):
                last_value = last_value.iloc[0]
            first_value = float(first_value)
            last_value = float(last_value)
            if pd.isna(first_value) or pd.isna(last_value):
                return None
            return ((last_value - first_value) / first_value) * 100
    except (TypeError, ValueError, AttributeError, IndexError) as e:
        print(f"Error calculating change: {e}")
        return None
    return None

def create_dual_axis_plot(data, yoy_data, metric):
    """Create a dual-axis plot with level and YoY growth."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add level data
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data.values,
            name=metric,
            line=dict(color='blue')
        ),
        secondary_y=False
    )
    
    # Add YoY growth
    if yoy_data is not None:
        fig.add_trace(
            go.Scatter(
                x=yoy_data.index,
                y=yoy_data.values,
                name="YoY Growth %",
                line=dict(color='red', dash='dot')
            ),
            secondary_y=True
        )
    
    # Update layout
    fig.update_layout(
        height=400,
        showlegend=True,
        hovermode='x unified',
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update axes labels
    fig.update_yaxes(title_text=metric, secondary_y=False)
    fig.update_yaxes(title_text="YoY Growth %", secondary_y=True)
    
    return fig

# Sidebar
st.sidebar.header("Settings")

# Time range selection with radio buttons
time_range = st.sidebar.radio(
    "Select Time Range",
    options=["1 Year", "2 Years", "5 Years"],
    index=0
)

# Convert selection to days
days_map = {
    "1 Year": 365,
    "2 Years": 730,
    "5 Years": 1825
}
days = days_map[time_range]

# Add refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()

# Cache the data fetching function
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_data(metric_name, days):
    return get_real_data(metric_name, days)

# Get categories and metrics
categories = get_categories()

# Create tabs for each category
tabs = st.tabs(list(categories.keys()))

# For each category tab
for tab, (category, metrics) in zip(tabs, categories.items()):
    with tab:
        st.header(category)
        
        # Create columns for metrics (2 per row)
        for i in range(0, len(metrics), 2):
            cols = st.columns(2)
            
            # First metric in the row
            with cols[0]:
                metric = metrics[i]
                st.subheader(metric)
                st.markdown(f"*{METRIC_DEFINITIONS[metric]}*")
                
                # Add loading spinner
                with st.spinner(f"Loading {metric} data..."):
                    data, yoy_data = fetch_data(metric, days)
                
                if data is not None and not data.empty:
                    fig = create_dual_axis_plot(data, yoy_data, metric)
                    
                    # Calculate and display percent change
                    pct_change = calculate_change(data)
                    if pct_change is not None:
                        color = "green" if pct_change >= 0 else "red"
                        st.markdown(f"**Change:** <span style='color:{color}'>{pct_change:.2f}%</span>", unsafe_allow_html=True)
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error("Unable to fetch data for this metric")
            
            # Second metric in the row (if exists)
            if i + 1 < len(metrics):
                with cols[1]:
                    metric = metrics[i + 1]
                    st.subheader(metric)
                    st.markdown(f"*{METRIC_DEFINITIONS[metric]}*")
                    
                    # Add loading spinner
                    with st.spinner(f"Loading {metric} data..."):
                        data, yoy_data = fetch_data(metric, days)
                    
                    if data is not None and not data.empty:
                        fig = create_dual_axis_plot(data, yoy_data, metric)
                        
                        # Calculate and display percent change
                        pct_change = calculate_change(data)
                        if pct_change is not None:
                            color = "green" if pct_change >= 0 else "red"
                            st.markdown(f"**Change:** <span style='color:{color}'>{pct_change:.2f}%</span>", unsafe_allow_html=True)
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Unable to fetch data for this metric")

# Footer
st.markdown("---")
st.markdown("""
Data sources:
- Federal Reserve Economic Data (FRED)
- Yahoo Finance
- Other financial data providers

Last updated: {}
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))) 