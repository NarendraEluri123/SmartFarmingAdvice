"""
Agricultural Knowledge Base — static documents used for RAG.
These cover best practices, crop guidelines, and advisory info.
"""

AGRICULTURAL_KNOWLEDGE = [
    # ── Soil Health ──────────────────────────────────────────────────────────
    """
SOIL HEALTH AND MANAGEMENT BEST PRACTICES

Healthy soil is the foundation of productive farming. Key indicators of soil health include:
- pH level: Most crops thrive between pH 6.0–7.0. Acidic soils (pH < 6) require lime application.
- Organic matter: Aim for 3–5% organic matter for optimal nutrient availability.
- Nitrogen (N): Essential for leafy growth; deficiency shows as yellowing of older leaves.
- Phosphorus (P): Critical for root development and flowering; deficiency shows as purple-tinged leaves.
- Potassium (K): Improves disease resistance and water regulation; deficiency shows as brown leaf edges.

Soil amendment strategies:
- Apply compost (5–10 tonnes/hectare) to improve structure and microbial activity.
- Use green manures/cover crops (legumes like clover) to fix atmospheric nitrogen.
- Conduct soil tests every 2–3 years to monitor pH and nutrient levels.
- Practice crop rotation to reduce nutrient depletion and break pest/disease cycles.
- Minimum tillage preserves soil structure and reduces erosion.
""",

    # ── Water & Irrigation ───────────────────────────────────────────────────
    """
IRRIGATION AND WATER MANAGEMENT

Efficient water management is critical for sustainable farming:

Drip irrigation:
- Delivers water directly to the root zone; reduces water use by 30–50% vs flood irrigation.
- Ideal for vegetables, fruits, and row crops.
- Recommended pressure: 0.5–1.5 bar.

Sprinkler irrigation:
- Suitable for field crops (wheat, maize, groundnut).
- Best applied in early morning to minimise evaporation and foliar disease.

Scheduling guidelines:
- Light soils (sandy): irrigate more frequently with smaller amounts.
- Heavy soils (clay): less frequent, deeper irrigation.
- Use soil moisture sensors or tensiometers at 15 cm and 30 cm depth.
- Crop water requirements (ETc) = Reference ET (ET₀) × crop coefficient (Kc).

Signs of water stress:
- Wilting during cooler parts of day (severe stress).
- Leaf curl, reduced turgidity.
- Premature fruit drop.
""",

    # ── Major Crops ───────────────────────────────────────────────────────────
    """
RICE CULTIVATION GUIDELINES

Variety selection:
- Short-duration (90–100 days): Suitable for water-scarce regions; IR64, MTU 1010.
- Medium-duration (110–120 days): Higher yield potential; Swarna, BPT 5204.
- Long-duration (>130 days): For areas with assured irrigation; Jaya, Pusa Basmati.

Nursery management:
- Sow seeds in well-prepared nursery beds at 30 kg seed/hectare.
- Transplant 21–25-day-old seedlings (2–3 seedlings/hill).
- Spacing: 20×15 cm for high-yielding varieties.

Fertilizer schedule (per hectare):
- Basal: 50 kg DAP + 50 kg MOP before transplanting.
- Top dress 1 (21 days after transplanting): 50 kg urea.
- Top dress 2 (45 days after transplanting): 50 kg urea.

Water management:
- Maintain 2–5 cm standing water during vegetative stage.
- Drain 10 days before harvest for uniform ripening.

Common diseases: Blast (Magnaporthe oryzae), Brown spot, Sheath blight.
""",

    """
WHEAT CULTIVATION GUIDELINES

Sowing season: Rabi (October–December in South Asia).
Optimum temperature: 10–25 °C during growing period.

Recommended varieties:
- HD 3086, GW 496 (drought-tolerant); HD 2967, DBW 17 (irrigated conditions).

Seed rate: 100–125 kg/ha (timely sown); 125–150 kg/ha (late sown).
Spacing: Row-to-row 22.5 cm; seed depth 5–6 cm.

Fertilizer (per hectare):
- N:P:K = 120:60:40 kg/ha for irrigated; 90:40:30 kg/ha for rainfed.
- Apply full P & K and 1/3 N at sowing; 1/3 N at first irrigation (CRI stage); 1/3 N at flag leaf.

Irrigation: 5–6 irrigations at CRI, tillering, jointing, booting, grain filling, and dough stages.
Critical irrigation: Crown Root Initiation (20–25 days after sowing).

Harvesting: Grain moisture ~14%; avoid delays to prevent shattering.
""",

    """
MAIZE (CORN) CULTIVATION GUIDELINES

Seasons: Kharif (June–July sowing) and Rabi (October–November).
Temperature: 21–30 °C; frost-sensitive.

Varieties:
- Hybrid: DKC 9144, PEHM 2 (high yield, 8–10 t/ha).
- Open-pollinated: Vijay, Ganga Safed (suitable for subsistence farming).

Spacing: 75 cm × 25 cm (single cross hybrids); 60 cm × 20 cm (composites).
Seed rate: 20–25 kg/ha.

Fertilizer (per hectare): N:P:K = 150:75:50 kg.
- 50% N + full P + full K at sowing.
- 25% N at knee-high stage (V6).
- 25% N at tasselling.

Critical stages for irrigation: Germination, knee-high, tasselling, grain fill.
""",

    """
TOMATO CULTIVATION GUIDELINES

Growing conditions: Temperature 20–27 °C day, 15–20 °C night; full sun (6–8 hours).
pH range: 6.0–6.8.

Varieties:
- Indeterminate: Arka Vikas, Pusa Ruby (fresh market).
- Determinate (processing): Pusa Hybrid-2, Naveen.

Nursery: Sow in raised beds or trays; transplant at 30–35 days (4–6 leaf stage).
Spacing: 60 × 45 cm or 75 × 60 cm.

Fertilizer (per hectare): 
- N:P:K = 120:60:60 kg/ha.
- Apply 20% N + full P + full K at transplanting; remaining N in 4 splits.

Common pests: Fruit borer (Helicoverpa), Whitefly, Aphids.
Common diseases: Early blight, Late blight, Bacterial wilt, Leaf curl virus.

Harvesting: Mature green to breaker stage for long-distance transport; vine-ripe for local markets.
""",

    # ── Pest & Disease Management ─────────────────────────────────────────────
    """
INTEGRATED PEST MANAGEMENT (IPM)

IPM principles:
1. Prevention: Crop rotation, resistant varieties, proper spacing, clean seed.
2. Monitoring: Regular field scouting; use pheromone traps for bollworm/stem borer.
3. Threshold-based intervention: Act only when Economic Threshold Level (ETL) is reached.
4. Biological control: Release Trichogramma parasitoids (egg parasitoids); use Bt (Bacillus thuringiensis) spray.
5. Chemical control: Last resort; use selective, low-toxicity pesticides; follow label instructions.

Common pests and management:
- Aphids: Spray imidacloprid 17.8 SL @ 0.5 mL/L or neem oil 5 mL/L.
- Whitefly: Yellow sticky traps; thiamethoxam 25 WG @ 0.3 g/L.
- Stem borer (rice): Cartap hydrochloride 4G @ 18 kg/ha.
- Fruit borer (tomato/brinjal): Spinosad 45 SC @ 0.3 mL/L; pheromone traps at 5/acre.
- Red spider mite: Propargite 57 EC @ 1.5 mL/L; increase humidity.

Safe pesticide handling:
- Wear PPE (gloves, mask, goggles).
- Spray in early morning or evening; avoid windy conditions.
- Observe pre-harvest intervals (PHI) strictly.
""",

    """
CROP DISEASE IDENTIFICATION AND MANAGEMENT

Fungal diseases:
- Early blight (Alternaria): Brown concentric rings on older leaves. Apply mancozeb 75 WP @ 2 g/L.
- Late blight (Phytophthora): Water-soaked lesions turning brown. Apply metalaxyl + mancozeb @ 2 g/L.
- Powdery mildew: White powdery coating. Apply sulphur 80 WP @ 2 g/L or triadimefon.
- Rust: Orange/brown pustules on leaves. Apply propiconazole 25 EC @ 1 mL/L.

Bacterial diseases:
- Bacterial wilt (Ralstonia): Sudden wilting; no leaf yellowing. No cure; remove and destroy plants. Use resistant varieties.
- Bacterial leaf blight (rice): Yellow-orange stripe on leaf margin. Apply copper oxychloride @ 3 g/L.

Viral diseases:
- Leaf curl virus (tomato): Transmitted by whitefly. Control vector; use virus-free seedlings; resistant varieties.
- Mosaic virus: Mottled yellow-green patterns. Remove infected plants; control aphid vectors.

General preventive measures:
- Use certified disease-free seeds.
- Maintain field hygiene; remove crop debris.
- Avoid overhead irrigation for foliage diseases.
- Apply preventive fungicide sprays during humid conditions.
""",

    # ── Market & Economics ────────────────────────────────────────────────────
    """
AGRICULTURAL MARKET AND ECONOMICS

Minimum Support Price (MSP) guidance (India 2024–25, indicative):
- Wheat: ₹2,275/quintal
- Rice (Common): ₹2,300/quintal
- Maize: ₹2,090/quintal
- Cotton (Medium): ₹7,121/quintal
- Soybean: ₹4,892/quintal
- Groundnut: ₹6,783/quintal

Market linkage strategies:
- Register on e-NAM (National Agriculture Market) for transparent price discovery.
- Join Farmer Producer Organizations (FPOs) to aggregate produce and reduce intermediary costs.
- Direct marketing through weekly haats or farm-gate sales reduces transportation costs.
- Cold storage (if available) allows selling during off-peak high-price periods.

Cost optimization:
- Group purchase of inputs through FPOs can reduce input cost by 15–20%.
- Custom hiring centres (CHCs) for mechanised operations reduce machinery cost.
- Crop insurance (PMFBY) protects against climate-related losses.
- Precision application of inputs based on soil testing reduces waste and cost.
""",

    # ── Climate-Smart Farming ────────────────────────────────────────────────
    """
CLIMATE-SMART AGRICULTURE

Adapting to climate change:
1. Drought-tolerant varieties: Use varieties with good performance under water stress.
   - Rice: DRR Dhan 42, Sahbhagi Dhan. Wheat: HD 4728 (Pusa Malvi).
2. Heat-tolerant varieties: Especially important for wheat in terminal heat stress.
   - HD 3385, K 0307.
3. Short-duration varieties: Escape terminal drought by completing lifecycle earlier.

Mitigation strategies:
- Alternate Wetting and Drying (AWD) in rice reduces methane emissions by 30–40% and saves 20–30% irrigation water.
- Conservation agriculture (zero tillage, mulching) reduces soil carbon loss.
- Agroforestry: Integrate trees with crops for carbon sequestration and shade.

Weather-based advisories:
- Cold wave: Cover nursery beds; avoid irrigation during frost risk periods.
- Heat wave: Mulch soil; increase irrigation frequency; harvest early morning.
- Heavy rainfall forecast: Ensure drainage channels are open; delay fertilizer application.
- Cyclone/storm: Harvest mature crops early; tie-up/stake tall crops.
""",

    # ── Government Schemes ────────────────────────────────────────────────────
    """
GOVERNMENT AGRICULTURAL SCHEMES AND SUBSIDIES (INDIA)

Key central schemes:
- PM-KISAN: ₹6,000/year direct income support in 3 installments to eligible farmers.
- PMFBY (Pradhan Mantri Fasal Bima Yojana): Crop insurance with low premium (2% for Kharif, 1.5% for Rabi).
- PM Krishi Sinchai Yojana: Subsidized drip/sprinkler irrigation ("Har Khet Ko Pani, More Crop Per Drop").
- Soil Health Card Scheme: Free soil testing; fertilizer recommendations.
- eNAM: Online agricultural markets for price transparency.
- MIDH: Subsidy for horticulture development (50% subsidy on capital cost).
- KCC (Kisan Credit Card): Short-term crop loans at subsidized 4% interest.

State-level schemes vary; farmers should contact the local Krishi Vigyan Kendra (KVK) or Agriculture Extension Officer for region-specific entitlements.
""",

    # ── Fertilizer Management ─────────────────────────────────────────────────
    """
FERTILIZER MANAGEMENT AND NUTRIENT GUIDELINES

Macronutrients:
- Nitrogen (N): Promotes vegetative growth. Sources: Urea (46% N), CAN (26% N), DAP (18% N).
  Excess N: Promotes pest/disease, delays maturity, lodging risk.
- Phosphorus (P₂O₅): Root and fruit development. Sources: DAP (46% P), SSP (16% P).
  Apply in basal dose; P availability reduces in alkaline soils.
- Potassium (K₂O): Water regulation, disease resistance. Sources: MOP (60% K), SOP (50% K).

Micronutrients:
- Zinc (Zn): Common deficiency in rice/wheat; apply zinc sulphate @ 25 kg/ha.
- Boron (B): Critical for fruit/seed set; apply borax @ 1 kg/ha or foliar 0.2%.
- Iron (Fe): Deficiency in alkaline soils; foliar ferrous sulphate 0.5%.

Bio-fertilizers:
- Rhizobium: For legumes (soybean, groundnut) — fixes atmospheric N₂.
- Azospirillum: For cereals — associative N fixation, growth promotion.
- PSB (Phosphate Solubilising Bacteria): Improves P availability from soil.
- Mycorrhizae: Enhances nutrient and water uptake; especially useful in poor soils.

Application tips:
- Split N application (3–4 doses) improves use efficiency and reduces leaching.
- Leaf colour chart (LCC) for rice helps determine N top-dressing need visually.
- Fertigation (drip + fertilizer) increases NUE by 40–60% vs broadcast application.
""",
]
