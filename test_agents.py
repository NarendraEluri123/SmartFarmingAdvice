"""
CLI test script — validates all agents without the Streamlit UI.
Run: python test_agents.py
"""
from __future__ import annotations

import json
import sys


def print_section(title: str, width: int = 70):
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def print_result(result: dict, key: str = "advice", max_chars: int = 500):
    advice = result.get(key, "")
    print(advice[:max_chars] + ("…" if len(advice) > max_chars else ""))


def test_rag():
    print_section("1. RAG Knowledge Retrieval")
    from rag_system import get_rag
    rag = get_rag()
    results = rag.retrieve("fertilizer schedule for wheat crop", top_k=2)
    for i, (chunk, score) in enumerate(results, 1):
        print(f"\n[Result {i}] Score: {score:.3f}")
        print(chunk[:300] + "…")
    print("\n✅ RAG system OK")


def test_llm():
    print_section("2. IBM Granite LLM Connection")
    from llm_client import get_llm_model, generate_text
    model = get_llm_model()
    response = generate_text("In one sentence, what is the best crop for Punjab in winter?", model)
    print(f"LLM Response: {response[:200]}")
    print("\n✅ IBM Granite LLM OK")


def test_weather_agent():
    print_section("3. Weather & Irrigation Agent")
    from agents.weather_irrigation_agent import WeatherIrrigationAgent
    agent = WeatherIrrigationAgent()
    result = agent.run(
        location="Ludhiana",
        crop="wheat",
        soil_type="loamy",
        farmer_query="Should I irrigate my wheat today?",
    )
    print(f"Location: {result['location']}")
    print(f"Weather: {result['weather']['description']}, {result['weather']['temperature_c']}°C")
    print(f"Irrigation need: {result['irrigation_need_mm_day']} mm/day")
    print_result(result)
    print("\n✅ Weather & Irrigation Agent OK")


def test_pest_agent():
    print_section("4. Pest & Disease Detection Agent")
    from agents.pest_disease_agent import PestDiseaseAgent
    agent = PestDiseaseAgent()
    result = agent.run(
        crop="tomato",
        symptoms="Yellow spots on leaves, leaves curling, small white insects under leaves",
        location="Karnataka",
    )
    print(f"Symptom matches: {len(result['symptom_matches'])}")
    for m in result["symptom_matches"]:
        print(f"  • {m['symptom']}: {', '.join(m['possible_causes'][:2])}")
    print_result(result)
    print("\n✅ Pest & Disease Agent OK")


def test_crop_agent():
    print_section("5. Crop Advisory Agent")
    from agents.crop_advisory_agent import CropAdvisoryAgent
    agent = CropAdvisoryAgent()
    result = agent.run(
        farmer_profile={
            "name": "Suresh Patel",
            "location": "Nashik, Maharashtra",
            "land_area_ha": 1.5,
            "soil_type": "black",
            "crop": "tomato",
            "season": "Rabi",
            "irrigation_source": "drip irrigation",
            "budget_inr": 40000,
            "objective": "maximize yield",
            "previous_crop": "onion",
        },
        query="What variety should I plant and when?",
    )
    print(f"Crop: {result['crop']}, Farmer: {result['farmer']}")
    print(f"Varieties: {', '.join(result['recommended_varieties'])}")
    fert = result["fertilizer_schedule_kg_ha"]
    print(f"Fertilizer: N={fert['N']} P={fert['P']} K={fert['K']} kg/ha")
    print_result(result)
    print("\n✅ Crop Advisory Agent OK")


def test_market_agent():
    print_section("6. Market Insights Agent")
    from agents.market_insights_agent import MarketInsightsAgent
    agent = MarketInsightsAgent()
    result = agent.run(
        crop="wheat",
        land_ha=2.0,
        location="Ludhiana, Punjab",
        yield_level="medium",
        query="When is the best time to sell wheat for maximum profit?",
    )
    econ = result["economics"]
    print(f"MSP: ₹{result['msp_inr_quintal']}/quintal")
    print(f"Expected yield: {econ['total_yield_qtl']} quintals")
    print(f"Input cost: ₹{econ['input_cost_inr']:,}")
    print(f"Net profit: ₹{econ['net_profit_inr']:,} (ROI: {econ['roi_pct']}%)")
    print_result(result)
    print("\n✅ Market Insights Agent OK")


def test_orchestrator():
    print_section("7. Multi-Agent Orchestrator (Full Pipeline)")
    from orchestrator import SmartFarmingOrchestrator
    orch = SmartFarmingOrchestrator()
    result = orch.ask(
        query="My wheat is yellowing and I'm worried about irrigation. When should I sell?",
        farmer_profile={
            "name": "Ramesh Singh",
            "location": "Haryana",
            "land_area_ha": 3.0,
            "soil_type": "loamy",
            "crop": "wheat",
            "season": "Rabi",
        },
    )
    print(f"Intents detected: {result['intents_detected']}")
    print(f"Agents invoked: {list(result['agent_outputs'].keys())}")
    print("\n--- SYNTHESIS (first 600 chars) ---")
    print(result["synthesis"][:600] + "…")
    print("\n✅ Orchestrator OK")


if __name__ == "__main__":
    tests = [
        ("rag", test_rag),
        ("llm", test_llm),
        ("weather", test_weather_agent),
        ("pest", test_pest_agent),
        ("crop", test_crop_agent),
        ("market", test_market_agent),
        ("orchestrator", test_orchestrator),
    ]

    run_only = sys.argv[1] if len(sys.argv) > 1 else None
    passed = failed = 0

    for name, fn in tests:
        if run_only and name != run_only:
            continue
        try:
            fn()
            passed += 1
        except Exception as e:
            import traceback
            print(f"\n❌ FAILED — {name}: {e}")
            traceback.print_exc()
            failed += 1

    print_section(f"RESULTS: {passed} passed, {failed} failed")
    sys.exit(failed)
