"""
Smart Farming Orchestrator — routes farmer queries to the appropriate
specialist agent(s) and assembles a unified response.
"""
from __future__ import annotations

import re
from typing import Any

from llm_client import get_llm_model, generate_with_system
from rag_system import get_rag
from agents.crop_advisory_agent import CropAdvisoryAgent
from agents.weather_irrigation_agent import WeatherIrrigationAgent
from agents.pest_disease_agent import PestDiseaseAgent
from agents.market_insights_agent import MarketInsightsAgent

# ─────────────────────────────────────────────────────────────────────────────
# Intent classifier
# ─────────────────────────────────────────────────────────────────────────────

INTENT_KEYWORDS: dict[str, list[str]] = {
    "weather": ["weather", "rain", "temperature", "forecast", "drought", "flood",
                "irrigation", "water", "humidity", "wind", "storm", "frost"],
    "pest":    ["pest", "disease", "insect", "fungus", "blight", "wilt", "rot",
                "mold", "mildew", "rust", "virus", "bacteria", "aphid", "worm",
                "caterpillar", "spot", "yellowing", "dying", "damaged"],
    "market":  ["price", "market", "sell", "income", "profit", "msp", "mandi",
                "cost", "expense", "revenue", "trade", "export", "demand"],
    "crop":    ["crop", "seed", "variety", "plant", "fertilizer", "sow", "harvest",
                "grow", "yield", "soil", "land", "farm", "agriculture", "advice",
                "recommend", "schedule", "plan", "when", "how"],
}


def _classify_intent(query: str) -> list[str]:
    """Return list of relevant agent intents for the query."""
    query_lower = query.lower()
    intents = []
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in query_lower for kw in keywords):
            intents.append(intent)
    # Default to crop advisory if nothing matched
    if not intents:
        intents = ["crop"]
    return intents


def _extract_crop(text: str) -> str:
    """Best-effort crop name extraction from free text."""
    crops = ["rice", "wheat", "maize", "tomato", "potato", "cotton",
             "soybean", "groundnut", "onion", "mustard", "arhar", "gram"]
    text_lower = text.lower()
    for crop in crops:
        if crop in text_lower:
            return crop
    return "wheat"  # sensible default


