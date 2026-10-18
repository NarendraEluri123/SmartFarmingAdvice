"""
Weather & Irrigation Agent
Fetches real-time weather data and provides irrigation & soil advice.
"""
from __future__ import annotations

import json
import math
from typing import Any

import requests

from config import OPENWEATHER_API_KEY, OPENWEATHER_BASE_URL
from llm_client import generate_with_system
from rag_system import get_rag

# ─────────────────────────────────────────────────────────────────────────────
# Weather data helpers
# ─────────────────────────────────────────────────────────────────────────────

def _fetch_weather(location: str) -> dict[str, Any]:
    """
    Fetch current weather from OpenWeatherMap.
    Returns a dict with temperature, humidity, wind, description, etc.
    Falls back to simulated data when the API key is 'demo' or the call fails.
    """
    if OPENWEATHER_API_KEY == "demo":
        return _simulated_weather(location)

    try:
        url = f"{OPENWEATHER_BASE_URL}/weather"
        params = {"q": location, "appid": OPENWEATHER_API_KEY, "units": "metric"}
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        return {
            "location": data.get("name", location),
            "temperature_c": data["main"]["temp"],
            "feels_like_c": data["main"]["feels_like"],
            "humidity_pct": data["main"]["humidity"],
            "wind_speed_ms": data["wind"]["speed"],
            "description": data["weather"][0]["description"].title(),
            "rain_1h_mm": data.get("rain", {}).get("1h", 0),
            "source": "OpenWeatherMap",
        }
    except Exception as exc:
        return _simulated_weather(location, note=str(exc))


def _fetch_forecast(location: str) -> list[dict]:
    """Fetch 5-day/3-hour forecast, summarised to daily."""
    if OPENWEATHER_API_KEY == "demo":
        return _simulated_forecast()

    try:
        url = f"{OPENWEATHER_BASE_URL}/forecast"
        params = {"q": location, "appid": OPENWEATHER_API_KEY, "units": "metric", "cnt": 40}
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()

        daily: dict[str, dict] = {}
        for item in data["list"]:
            date = item["dt_txt"].split()[0]
            if date not in daily:
                daily[date] = {"temps": [], "humidity": [], "rain": 0, "desc": []}
            daily[date]["temps"].append(item["main"]["temp"])
            daily[date]["humidity"].append(item["main"]["humidity"])
            daily[date]["rain"] += item.get("rain", {}).get("3h", 0)
            daily[date]["desc"].append(item["weather"][0]["description"])

        result = []
        for date, d in list(daily.items())[:5]:
            result.append({
                "date": date,
                "max_temp_c": round(max(d["temps"]), 1),
                "min_temp_c": round(min(d["temps"]), 1),
                "avg_humidity_pct": round(sum(d["humidity"]) / len(d["humidity"]), 1),
                "rain_mm": round(d["rain"], 1),
                "description": max(set(d["desc"]), key=d["desc"].count).title(),
            })
        return result
    except Exception:
        return _simulated_forecast()


def _simulated_weather(location: str, note: str = "") -> dict[str, Any]:
    """Realistic simulated weather for demo purposes."""
    return {
        "location": location,
        "temperature_c": 28.4,
        "feels_like_c": 31.0,
        "humidity_pct": 72,
        "wind_speed_ms": 3.2,
        "description": "Partly Cloudy",
        "rain_1h_mm": 0,
        "source": f"Simulated (demo mode{'; ' + note if note else ''})",
    }


def _simulated_forecast() -> list[dict]:
    """5-day simulated forecast."""
    return [
        {"date": "Day 1", "max_temp_c": 30, "min_temp_c": 22, "avg_humidity_pct": 70, "rain_mm": 0, "description": "Sunny"},
        {"date": "Day 2", "max_temp_c": 29, "min_temp_c": 21, "avg_humidity_pct": 75, "rain_mm": 2.5, "description": "Partly Cloudy"},
        {"date": "Day 3", "max_temp_c": 26, "min_temp_c": 20, "avg_humidity_pct": 85, "rain_mm": 12.0, "description": "Thunderstorms"},
        {"date": "Day 4", "max_temp_c": 24, "min_temp_c": 19, "avg_humidity_pct": 80, "rain_mm": 5.0, "description": "Light Rain"},
        {"date": "Day 5", "max_temp_c": 28, "min_temp_c": 21, "avg_humidity_pct": 68, "rain_mm": 0, "description": "Clear"},
    ]


