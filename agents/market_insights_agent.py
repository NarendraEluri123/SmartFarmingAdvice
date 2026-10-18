"""
Market Insights Agent — forecasts demand, suggests market prices,
and recommends cost-efficient practices for better farmer income.
"""
from __future__ import annotations

from typing import Any

from llm_client import generate_with_system
from rag_system import get_rag

# ─────────────────────────────────────────────────────────────────────────────
# Static market reference data (2024–25 India indicative values)
# ─────────────────────────────────────────────────────────────────────────────

MSP_DATA: dict[str, dict] = {
    "rice":       {"msp_inr_quintal": 2300, "crop_type": "Kharif"},
    "wheat":      {"msp_inr_quintal": 2275, "crop_type": "Rabi"},
    "maize":      {"msp_inr_quintal": 2090, "crop_type": "Kharif"},
    "soybean":    {"msp_inr_quintal": 4892, "crop_type": "Kharif"},
    "groundnut":  {"msp_inr_quintal": 6783, "crop_type": "Kharif"},
    "cotton":     {"msp_inr_quintal": 7121, "crop_type": "Kharif"},
    "tomato":     {"msp_inr_quintal": None, "crop_type": "Horticulture – market driven"},
    "potato":     {"msp_inr_quintal": None, "crop_type": "Horticulture – market driven"},
    "onion":      {"msp_inr_quintal": None, "crop_type": "Horticulture – market driven"},
    "sugarcane":  {"msp_inr_quintal": 340,  "crop_type": "Annual"},
    "mustard":    {"msp_inr_quintal": 5950, "crop_type": "Rabi"},
    "arhar":      {"msp_inr_quintal": 7550, "crop_type": "Kharif"},
    "gram":       {"msp_inr_quintal": 5440, "crop_type": "Rabi"},
    "moong":      {"msp_inr_quintal": 8682, "crop_type": "Kharif"},
}

TYPICAL_YIELDS_QTL_HA: dict[str, dict] = {
    "rice":      {"low": 20, "medium": 40, "high": 60},
    "wheat":     {"low": 25, "medium": 40, "high": 55},
    "maize":     {"low": 30, "medium": 55, "high": 80},
    "tomato":    {"low": 150, "medium": 300, "high": 500},
    "potato":    {"low": 100, "medium": 200, "high": 300},
    "cotton":    {"low": 10, "medium": 18, "high": 25},
    "soybean":   {"low": 12, "medium": 20, "high": 28},
    "groundnut": {"low": 15, "medium": 25, "high": 35},
    "mustard":   {"low": 10, "medium": 18, "high": 25},
}

INPUT_COST_PER_HA: dict[str, dict] = {
    "rice":      {"seed": 2000,  "fertilizer": 6000,  "pesticide": 3000, "labour": 12000, "irrigation": 5000},
    "wheat":     {"seed": 2500,  "fertilizer": 6000,  "pesticide": 2000, "labour": 8000,  "irrigation": 4000},
    "maize":     {"seed": 3000,  "fertilizer": 7000,  "pesticide": 3000, "labour": 7000,  "irrigation": 3000},
    "tomato":    {"seed": 5000,  "fertilizer": 12000, "pesticide": 8000, "labour": 30000, "irrigation": 8000},
    "potato":    {"seed": 20000, "fertilizer": 15000, "pesticide": 6000, "labour": 20000, "irrigation": 6000},
    "cotton":    {"seed": 3500,  "fertilizer": 8000,  "pesticide": 8000, "labour": 15000, "irrigation": 4000},
    "soybean":   {"seed": 4000,  "fertilizer": 4000,  "pesticide": 3000, "labour": 6000,  "irrigation": 2000},
    "groundnut": {"seed": 8000,  "fertilizer": 5000,  "pesticide": 4000, "labour": 10000, "irrigation": 4000},
}

SEASONAL_PRICE_TREND: dict[str, str] = {
    "rice":      "Prices peak Oct–Nov (post-harvest scarcity). Storing 2–3 months can gain 15–20%.",
    "wheat":     "Prices peak Jul–Sep. Storing until Jul can improve returns by 10–15%.",
    "maize":     "Poultry sector drives demand year-round. Prices dip post-Kharif harvest (Oct).",
    "tomato":    "Highly volatile; peaks Dec–Jan and Apr–May. Off-season growing is highly profitable.",
    "potato":    "Prices peak May–Jun. Cold storage unlocks 20–25% premium.",
    "onion":     "Extremely volatile; prices peak Dec–Apr. Export demand impacts prices significantly.",
    "cotton":    "International prices drive local prices. Prices tend to be better Oct–Dec.",
    "soybean":   "Soy meal exports influence prices. Better prices available Feb–May.",
    "groundnut": "Oil demand steady; prices better Mar–Jun after stocks deplete.",
}