def _extract_location(text: str) -> str:
    """Best-effort location extraction (looks for capitalised words)."""
    # Simple heuristic: return last capitalised word or phrase
    matches = re.findall(r"\b[A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)?\b", text)
    # Filter out common non-place words
    skip = {"I", "My", "The", "This", "Please", "Can", "What", "How", "When",
            "Any", "Give", "Tell", "Provide", "Help", "For", "With"}
    places = [m for m in matches if m not in skip]
    return places[-1] if places else "Punjab, India"


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are the Smart Farming Orchestrator (IBM Granite). Briefly synthesise the specialist agent outputs below into a single, clear farmer advisory. End with **Top 3 Actions for Today**. Be concise."""


class SmartFarmingOrchestrator:
    """
    Master orchestrator that routes to and coordinates all specialist agents.
    """

    def __init__(self):
        self._rag = get_rag()
        # Lazy-initialise agents on first use
        self._crop_agent: CropAdvisoryAgent | None = None
        self._weather_agent: WeatherIrrigationAgent | None = None
        self._pest_agent: PestDiseaseAgent | None = None
        self._market_agent: MarketInsightsAgent | None = None

    # ── Lazy agent accessors ─────────────────────────────────────────────────

    @property
    def crop_agent(self) -> CropAdvisoryAgent:
        if self._crop_agent is None:
            self._crop_agent = CropAdvisoryAgent()
        return self._crop_agent

    @property
    def weather_agent(self) -> WeatherIrrigationAgent:
        if self._weather_agent is None:
            self._weather_agent = WeatherIrrigationAgent()
        return self._weather_agent

    @property
    def pest_agent(self) -> PestDiseaseAgent:
        if self._pest_agent is None:
            self._pest_agent = PestDiseaseAgent()
        return self._pest_agent

    @property
    def market_agent(self) -> MarketInsightsAgent:
        if self._market_agent is None:
            self._market_agent = MarketInsightsAgent()
        return self._market_agent

    # ── Public API ───────────────────────────────────────────────────────────

    def ask(
        self,
        query: str,
        farmer_profile: dict[str, Any] | None = None,
        image_bytes: bytes | None = None,
    ) -> dict[str, Any]:
        """
        Main entry point.  Route query to relevant agents and synthesize response.

        Parameters
        ----------
        query : str
            The farmer's question or request.
        farmer_profile : dict, optional
            Keys: name, location, land_area_ha, soil_type, crop, season,
                  irrigation_source, budget_inr, objective, previous_crop
        image_bytes : bytes, optional
            Raw image bytes for pest/disease detection.

        Returns
        -------
        dict with keys: query, intents, agent_outputs, synthesis, top_actions
        """
        if farmer_profile is None:
            farmer_profile = {}

        # Fill defaults from query
        crop = farmer_profile.get("crop") or _extract_crop(query)
        location = farmer_profile.get("location") or _extract_location(query)
        land_ha = float(farmer_profile.get("land_area_ha", 1.0))

        farmer_profile.setdefault("crop", crop)
        farmer_profile.setdefault("location", location)
        farmer_profile.setdefault("land_area_ha", land_ha)

        intents = _classify_intent(query)

        agent_outputs: dict[str, Any] = {}

        # ── Run relevant agents ──────────────────────────────────────────────
        if "weather" in intents:
            agent_outputs["weather"] = self.weather_agent.run(
                location=location,
                crop=crop,
                soil_type=farmer_profile.get("soil_type", "loamy"),
                farmer_query=query,
            )

        if "pest" in intents or image_bytes is not None:
            agent_outputs["pest"] = self.pest_agent.run(
                crop=crop,
                symptoms=query if "pest" in intents else "",
                image_bytes=image_bytes,
                location=location,
            )

        if "market" in intents:
            agent_outputs["market"] = self.market_agent.run(
                crop=crop,
                land_ha=land_ha,
                location=location,
                query=query,
            )

        if "crop" in intents or not agent_outputs:
            agent_outputs["crop"] = self.crop_agent.run(
                farmer_profile=farmer_profile,
                query=query,
            )

        # ── Synthesize all agent outputs ─────────────────────────────────────
        synthesis_input = self._build_synthesis_input(query, agent_outputs, farmer_profile)
        synthesis = generate_with_system(SYSTEM_PROMPT, synthesis_input)

        return {
            "query": query,
            "farmer_profile": farmer_profile,
            "intents_detected": intents,
            "agent_outputs": agent_outputs,
            "synthesis": synthesis,
        }

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _build_synthesis_input(
        self,
        query: str,
        outputs: dict[str, Any],
        profile: dict[str, Any],
    ) -> str:
        parts = [f"Query: {query} | Crop: {profile.get('crop')} | Location: {profile.get('location')}"]
        for agent_key, result in outputs.items():
            advice = result.get("advice", "")
            if advice:
                parts.append(f"[{result.get('agent', agent_key)}]: {advice[:300]}…")
        parts.append("Summarise the above into a unified advisory and list Top 3 Actions for Today.")
        return "\n".join(parts)

    # ── Convenience single-agent calls (for direct UI panels) ─────────────────

    def get_weather_advice(self, location: str, crop: str, soil_type: str = "loamy", query: str = "") -> dict:
        return self.weather_agent.run(location, crop, soil_type, query)

    def get_pest_advice(self, crop: str, symptoms: str, image_bytes: bytes | None = None, location: str = "") -> dict:
        return self.pest_agent.run(crop, symptoms, image_bytes, location=location)

    def get_crop_advice(self, farmer_profile: dict, query: str = "") -> dict:
        return self.crop_agent.run(farmer_profile, query)

    def get_market_advice(self, crop: str, land_ha: float, location: str = "", query: str = "") -> dict:
        return self.market_agent.run(crop, land_ha, location, query=query)
