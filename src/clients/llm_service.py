import os
import google.generativeai as genai
import wandb
import json
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WANDB_API_KEY = os.environ.get("WANDB_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Check your .env file.")
if not WANDB_API_KEY:
     raise ValueError("WANDB_API_KEY is not set. Check your .env file.")

genai.configure(api_key=GEMINI_API_KEY)
wandb.login(key=WANDB_API_KEY)

run = wandb.init(project="llm_portfolio_analyzer", job_type="llm_analysis")

def get_llm_analysis(prompt: str, financial_data: Dict[str, Any]) -> str:
    """
    Sends data and a prompt to the LLM and logs the interaction to W&B.

    Args:
        prompt: The fully formatted prompt string.
        financial_data: The raw data dict from Alpha Vantage (for logging).

    Returns:
        The text analysis from the LLM, or an error message.
    """
    print("Sending prompt to LLM...")
    
    try:
        # --- Call the Gemini API ---
        model = genai.GenerativeModel('gemini-2.5-flash-preview-09-2025')
        response = model.generate_content(prompt)
        
        analysis_text = response.text

        # --- W&B Logging (The "MLOps" part) ---
        print("Logging interaction to Weights & Biases...")
        
        # Create a W&B Table to log the interaction
        # This gives you a structured way to review prompts and responses later
        trace_table = wandb.Table(columns=["prompt", "financial_data_json", "llm_response"])
        trace_table.add_data(
            prompt, 
            json.dumps(financial_data, indent=2), # Log data as a JSON string
            analysis_text
        )
        
        # Log the table to your W&B run
        wandb.log({"llm_trace": trace_table})

        print("Successfully logged to W&B.")

        return analysis_text

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # Also log the failure to W&B
        wandb.log({"error": str(e), "failed_prompt": prompt})
        return f"Error: Could not get analysis from LLM. {e}"


if __name__ == "__main__":
    print("--- Testing LLM Service Client ---")
    
    # 1. Import the prompt we created
    from prompt import PORTFOLIO_ANALYSIS_PROMPT
    
    # 2. Create some MOCK data (so we don't have to call Alpha Vantage)
    mock_tickers = ["MOCK", "TICKR"]
    mock_data = {
        "MOCK": {
            "data": [
                {"date": "2025-10-28", "open": "150.00", "close": "152.00", "volume": "10000"},
                {"date": "2025-10-27", "open": "148.00", "close": "150.00", "volume": "12000"}
            ]
        },
        "TICKR": {
             "data": [
                {"date": "2025-10-28", "open": "300.00", "close": "298.00", "volume": "5000"},
                {"date": "2025-10-27", "open": "301.00", "close": "300.00", "volume": "6000"}
            ]
        }
    }
    
    # 3. Format the prompt
    formatted_prompt = PORTFOLIO_ANALYSIS_PROMPT.format(
        tickers_str=", ".join(mock_tickers),
        json_data=json.dumps(mock_data, indent=2)
    )
    
    # 4. Call the function
    analysis = get_llm_analysis(formatted_prompt, mock_data)
    
    print("\n--- LLM Analysis Result ---")
    print(analysis)
    
    # 5. Finish the W&B run
    # (In a real app, this happens when the app shuts down)
    run.finish()
    print("\nTest complete. Check your W&B project 'llm_portfolio_analyzer'!")