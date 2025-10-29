import json
from typing import List, Dict, Any

from clients.alpha_vantage import get_recent_stock_data
from clients.llm_service import get_llm_analysis
from clients.prompt import PORTFOLIO_ANALYSIS_PROMPT_UPDATED

def get_portfolio_analysis(tickers: List[str]) -> Dict[str, Any]:
    """
    Orchestrates the full portfolio analysis workflow.

    Args:
        tickers: A list of stock ticker symbols.

    Returns:
        A dictionary containing the analysis or an error.
    """
    print(f"--- Starting analysis for: {tickers} ---")

    # --- Step 1: Get data from Alpha Vantage ---
    print("Fetching data from Alpha Vantage...")
    try:
        stock_data = get_recent_stock_data(tickers)
    except Exception as e:
        print(f"Critical error in Alpha Vantage client: {e}")
        return {"error": f"Failed to fetch data from Alpha Vantage: {e}"}

    # --- Step 2: Handle API errors ---
    # Check if all tickers returned an error
    all_errors = True
    for ticker, result in stock_data.items():
        if "data" in result:
            all_errors = False
            break
            
    if all_errors:
        print("All tickers returned errors. Returning raw error data.")
        return {
            "analysis": "Could not perform analysis. All tickers returned errors.",
            "raw_data": stock_data
        }

    # --- Step 3: Format the prompt ---
    print("Formatting prompt for LLM...")
    try:
        # Convert the tickers list and data dict to clean strings
        tickers_str = ", ".join(tickers)
        json_data = json.dumps(stock_data, indent=2)

        # Fill in the placeholders in our prompt template
        formatted_prompt = PORTFOLIO_ANALYSIS_PROMPT_UPDATED.format(
            tickers_str=tickers_str,
            json_data=json_data
        )
    except Exception as e:
        print(f"Error formatting prompt: {e}")
        return {"error": f"Failed to format prompt: {e}"}

    # --- Step 4: Get analysis from LLM ---
    print("Getting analysis from LLM service...")
    # This function also handles W&B logging
    analysis_text = get_llm_analysis(
        prompt=formatted_prompt, 
        financial_data=stock_data
    )

    # --- Step 5: Return the final result ---
    print("--- Analysis complete ---")
    return {
        "analysis": analysis_text,
        "raw_data": stock_data
    }


if __name__ == "__main__":
    print("--- Testing Orchestration Service ---")
    
    test_tickers = ["AMD", "AMZN", "MSFT"]
    
    analysis_result = get_portfolio_analysis(test_tickers)
    
    print("\n--- Service Result ---")
    print(json.dumps(analysis_result, indent=2))
