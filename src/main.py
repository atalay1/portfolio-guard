from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
from service import get_portfolio_analysis

app = FastAPI(
    title="Portfolio Analyzer AI",
    description="An API that uses Alpha Vantage and an LLM to analyze stock portfolios.",
    version="1.0.0"
)

# 2. Define the request model
# This tells FastAPI what the incoming JSON request body should look like
class PortfolioRequest(BaseModel):
    tickers: List[str]
    
    # Example to show in the API docs
    class Config:
        json_schema_extra = {
            "example": {
                "tickers": ["IBM", "MSFT", "GOOG"]
            }
        }

# 3. Define a root endpoint (for health checks)
@app.get("/")
def read_root():
    """A simple endpoint to check if the API is live."""
    return {"status": "Portfolio Analyzer API is running!"}

# 4. Define the main analysis endpoint
@app.post("/analyze", response_model=Dict[str, Any])
async def analyze_portfolio(request: PortfolioRequest):
    """
    Analyzes a portfolio of stock tickers.
    
    This endpoint:
    1. Fetches recent price data from Alpha Vantage.
    2. Sends the data to an LLM for analysis.
    3. Logs the interaction to W&B.
    4. Returns the analysis as JSON.
    """
    if not request.tickers:
        raise HTTPException(status_code=400, detail="Tickers list cannot be empty.")

    try:
        analysis_result = get_portfolio_analysis(request.tickers)
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

# 5. Make the app runnable with Uvicorn
if __name__ == "__main__":
    """
    Recommended way to use:
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    """
    uvicorn.run(app, host="0.0.0.0", port=8000)
