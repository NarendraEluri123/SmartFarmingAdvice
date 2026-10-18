"""
Smart Farming Advice — Streamlit Web Application
Powered by IBM Granite 4 H Small via IBM watsonx.ai
"""
from __future__ import annotations

import io
import traceback
from typing import Any

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# ─────────────────────────────────────────────────────────────────────────────
# Page config (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Farming Advisor",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a6b2e 0%, #2d8a48 50%, #3dab5e 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 { font-size: 2.2rem; margin: 0; }
    .main-header p  { font-size: 1rem; margin: 0.3rem 0 0; opacity: 0.9; }

    .agent-card {
        background: #f8fdf9;
        border: 1px solid #c3e6cb;
        border-left: 4px solid #28a745;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }
    .agent-card h4 { color: #1a6b2e; margin: 0 0 0.4rem; }

    .metric-box {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 0.8rem;
        text-align: center;
    }
    .metric-box .value { font-size: 1.5rem; font-weight: 700; color: #166534; }
    .metric-box .label { font-size: 0.8rem; color: #6b7280; }

    .ibm-badge {
        background: #0f62fe;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .warning-box {
        background: #fffbeb;
        border: 1px solid #fbbf24;
        border-left: 4px solid #f59e0b;
        border-radius: 6px;
        padding: 0.8rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🌾 Smart Farming Advisor</h1>
    <p>AI-Powered Agricultural Intelligence &nbsp;|&nbsp;
       <span class="ibm-badge">IBM Granite 4 H Small</span> &nbsp;
       <span class="ibm-badge">IBM watsonx.ai</span>
    </p>
</div>
""", unsafe_allow_html=True)

st.info("⏱ **IBM Free Plan Note:** Each AI response takes ~30–60 seconds (IBM Granite free-tier rate limit). "
        "The system auto-retries up to 3 times. All data panels (weather, financials) load instantly.", icon="ℹ️")


# ─────────────────────────────────────────────────────────────────────────────
# Session state initialisation
# ─────────────────────────────────────────────────────────────────────────────
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "initialized" not in st.session_state:
    st.session_state.initialized = False


# ─────────────────────────────────────────────────────────────────────────────
# Lazy orchestrator loader
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Initialising AI agents…")
def load_orchestrator():
    from orchestrator import SmartFarmingOrchestrator
    return SmartFarmingOrchestrator()


def get_orchestrator():
    if st.session_state.orchestrator is None:
        st.session_state.orchestrator = load_orchestrator()
    return st.session_state.orchestrator


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar — Farmer Profile
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 👨‍🌾 Farmer Profile")

    farmer_name = st.text_input("Your Name", value="Rajesh Kumar")
    location = st.text_input("Location / Village", value="Ludhiana, Punjab")
    land_ha = st.number_input("Land Area (hectares)", min_value=0.1, max_value=500.0, value=2.0, step=0.5)

    crop = st.selectbox(
        "Primary Crop",
        ["wheat", "rice", "maize", "tomato", "potato", "cotton", "soybean",
         "groundnut", "mustard", "arhar", "gram", "onion"],
    )

    soil_type = st.selectbox(
        "Soil Type",
        ["loamy", "sandy", "clay", "silty", "black", "red"],
    )

    season = st.selectbox(
        "Current Season",
        ["Rabi (Oct–Mar)", "Kharif (Jun–Oct)", "Zaid (Mar–Jun)", "Year-round"],
    )

    irrigation = st.selectbox(
        "Irrigation Source",
        ["Canal / Tube well", "Drip irrigation", "Sprinkler", "Rainfed", "Borewell"],
    )

    budget = st.number_input("Budget (₹/hectare)", min_value=0, max_value=500000, value=25000, step=5000)
    prev_crop = st.text_input("Previous Crop", value="rice")

    st.markdown("---")
    st.markdown("""
    <small>
    <b>Powered by:</b><br>
    🔵 IBM Granite 4 H Small<br>
    🔵 IBM watsonx.ai<br>
    🔵 RAG + Multi-Agent System
    </small>
    """, unsafe_allow_html=True)

farmer_profile = {
    "name": farmer_name,
    "location": location,
    "land_area_ha": land_ha,
    "soil_type": soil_type,
    "crop": crop,
    "season": season,
    "irrigation_source": irrigation,
    "budget_inr": budget,
    "previous_crop": prev_crop,
}

# ─────────────────────────────────────────────────────────────────────────────
# Main tabs
# ─────────────────────────────────────────────────────────────────────────────
tab_chat, tab_crop, tab_weather, tab_pest, tab_market, tab_rag = st.tabs([
    "💬 Chat Assistant",
    "🌱 Crop Advisory",
    "🌤 Weather & Irrigation",
    "🐛 Pest & Disease",
    "📈 Market Insights",
    "📚 Knowledge Base",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Chat Assistant (orchestrator)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_chat:
    st.subheader("💬 Smart Farming Assistant")
    st.caption("Ask anything about your farm — the system will route your question to the right specialist agents.")

    # Display history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="👨‍🌾" if msg["role"] == "user" else "🌾"):
            st.markdown(msg["content"])

    # Input
    user_input = st.chat_input("Ask your farming question… e.g. 'My wheat leaves are turning yellow, what should I do?'")

    if user_input:
        # Show user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👨‍🌾"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🌾"):
            with st.spinner("🌾 IBM Granite thinking… (free plan: ~30–60s, auto-retrying on rate limits)"):
                try:
                    orch = get_orchestrator()
                    result = orch.ask(query=user_input, farmer_profile=dict(farmer_profile))
                    synthesis = result.get("synthesis", "")

                    st.markdown(synthesis)

                    # Show which agents were invoked
                    agents_used = list(result.get("agent_outputs", {}).keys())
                    if agents_used:
                        agent_labels = {
                            "crop": "🌱 Crop Advisory",
                            "weather": "🌤 Weather & Irrigation",
                            "pest": "🐛 Pest & Disease",
                            "market": "📈 Market Insights",
                        }
                        badges = " · ".join(agent_labels.get(a, a) for a in agents_used)
                        st.caption(f"Agents consulted: {badges}")

                    st.session_state.chat_history.append({"role": "assistant", "content": synthesis})

                except Exception as e:
                    err = f"⚠️ Error: {e}\n\n```\n{traceback.format_exc()}\n```"
                    st.error(err)
                    st.session_state.chat_history.append({"role": "assistant", "content": err})

    if st.button("🗑 Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Crop Advisory
# ═══════════════════════════════════════════════════════════════════════════════
with tab_crop:
    st.subheader("🌱 Personalized Crop Advisory")
    st.caption("Get a complete, personalized farming plan for your crop and land conditions.")

    specific_q = st.text_area(
        "Specific Question (optional)",
        placeholder="e.g. When should I apply fertilizer for my wheat crop?",
        height=80,
    )

    if st.button("🌱 Get Crop Advisory", type="primary"):
        with st.spinner("🌱 IBM Granite generating crop plan… (~30–60s)"):
            try:
                orch = get_orchestrator()
                result = orch.get_crop_advice(farmer_profile, specific_q)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""<div class="metric-box">
                        <div class="value">{result['crop'].title()}</div>
                        <div class="label">Crop</div></div>""", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""<div class="metric-box">
                        <div class="value">{result['land_ha']} ha</div>
                        <div class="label">Land Area</div></div>""", unsafe_allow_html=True)
                with col3:
                    fert = result.get("fertilizer_schedule_kg_ha", {})
                    st.markdown(f"""<div class="metric-box">
                        <div class="value">N{fert.get('N','-')}:P{fert.get('P','-')}:K{fert.get('K','-')}</div>
                        <div class="label">Fertilizer (kg/ha)</div></div>""", unsafe_allow_html=True)

                st.markdown("### 🌾 Recommended Varieties")
                for v in result.get("recommended_varieties", []):
                    st.markdown(f"- **{v}**")

                st.markdown("### 📋 Advisory Plan")
                st.markdown(result["advice"])

            except Exception as e:
                st.error(f"Error: {e}")
                st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Weather & Irrigation
# ═══════════════════════════════════════════════════════════════════════════════
with tab_weather:
    st.subheader("🌤 Weather & Irrigation Advisor")

    col_l, col_r = st.columns([2, 1])
    with col_l:
        weather_location = st.text_input("Location for weather forecast", value=location, key="w_loc")
        weather_query = st.text_area("Your question", placeholder="Should I irrigate tomorrow?", height=100, key="w_q")
    with col_r:
        weather_crop = st.selectbox("Crop", ["wheat", "rice", "maize", "tomato", "potato", "cotton", "soybean", "groundnut"], key="w_crop")
        weather_soil = st.selectbox("Soil Type", ["loamy", "sandy", "clay", "silty", "black", "red"], key="w_soil")

    if st.button("🌤 Get Weather & Irrigation Advice", type="primary"):
        with st.spinner("🌤 Fetching weather data… (data loads fast, AI advice ~30–60s)"):
            try:
                orch = get_orchestrator()
                result = orch.get_weather_advice(weather_location, weather_crop, weather_soil, weather_query)

                weather = result["weather"]
                forecast = result["forecast"]

                # Current conditions
                st.markdown("### 🌡 Current Conditions")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Temperature", f"{weather['temperature_c']}°C")
                c2.metric("Humidity", f"{weather['humidity_pct']}%")
                c3.metric("Wind Speed", f"{weather['wind_speed_ms']} m/s")
                c4.metric("Irrigation Need", f"{result['irrigation_need_mm_day']} mm/day")
                st.caption(f"📍 {weather['location']} | Source: {weather['source']}")

                # Forecast chart
                st.markdown("### 📅 5-Day Forecast")
                if forecast:
                    dates = [f["date"] for f in forecast]
                    max_t = [f["max_temp_c"] for f in forecast]
                    min_t = [f["min_temp_c"] for f in forecast]
                    rain  = [f["rain_mm"] for f in forecast]

                    fig = go.Figure()
                    fig.add_trace(go.Bar(name="Rainfall (mm)", x=dates, y=rain,
                                         marker_color="#3b82f6", yaxis="y2", opacity=0.6))
                    fig.add_trace(go.Scatter(name="Max Temp °C", x=dates, y=max_t,
                                             line=dict(color="#ef4444", width=2), mode="lines+markers"))
                    fig.add_trace(go.Scatter(name="Min Temp °C", x=dates, y=min_t,
                                             line=dict(color="#f97316", width=2, dash="dot"), mode="lines+markers"))
                    fig.update_layout(
                        yaxis=dict(title="Temperature (°C)"),
                        yaxis2=dict(title="Rainfall (mm)", overlaying="y", side="right"),
                        legend=dict(orientation="h"),
                        height=320, margin=dict(l=20, r=20, t=20, b=20),
                    )
                    st.plotly_chart(fig, use_container_width=True)

                st.markdown("### 💧 Irrigation Advisory")
                st.markdown(result["advice"])

            except Exception as e:
                st.error(f"Error: {e}")
                st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Pest & Disease Detection
# ═══════════════════════════════════════════════════════════════════════════════
with tab_pest:
    st.subheader("🐛 Pest & Disease Detection")
    st.caption("Upload a crop image or describe symptoms for instant diagnosis and treatment recommendations.")

    p_col1, p_col2 = st.columns(2)
    with p_col1:
        pest_crop = st.selectbox("Affected Crop", ["wheat", "rice", "maize", "tomato", "potato", "cotton", "soybean", "groundnut"], key="p_crop")
        pest_location = st.text_input("Location", value=location, key="p_loc")
        symptoms = st.text_area(
            "Describe Symptoms",
            placeholder="e.g. Yellow spots on leaves, leaves curling, small insects visible on undersides...",
            height=120,
        )

    with p_col2:
        uploaded_image = st.file_uploader(
            "Upload Crop Image (JPG/PNG)",
            type=["jpg", "jpeg", "png", "webp"],
            help="Upload a clear photo of the affected plant part.",
        )
        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded crop image", use_column_width=True)

    if st.button("🔍 Diagnose Pest / Disease", type="primary"):
        if not symptoms and not uploaded_image:
            st.warning("Please describe symptoms or upload an image.")
        else:
            with st.spinner("🔬 IBM Granite diagnosing… (~30–60s)"):
                try:
                    orch = get_orchestrator()
                    image_bytes = uploaded_image.read() if uploaded_image else None
                    image_desc = uploaded_image.name if uploaded_image else ""
                    result = orch.get_pest_advice(pest_crop, symptoms, image_bytes, pest_location)

                    # Symptom matches
                    matches = result.get("symptom_matches", [])
                    if matches:
                        st.markdown("### 🔬 Symptom Pattern Matches")
                        for m in matches:
                            with st.expander(f"📌 {m['symptom'].title()} (crops: {m['crops_affected']})"):
                                for cause in m["possible_causes"]:
                                    st.markdown(f"- {cause}")

                    st.markdown("### 🩺 Diagnosis & Treatment Plan")
                    st.markdown(result["advice"])

                except Exception as e:
                    st.error(f"Error: {e}")
                    st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Market Insights
# ═══════════════════════════════════════════════════════════════════════════════
with tab_market:
    st.subheader("📈 Market Insights & Cost Optimization")

    m_col1, m_col2 = st.columns(2)
    with m_col1:
        market_crop = st.selectbox("Crop", ["wheat", "rice", "maize", "tomato", "potato", "cotton", "soybean", "groundnut", "mustard", "arhar", "gram"], key="m_crop")
        market_land = st.number_input("Land Area (ha)", min_value=0.1, max_value=500.0, value=land_ha, key="m_land")
        market_location = st.text_input("Location", value=location, key="m_loc")
    with m_col2:
        yield_level = st.selectbox("Expected Yield Level", ["low", "medium", "high"])
        market_query = st.text_area("Your Question", placeholder="When is the best time to sell my wheat?", height=80, key="m_q")

    if st.button("📈 Get Market Analysis", type="primary"):
        with st.spinner("📈 Calculating financials + IBM Granite market analysis… (~30–60s)"):
            try:
                orch = get_orchestrator()
                result = orch.get_market_advice(market_crop, market_land, market_location, market_query)
                econ = result["economics"]

                # Economics cards
                st.markdown("### 💰 Financial Projections")
                e1, e2, e3, e4 = st.columns(4)
                e1.metric("Total Yield", f"{econ['total_yield_qtl']} qtl")
                e2.metric("Input Cost", f"₹{econ['input_cost_inr']:,}")
                e3.metric("Gross Income", f"₹{econ['gross_income_inr']:,}")
                e4.metric("Net Profit", f"₹{econ['net_profit_inr']:,}",
                          delta=f"ROI: {econ['roi_pct']}%")

                # Waterfall chart
                fig = go.Figure(go.Waterfall(
                    name="Financials",
                    orientation="v",
                    measure=["absolute", "relative", "total"],
                    x=["Input Cost", "Gross Income", "Net Profit"],
                    y=[-econ["input_cost_inr"], econ["gross_income_inr"], 0],
                    totals={"marker": {"color": "#10b981"}},
                    increasing={"marker": {"color": "#3b82f6"}},
                    decreasing={"marker": {"color": "#ef4444"}},
                    connector={"line": {"color": "#6b7280"}},
                ))
                fig.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)

                if result.get("msp_inr_quintal"):
                    st.info(f"📌 MSP (2024–25) for **{market_crop}**: ₹{result['msp_inr_quintal']:,}/quintal")

                st.markdown("### 📊 Market Advisory")
                st.markdown(result["advice"])

            except Exception as e:
                st.error(f"Error: {e}")
                st.code(traceback.format_exc())


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — Knowledge Base (RAG viewer)
# ═══════════════════════════════════════════════════════════════════════════════
with tab_rag:
    st.subheader("📚 Agricultural Knowledge Base Search")
    st.caption("Search the RAG knowledge base used by all agents. Powered by semantic retrieval.")

    rag_query = st.text_input("Search query", placeholder="e.g. fertilizer schedule for rice", key="rag_q")
    top_k = st.slider("Number of results", 1, 8, 4)

    if st.button("🔎 Search Knowledge Base") and rag_query:
        with st.spinner("Retrieving relevant passages…"):
            try:
                from rag_system import get_rag
                rag = get_rag()
                results = rag.retrieve(rag_query, top_k)

                for i, (chunk, score) in enumerate(results, 1):
                    with st.expander(f"📄 Result {i} — Relevance: {score:.3f}"):
                        st.markdown(chunk)
            except Exception as e:
                st.error(f"Error: {e}")
                st.code(traceback.format_exc())

    # Knowledge topics overview
    st.markdown("---")
    st.markdown("### 📖 Topics in Knowledge Base")
    topics = [
        ("🌱 Soil Health & Management", "pH, organic matter, NPK, amendments"),
        ("💧 Irrigation & Water Management", "Drip/sprinkler systems, ET₀, scheduling"),
        ("🌾 Rice Cultivation", "Varieties, nursery, fertilizer, diseases"),
        ("🌾 Wheat Cultivation", "Rabi season, varieties, irrigation stages"),
        ("🌽 Maize Cultivation", "Hybrid varieties, fertilizer, spacing"),
        ("🍅 Tomato Cultivation", "Varieties, transplanting, IPM"),
        ("🐛 Integrated Pest Management", "Cultural, biological, chemical options"),
        ("🦠 Disease Identification", "Fungal, bacterial, viral diseases"),
        ("📈 Market & Economics", "MSP, eNAM, FPO, cost optimization"),
        ("🌡 Climate-Smart Agriculture", "Drought/heat tolerant varieties, AWD"),
        ("🏛 Government Schemes", "PM-KISAN, PMFBY, KCC, soil health card"),
        ("🧪 Fertilizer Management", "Macro/micro nutrients, bio-fertilizers"),
    ]
    cols = st.columns(2)
    for i, (title, desc) in enumerate(topics):
        with cols[i % 2]:
            st.markdown(f"""<div class="agent-card">
                <h4>{title}</h4>
                <p style="margin:0; color:#6b7280; font-size:0.85rem">{desc}</p>
            </div>""", unsafe_allow_html=True)