MARKET_CHANNELS: list[dict] = [
    {"channel": "APMC Mandi",      "pros": "Regulated, transparent auction",         "cons": "Commission charges, transport cost"},
    {"channel": "eNAM",            "pros": "Online price discovery, wider buyer base","cons": "Requires internet and quality grading"},
    {"channel": "FPO/Cooperative", "pros": "Aggregated volume, better bargaining",     "cons": "Requires membership and coordination"},
    {"channel": "Direct to Processor", "pros": "Best price, elimination of middlemen", "cons": "Requires quality standards, contracts"},
    {"channel": "Retail/Local market", "pros": "Quick cash, no transport",             "cons": "Lower price, limited volume"},
]


def _calculate_economics(crop: str, land_ha: float, yield_level: str = "medium") -> dict:
    """Calculate gross income, input cost, and net profit."""
    msp = MSP_DATA.get(crop, {}).get("msp_inr_quintal")
    yield_qtl_ha = TYPICAL_YIELDS_QTL_HA.get(crop, {}).get(yield_level, 30)
    costs = INPUT_COST_PER_HA.get(crop, {})

    total_yield_qtl = yield_qtl_ha * land_ha
    total_cost = sum(costs.values()) * land_ha if costs else 50000 * land_ha

    if msp:
        gross_income = total_yield_qtl * msp
    else:
        # Horticulture – use a realistic average market price
        hort_avg = {"tomato": 800, "potato": 600, "onion": 1000}
        avg_price = hort_avg.get(crop, 800)
        gross_income = total_yield_qtl * avg_price

    net_profit = gross_income - total_cost
    roi_pct = (net_profit / total_cost * 100) if total_cost > 0 else 0

    return {
        "land_ha": land_ha,
        "yield_qtl_ha": yield_qtl_ha,
        "total_yield_qtl": round(total_yield_qtl, 1),
        "input_cost_inr": round(total_cost),
        "gross_income_inr": round(gross_income),
        "net_profit_inr": round(net_profit),
        "roi_pct": round(roi_pct, 1),
        "msp_inr_quintal": msp,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Agent
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are the Market Insights Agent (IBM Granite). Give concise advice on market prices, best time to sell, cost-cutting tips, and relevant government schemes. Focus on maximising farmer income. Be brief."""


class MarketInsightsAgent:
    """Market & Cost Optimization Agent."""

    def __init__(self):
        self._rag = get_rag()

    def run(
        self,
        crop: str,
        land_ha: float = 1.0,
        location: str = "",
        yield_level: str = "medium",
        query: str = "",
    ) -> dict[str, Any]:
        """
        Generate market analysis and cost optimization advice.
        """
        crop_lower = crop.lower()

        # Compute economics
        economics = _calculate_economics(crop_lower, land_ha, yield_level)
        msp_info = MSP_DATA.get(crop_lower, {})
        price_trend = SEASONAL_PRICE_TREND.get(crop_lower, "Consult local APMC for price trends.")

        # RAG context
        rag_ctx = self._rag.get_context(
            f"market price {crop} income optimization government scheme FPO"
        )

        channels_text = "\n".join(
            f"  • {c['channel']}: Pros – {c['pros']} | Cons – {c['cons']}"
            for c in MARKET_CHANNELS
        )

        user_msg = f"""Crop: {crop} | Land: {land_ha} ha | Location: {location or "India"}
MSP: ₹{msp_info.get('msp_inr_quintal','N/A')}/qtl | Yield: {economics['total_yield_qtl']} qtl | Cost: ₹{economics['input_cost_inr']:,} | Profit: ₹{economics['net_profit_inr']:,} (ROI {economics['roi_pct']}%)
Price trend: {price_trend}
Context: {rag_ctx[:300]}
Question: {query or "Give market and cost optimization advice."}
Cover: 1) Price outlook 2) When/where to sell 3) Top 3 cost cuts 4) Govt schemes. Be concise."""
        advice = generate_with_system(SYSTEM_PROMPT, user_msg)

        return {
            "agent": "Market Insights Agent",
            "crop": crop,
            "land_ha": land_ha,
            "economics": economics,
            "msp_inr_quintal": msp_info.get("msp_inr_quintal"),
            "price_trend": price_trend,
            "advice": advice,
        }
