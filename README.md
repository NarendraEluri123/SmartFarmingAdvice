# 🌾 Smart Farming Advisor

**AI-Powered Agricultural Intelligence System**  
Powered by **IBM Granite 4 H Small** via **IBM watsonx.ai**

---

## Overview

Smart Farming Advisor is a multi-agent AI system that provides personalised, real-time, and sustainable agricultural advice to farmers. The system combines Retrieval-Augmented Generation (RAG) with four specialised AI agents, orchestrated by IBM Granite 4 H Small.

```
┌─────────────────────────────────────────────────────────────┐
│              Smart Farming Orchestrator (IBM Granite)        │
│                                                             │
│  ┌──────────────┐ ┌─────────────┐ ┌──────────┐ ┌────────┐ │
│  │ Crop Advisory│ │Weather &    │ │Pest &    │ │Market  │ │
│  │    Agent     │ │Irrigation   │ │Disease   │ │Insights│ │
│  │              │ │   Agent     │ │  Agent   │ │ Agent  │ │
│  └──────────────┘ └─────────────┘ └──────────┘ └────────┘ │
│                                                             │
│                    RAG Knowledge Base                        │
│         (12 agricultural domains, vector indexed)           │
└─────────────────────────────────────────────────────────────┘
```

---

## Features

| Feature | Description |
|---|---|
| 🌱 **Crop Advisory** | Personalised variety selection, fertilizer program, sowing/harvest timeline |
| 🌤 **Weather & Irrigation** | Real-time weather, ET₀ calculation, irrigation scheduling |
| 🐛 **Pest & Disease Detection** | Symptom analysis + image upload, IPM treatment plans |
| 📈 **Market Insights** | MSP guidance, selling strategy, ROI projections, cost optimization |
| 📚 **RAG Knowledge Base** | 12 domains: soil health, irrigation, 6 crops, IPM, market, govt schemes |
| 💬 **Chat Assistant** | Natural language queries routed to specialist agents |

---

## Tech Stack

- **LLM**: IBM Granite 4 H Small (`ibm/granite-4-0-8b-preview`) via IBM watsonx.ai
- **RAG**: Sentence-transformers + cosine similarity vector search
- **UI**: Streamlit + Plotly
- **Agents**: Custom Python multi-agent architecture
- **Weather**: OpenWeatherMap API (demo mode included)

---

## Project Structure

```
SmartFarmingAdvice/
├── app.py                          # Streamlit UI
├── orchestrator.py                 # Multi-agent orchestrator
├── llm_client.py                   # IBM watsonx.ai / Granite client
├── rag_system.py                   # RAG retrieval engine
├── knowledge_base.py               # Agricultural knowledge documents
├── config.py                       # Configuration & credentials
├── test_agents.py                  # CLI test suite
├── requirements.txt                # Python dependencies
└── agents/
    ├── __init__.py
    ├── crop_advisory_agent.py      # Crop Advisory Agent
    ├── weather_irrigation_agent.py # Weather & Irrigation Agent
    ├── pest_disease_agent.py       # Pest & Disease Detection Agent
    └── market_insights_agent.py    # Market Insights Agent
```

---

## Installation

```bash
# 1. Clone the repository
git clone <repo-url>
cd SmartFarmingAdvice

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Running the Application

### Web UI (Streamlit)
```bash
streamlit run app.py
```
Open http://localhost:8501 in your browser.

### CLI Test Suite
```bash
# Run all tests
python test_agents.py

# Run a specific agent test
python test_agents.py rag
python test_agents.py llm
python test_agents.py weather
python test_agents.py pest
python test_agents.py crop
python test_agents.py market
python test_agents.py orchestrator
```

---

## IBM watsonx.ai Credentials

| Parameter | Value |
|---|---|
| Project ID | `a732d551-9d07-47e7-a957-e1e80082ce52` |
| API Key | Configured in `config.py` |
| Model | `ibm/granite-4-0-8b-preview` (IBM Granite 4 H Small) |
| Region | `us-south.ml.cloud.ibm.com` |

---

## Agent Architecture

### Orchestrator
- Classifies farmer query intent (weather / pest / market / crop)
- Routes to one or more specialist agents in parallel
- Synthesizes agent outputs into a unified, actionable response

### Crop Advisory Agent
- Variety recommendations per soil/climate
- Personalized fertilizer program (N-adjusted for soil type)
- Sowing-to-harvest timeline

### Weather & Irrigation Agent
- OpenWeatherMap integration (real-time + 5-day forecast)
- Hargreaves–Samani ET₀ estimation
- Net irrigation need calculation (ETc − rainfall)

### Pest & Disease Detection Agent
- Symptom keyword matching against 10 common pest/disease patterns
- Multimodal: accepts image uploads
- IPM-first treatment recommendations

### Market Insights Agent
- MSP database (2024–25, 12 crops)
- Input cost & profit projection for any land area
- Seasonal price trend analysis
- Market channel comparison (APMC, eNAM, FPO, direct)

---

## RAG Knowledge Base Topics

1. Soil Health & Management
2. Irrigation & Water Management
3. Rice Cultivation Guidelines
4. Wheat Cultivation Guidelines
5. Maize Cultivation Guidelines
6. Tomato Cultivation Guidelines
7. Integrated Pest Management (IPM)
8. Crop Disease Identification
9. Agricultural Market & Economics
10. Climate-Smart Agriculture
11. Government Schemes & Subsidies
12. Fertilizer Management & Nutrients

---

## License

MIT License — for educational and research purposes.

---

*Built with IBM Granite 4 H Small · IBM watsonx.ai · IBM Cloud*
