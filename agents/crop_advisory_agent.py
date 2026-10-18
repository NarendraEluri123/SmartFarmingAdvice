"""
Crop Advisory Agent — personalized seed, fertilizer, irrigation schedule,
and harvesting timeline advice based on farmer profile and land conditions.
"""
from __future__ import annotations

from typing import Any

from llm_client import generate_with_system
from rag_system import get_rag

# ─────────────────────────────────────────────────────────────────────────────
# Lookup tables
# ─────────────────────────────────────────────────────────────────────────────

CROP_CALENDAR: dict[str, dict] = {
    "rice": {
        "seasons": ["Kharif (Jun–Oct)", "Rabi (Nov–Mar) in S. India"],
        "sowing_to_harvest_days": {"short": 90, "medium": 115, "long": 140},
        "optimal_temp_c": (20, 35),
        "water_req_mm": 1200,
    },
    "wheat": {
        "seasons": ["Rabi (Oct–Mar)"],
        "sowing_to_harvest_days": {"timely": 120, "late": 110},
        "optimal_temp_c": (10, 25),
        "water_req_mm": 450,
    },
    "maize": {
        "seasons": ["Kharif (Jun–Sep)", "Rabi (Oct–Feb)", "Spring (Jan–May)"],
        "sowing_to_harvest_days": {"hybrid": 90, "composite": 100},
        "optimal_temp_c": (21, 30),
        "water_req_mm": 500,
    },
    "tomato": {
        "seasons": ["Year-round with irrigation; avoid peak summer"],
        "sowing_to_harvest_days": {"indeterminate": 70, "determinate": 65},
        "optimal_temp_c": (20, 27),
        "water_req_mm": 600,
    },
    "potato": {
        "seasons": ["Rabi (Oct–Feb)", "Hills (Mar–Jun)"],
        "sowing_to_harvest_days": {"early": 70, "main": 90},
        "optimal_temp_c": (15, 22),
        "water_req_mm": 500,
    },
    "cotton": {
        "seasons": ["Kharif (Apr–Nov)"],
        "sowing_to_harvest_days": {"hybrid": 180, "bt": 170},
        "optimal_temp_c": (25, 35),
        "water_req_mm": 700,
    },
    "soybean": {
        "seasons": ["Kharif (Jun–Oct)"],
        "sowing_to_harvest_days": {"main": 100},
        "optimal_temp_c": (20, 30),
        "water_req_mm": 450,
    },
    "groundnut": {
        "seasons": ["Kharif (Jun–Oct)", "Rabi (Nov–Mar)"],
        "sowing_to_harvest_days": {"virginia": 130, "bunch": 100},
        "optimal_temp_c": (25, 35),
        "water_req_mm": 500,
    },
}

SOIL_FERTILITY_ADJUSTMENTS: dict[str, dict] = {
    "sandy": {"n_adj": +20, "irrigation_freq": "high", "organic_matter": "critical"},
    "loamy": {"n_adj": 0, "irrigation_freq": "moderate", "organic_matter": "good"},
    "clay": {"n_adj": -10, "irrigation_freq": "low", "organic_matter": "adequate"},
    "silty": {"n_adj": 0, "irrigation_freq": "moderate", "organic_matter": "moderate"},
    "black": {"n_adj": -15, "irrigation_freq": "low", "organic_matter": "naturally high"},
    "red": {"n_adj": +10, "irrigation_freq": "moderate-high", "organic_matter": "low – add compost"},
}

RECOMMENDED_VARIETIES: dict[str, list] = {
    "rice": ["Swarna (MTU 7029)", "BPT 5204", "Samba Mahsuri", "IR64 (drought-tolerant)"],
    "wheat": ["HD 3086", "GW 496", "DBW 187", "HD 2967"],
    "maize": ["DKC 9144", "PEHM 2", "NK 6240", "Pro 4212 (drought-tolerant)"],
    "tomato": ["Arka Vikas", "Pusa Ruby", "Naveen", "Pusa Hybrid-2"],
    "potato": ["Kufri Jyoti", "Kufri Badshah", "Kufri Pukhraj", "Kufri Chipsona-1"],
    "cotton": ["JKCH 1947 (BT)", "MRC 7017 BG II", "NCS 207"],
    "soybean": ["JS 335", "NRC 37", "MACS 450"],
    "groundnut": ["TAG 24", "GG 20", "ICGV 91114 (drought-tolerant)"],
}

