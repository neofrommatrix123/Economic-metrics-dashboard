# Economic Metrics Dashboard

A comprehensive dashboard built with Streamlit that visualizes various economic metrics including GDP, employment data, market indicators, and more.

## Features

- Real-time economic data visualization
- Multiple categories: Consumption, Supply, Interest Rate, and Market metrics
- Interactive plots with dual-axis showing both level and year-over-year growth
- Customizable time ranges (1 Year, 2 Years, 5 Years)
- Data from reliable sources (FRED, Yahoo Finance)

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Local Development

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <repository-name>
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
FRED_API_KEY=your_fred_api_key_here
```

5. Run the application:
```bash
streamlit run app.py
```

## Deployment on Streamlit Cloud

1. Push your code to GitHub
2. Visit [Streamlit Cloud](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository, branch, and `app.py` file
6. Add your FRED API key in the Streamlit Cloud secrets management:
   - Go to ⚙️ (Advanced settings)
   - Add your FRED API key under "Secrets":
   ```toml
   FRED_API_KEY = "your_fred_api_key_here"
   ```
7. Deploy! 