# ─────────────────────────────────────────────────────────────────────────────
# ET₀ / Irrigation calculation helpers (Hargreaves method)
# ─────────────────────────────────────────────────────────────────────────────

def _estimate_et0(temp_max: float, temp_min: float, ra_mm_day: float = 8.0) -> float:
    """Hargreaves–Samani ET₀ estimate (mm/day)."""
    temp_mean = (temp_max + temp_min) / 2.0
    return 0.0023 * (temp_mean + 17.8) * math.sqrt(max(temp_max - temp_min, 0)) * ra_mm_day


CROP_KC: dict[str, float] = {
    "rice": 1.2, "wheat": 1.0, "maize": 1.05, "tomato": 1.15,
    "potato": 1.1, "cotton": 1.15, "soybean": 1.0, "groundnut": 1.05,
    "default": 1.0,
}


def _irrigation_need(et0: float, kc: float, rain_mm: float) -> float:
    """Net irrigation need (mm/day). Returns 0 if rain covers demand."""
    etc = et0 * kc
    return max(0.0, etc - rain_mm)


# ─────────────────────────────────────────────────────────────────────────────
# Agent class
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are the Weather & Irrigation Agent (IBM Granite). Analyse weather data, calculate irrigation needs, warn about risks, and give concise actionable advice. Be brief and practical."""


class WeatherIrrigationAgent:
    """Weather & Irrigation Agent."""

    def __init__(self):
        self._rag = get_rag()

    def run(
        self,
        location: str,
        crop: str = "wheat",
        soil_type: str = "loamy",
        farmer_query: str = "",
    ) -> dict[str, Any]:
        """
        Main entry point.  Returns a dict with weather data, forecast,
        irrigation recommendation, and LLM advisory text.
        """
        weather = _fetch_weather(location)
        forecast = _fetch_forecast(location)

        # Irrigation estimate from forecast day 1
        f1 = forecast[0] if forecast else {}
        et0 = _estimate_et0(
            f1.get("max_temp_c", weather["temperature_c"] + 3),
            f1.get("min_temp_c", weather["temperature_c"] - 3),
        )
        kc = CROP_KC.get(crop.lower(), CROP_KC["default"])
        rain = f1.get("rain_mm", 0)
        irr_need = _irrigation_need(et0, kc, rain)

        # RAG context
        rag_ctx = self._rag.get_context(
            f"irrigation {soil_type} soil {crop} crop water management"
        )

        # Build prompt
        weather_summary = json.dumps(weather, indent=2)
        forecast_summary = json.dumps(forecast[:3], indent=2)

        user_msg = f"""Location: {location} | Crop: {crop} | Soil: {soil_type}
Weather: {weather['description']}, {weather['temperature_c']}°C, Humidity {weather['humidity_pct']}%
ET₀: {et0:.1f} mm/day | ETc: {et0*kc:.1f} mm/day | Rain tomorrow: {rain:.1f} mm | Net irrigation needed: {irr_need:.1f} mm/day
Forecast summary: {forecast_summary}
Context: {rag_ctx[:400]}
Question: {farmer_query or "Give irrigation advice for next 3 days."}
Provide: 1) Weather summary 2) Irrigation plan 3) Warnings 4) Key farm activities. Be concise."""
        advice = generate_with_system(SYSTEM_PROMPT, user_msg)

        return {
            "agent": "Weather & Irrigation Agent",
            "location": location,
            "crop": crop,
            "weather": weather,
            "forecast": forecast,
            "irrigation_need_mm_day": round(irr_need, 2),
            "et0_mm_day": round(et0, 2),
            "advice": advice,
        }
