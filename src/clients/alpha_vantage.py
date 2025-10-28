import os
import requests
import json
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

load_dotenv()

ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")

def get_recent_stock_data(tickers: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Fetches recent daily stock data for a list of tickers from Alpha Vantage.

    Args:
        tickers: A list of stock ticker symbols (e.g., ["MSFT", "AAPL"]).

    Returns:
        A dictionary where each key is a ticker symbol.
        The value is a dictionary containing either:
        - "data": A list of the 5 most recent trading days' data.
        - "error": A string describing what went wrong.
    """
    
    if not ALPHA_VANTAGE_API_KEY:
        print("Error: ALPHA_VANTAGE_API_KEY not found in environment.")
        raise ValueError("ALPHA_VANTAGE_API_KEY is not set. Check your .env file.")

    portfolio_data = {}

    for ticker in tickers:
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "outputsize": "compact",  # "compact" gives the latest 100 data points
            "apikey": ALPHA_VANTAGE_API_KEY,
        }

        try:
            response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params)
            response.raise_for_status() 
            
            data = response.json()

            if "Error Message" in data:
                print(f"API Error for {ticker}: {data['Error Message']}")
                portfolio_data[ticker] = {"error": data["Error Message"]}
                continue # Go to the next ticker

            if "Note" in data:
                print(f"API Note for {ticker}: {data['Note']}")
                portfolio_data[ticker] = {"error": data["Note"]}
                continue

            time_series = data.get("Time Series (Daily)")
            if not time_series:
                print(f"No 'Time Series (Daily)' data found for {ticker}")
                portfolio_data[ticker] = {"error": "No time series data found."}
                continue

            recent_data = []
            for date in list(time_series.keys())[:5]:
                day_data = time_series[date]

                cleaned_day_data = {
                    "date": date,
                    "open": day_data.get("1. open"),
                    "high": day_data.get("2. high"),
                    "low": day_data.get("3. low"),
                    "close": day_data.get("4. close"),
                    "volume": day_data.get("5. volume"),
                }
                recent_data.append(cleaned_day_data)

            portfolio_data[ticker] = {"data": recent_data}
        except requests.exceptions.HTTPError as http_err:
            # Handle HTTP errors (e.g., 404, 503)
            print(f"HTTP error occurred for {ticker}: {http_err}")
            portfolio_data[ticker] = {"error": f"HTTP Error: {http_err}"}
        
        except requests.exceptions.RequestException as req_err:
            # Handle other network errors (e.g., connection refused)
            print(f"Network error occurred for {ticker}: {req_err}")
            portfolio_data[ticker] = {"error": f"Network Error: {req_err}"}
        
        except Exception as e:
            # Catch any other unexpected errors (e.g., bad JSON)
            print(f"An unexpected error occurred for {ticker}: {e}")
            portfolio_data[ticker] = {"error": f"An unexpected error: {e}"}
    return portfolio_data


if __name__ == "__main__":
    print("--- Testing Alpha Vantage Client ---")

    test_tickers = ["MSFT", "GOOGL", "TESTTICKER"]
    
    data = get_recent_stock_data(test_tickers)

    print(json.dumps(data, indent=2))