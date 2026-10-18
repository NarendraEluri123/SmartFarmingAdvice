"""
IBM Watsonx Configuration for Smart Farming Advice System
Using IBM Granite 4 H Small via IBM watsonx.ai
"""
import os

# IBM Watsonx credentials
IBM_API_KEY = os.getenv("IBM_API_KEY", "L3BISep_aIDl9yk8j0Z060VqGHhCSgBVLtkvb5WAMKkR")
IBM_PROJECT_ID = os.getenv("IBM_PROJECT_ID", "a732d551-9d07-47e7-a957-e1e80082ce52")
IBM_WATSONX_URL = os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

# LLM Model
LLM_MODEL_ID = "ibm/granite-4-h-small"  # IBM Granite 4 H Small

# LLM Generation parameters
LLM_PARAMS = {
    "max_new_tokens": 300,   # keep short for fast responses
    "temperature": 0.3,
    "top_p": 0.9,
    "repetition_penalty": 1.1,
}

# Weather API (OpenWeatherMap free tier)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "demo")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# RAG configuration
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
TOP_K_RETRIEVAL = 1   # single best chunk = minimal context injection

# Agent names
AGENTS = {
    "crop_advisory": "Crop Advisory Agent",
    "weather_irrigation": "Weather & Irrigation Agent",
    "pest_disease": "Pest & Disease Detection Agent",
    "market_insights": "Market Insights Agent",
    "orchestrator": "Smart Farming Orchestrator",
}
