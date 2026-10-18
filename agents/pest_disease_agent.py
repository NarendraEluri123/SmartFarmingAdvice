"""
Pest & Disease Detection Agent
Accepts crop image uploads OR text descriptions to identify pests/diseases
and provide instant management recommendations.
"""
from __future__ import annotations

import base64
import io
from typing import Any

from llm_client import generate_with_system
from rag_system import get_rag

# ─────────────────────────────────────────────────────────────────────────────
# Knowledge tables
# ─────────────────────────────────────────────────────────────────────────────

PEST_SYMPTOMS: dict[str, dict] = {
    "yellowing leaves": {
        "possible_causes": ["Nitrogen deficiency", "Iron deficiency (alkaline soil)", "Viral infection", "Waterlogging"],
        "crops_affected": "All crops",
    },
    "brown spots": {
        "possible_causes": ["Early blight (Alternaria solani)", "Brown spot (Helminthosporium)", "Bacterial leaf spot"],
        "crops_affected": "Tomato, Rice, Potato",
    },
    "white powder on leaves": {
        "possible_causes": ["Powdery mildew (Erysiphales)"],
        "crops_affected": "Cucurbits, Wheat, Grapes",
    },
    "water soaked lesions": {
        "possible_causes": ["Late blight (Phytophthora infestans)", "Bacterial blight"],
        "crops_affected": "Tomato, Potato, Rice",
    },
    "curled leaves": {
        "possible_causes": ["Leaf curl virus", "Aphid infestation", "Thrips", "Water stress"],
        "crops_affected": "Tomato, Cotton, Chilli",
    },
    "holes in leaves": {
        "possible_causes": ["Caterpillars / Leaf roller", "Flea beetles", "Shot-hole disease"],
        "crops_affected": "Brassicas, Beans, Eggplant",
    },
    "wilting": {
        "possible_causes": ["Fusarium wilt", "Bacterial wilt", "Root rot", "Water deficit"],
        "crops_affected": "Tomato, Banana, Cotton",
    },
    "orange rust pustules": {
        "possible_causes": ["Wheat stem rust (Puccinia graminis)", "Leaf rust"],
        "crops_affected": "Wheat, Barley",
    },
    "sticky substance on leaves": {
        "possible_causes": ["Aphid honeydew → Sooty mould", "Whitefly", "Scale insects"],
        "crops_affected": "All crops",
    },
    "dead heart in paddy": {
        "possible_causes": ["Rice stem borer (Scirpophaga incertulas)"],
        "crops_affected": "Rice",
    },
}

IMAGE_ANALYSIS_KEYWORDS: dict[str, str] = {
    "yellow": "yellowing / chlorosis observed",
    "brown": "brown lesions / necrosis observed",
    "white": "white powder or fungal growth observed",
    "hole": "feeding damage / holes in leaf tissue observed",
    "curl": "leaf curl / distortion observed",
    "wilt": "wilting / loss of turgidity observed",
    "rust": "rust-colored pustules observed",
    "spot": "spots / lesion patterns observed",
    "dead": "dead tissue / die-back observed",
    "mold": "mold / fungal growth observed",
    "insect": "insect presence detected",
    "larvae": "larval feeding damage observed",
}


def _analyze_image_description(description: str) -> list[str]:
    """Extract symptom keywords from image description text."""
    desc_lower = description.lower()
    found = []
    for keyword, observation in IMAGE_ANALYSIS_KEYWORDS.items():
        if keyword in desc_lower:
            found.append(observation)
    return found


def _match_symptoms(symptoms_text: str) -> list[dict]:
    """Match described symptoms against the knowledge table."""
    symptoms_lower = symptoms_text.lower()
    matches = []
    for symptom_key, data in PEST_SYMPTOMS.items():
        if any(word in symptoms_lower for word in symptom_key.split()):
            matches.append({"symptom": symptom_key, **data})
    return matches[:4]  # top 4 matches


def _encode_image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Agent
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are the Pest & Disease Detection Agent (IBM Granite). Identify pests/diseases from symptoms, give a concise diagnosis with 2-3 likely causes, IPM treatment options with dosages, and prevention tips. Be brief."""


class PestDiseaseAgent:
    """Pest & Disease Detection Agent with multimodal support."""

    def __init__(self):
        self._rag = get_rag()

    def run(
        self,
        crop: str,
        symptoms: str = "",
        image_bytes: bytes | None = None,
        image_description: str = "",
        location: str = "",
    ) -> dict[str, Any]:
        """
        Detect pest/disease from symptoms text and/or image.
        Returns diagnosis, confidence reasoning, and management recommendations.
        """
        # Combine all evidence
        evidence_parts = []
        if symptoms:
            evidence_parts.append(f"Farmer-reported symptoms: {symptoms}")
        if image_description:
            evidence_parts.append(f"Image description: {image_description}")
            obs = _analyze_image_description(image_description)
            if obs:
                evidence_parts.append("Automated image observations:\n  - " + "\n  - ".join(obs))
        if image_bytes:
            # In a full deployment, pass the base64 image to a vision-capable model.
            # Here we note its presence for the LLM context.
            size_kb = len(image_bytes) / 1024
            evidence_parts.append(
                f"Crop image uploaded ({size_kb:.1f} KB). "
                "Analyze the image for discoloration, lesions, insects, or abnormal growth patterns."
            )

        if not evidence_parts:
            evidence_parts.append("No specific symptoms provided. Give general pest/disease prevention advice.")

        evidence_text = "\n".join(evidence_parts)

        # Symptom matching
        all_symptoms = f"{symptoms} {image_description}"
        matched = _match_symptoms(all_symptoms)
        match_summary = ""
        if matched:
            lines = []
            for m in matched:
                lines.append(
                    f"  • {m['symptom'].title()}: likely causes = {', '.join(m['possible_causes'])} "
                    f"(crops: {m['crops_affected']})"
                )
            match_summary = "Symptom database matches:\n" + "\n".join(lines)

        # RAG context
        rag_ctx = self._rag.get_context(
            f"pest disease {crop} detection management IPM treatment"
        )

        user_msg = f"""Crop: {crop} | Location: {location or "India"}
{evidence_text}
{match_summary}
Context: {rag_ctx[:400]}
Give: 1) Top 2-3 diagnoses 2) Severity 3) Immediate action 4) Treatment with dosages 5) Prevention. Be concise."""
        advice = generate_with_system(SYSTEM_PROMPT, user_msg)

        return {
            "agent": "Pest & Disease Detection Agent",
            "crop": crop,
            "symptoms_provided": symptoms,
            "image_uploaded": image_bytes is not None,
            "symptom_matches": matched,
            "advice": advice,
        }