FERTILIZER_SCHEDULE: dict[str, dict] = {
    "rice":     {"n": 120, "p": 60,  "k": 60,  "splits": "1/3 basal, 1/3 at 21 DAT, 1/3 at 45 DAT"},
    "wheat":    {"n": 120, "p": 60,  "k": 40,  "splits": "1/3 basal, 1/3 at CRI, 1/3 at flag leaf"},
    "maize":    {"n": 150, "p": 75,  "k": 50,  "splits": "50% basal, 25% at V6, 25% at tasselling"},
    "tomato":   {"n": 120, "p": 60,  "k": 60,  "splits": "20% basal, remaining in 4 splits after transplanting"},
    "potato":   {"n": 150, "p": 100, "k": 100, "splits": "50% basal, 50% at earthing-up"},
    "cotton":   {"n": 120, "p": 60,  "k": 60,  "splits": "1/3 basal, 1/3 squaring, 1/3 boll development"},
    "soybean":  {"n": 20,  "p": 60,  "k": 40,  "splits": "Full basal (Rhizobium inoculation for N fixation)"},
    "groundnut": {"n": 25, "p": 50,  "k": 75,  "splits": "Full basal + gypsum @ 250 kg/ha at pegging"},
}


# ─────────────────────────────────────────────────────────────────────────────
# Agent
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are the Crop Advisory Agent (IBM Granite). Give personalised, concise farming advice: variety selection, land prep, sowing date, fertilizer schedule, irrigation, and harvest timeline. Be brief and practical."""


class CropAdvisoryAgent:
    """Personalized Crop Advisory Agent."""

    def __init__(self):
        self._rag = get_rag()

    def run(self, farmer_profile: dict[str, Any], query: str = "") -> dict[str, Any]:
        """
        Generate personalized crop advisory.

        farmer_profile keys (all optional with defaults):
            name, location, land_area_ha, soil_type, crop, season,
            irrigation_source, budget_inr, objective, previous_crop
        """
        # Extract profile
        name = farmer_profile.get("name", "Farmer")
        location = farmer_profile.get("location", "India")
        land_ha = float(farmer_profile.get("land_area_ha", 1.0))
        soil_type = farmer_profile.get("soil_type", "loamy").lower()
        crop = farmer_profile.get("crop", "wheat").lower()
        season = farmer_profile.get("season", "")
        irrigation = farmer_profile.get("irrigation_source", "canal/tube well")
        budget = farmer_profile.get("budget_inr", "not specified")
        objective = farmer_profile.get("objective", "maximize yield")
        prev_crop = farmer_profile.get("previous_crop", "not specified")

        # Look up tables
        crop_info = CROP_CALENDAR.get(crop, {})
        soil_adj = SOIL_FERTILITY_ADJUSTMENTS.get(soil_type, SOIL_FERTILITY_ADJUSTMENTS["loamy"])
        varieties = RECOMMENDED_VARIETIES.get(crop, ["Consult local KVK for variety recommendations"])
        fert = FERTILIZER_SCHEDULE.get(crop, {"n": 100, "p": 50, "k": 50, "splits": "As per soil test"})

        # Adjust N for soil type
        n_adjusted = fert["n"] + soil_adj["n_adj"]

        # RAG context
        rag_ctx = self._rag.get_context(
            f"{crop} cultivation guidelines {soil_type} soil fertilizer irrigation schedule"
        )

        user_msg = f"""Farmer: {name} | Location: {location} | Land: {land_ha} ha | Soil: {soil_type}
Crop: {crop} | Season: {season or crop_info.get('seasons', ['Year-round'])[0]} | Irrigation: {irrigation} | Budget: ₹{budget}
Previous crop: {prev_crop} | Objective: {objective}
Varieties: {', '.join(varieties[:2])} | N={n_adjusted} P={fert['p']} K={fert['k']} kg/ha | Splits: {fert['splits']}
Context: {rag_ctx[:400]}
Question: {query or "Give complete farming plan."}
Cover: 1) Best variety 2) Land prep 3) Sowing window 4) Fertilizer for {land_ha}ha 5) Irrigation 6) Harvest timeline. Be concise."""
        advice = generate_with_system(SYSTEM_PROMPT, user_msg)

        return {
            "agent": "Crop Advisory Agent",
            "farmer": name,
            "crop": crop,
            "land_ha": land_ha,
            "recommended_varieties": varieties[:3],
            "fertilizer_schedule_kg_ha": {
                "N": n_adjusted, "P": fert["p"], "K": fert["k"],
                "splits": fert["splits"],
            },
            "advice": advice,
        }
