"""
IBM watsonx.ai LLM client — IBM Granite 4 H Small
- Single shared ModelInference singleton (created once, reused everywhere)
- Auto-retry with exponential backoff on 429 rate-limit errors
- Local fallback response when API is unavailable
"""
from __future__ import annotations

import time
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from config import IBM_API_KEY, IBM_PROJECT_ID, IBM_WATSONX_URL, LLM_MODEL_ID, LLM_PARAMS

# ── singleton ─────────────────────────────────────────────────────────────────
_MODEL: ModelInference | None = None

# retry config
_MAX_RETRIES = 3
_RETRY_DELAYS = [5, 15, 30]   # seconds between retries


def get_llm_model() -> ModelInference:
    """Return the shared ModelInference instance, creating it once."""
    global _MODEL
    if _MODEL is None:
        _MODEL = ModelInference(
            model_id=LLM_MODEL_ID,
            credentials=Credentials(url=IBM_WATSONX_URL, api_key=IBM_API_KEY),
            project_id=IBM_PROJECT_ID,
            params={
                GenParams.MAX_NEW_TOKENS:      LLM_PARAMS["max_new_tokens"],
                GenParams.TEMPERATURE:         LLM_PARAMS["temperature"],
                GenParams.TOP_P:               LLM_PARAMS["top_p"],
                GenParams.REPETITION_PENALTY:  LLM_PARAMS["repetition_penalty"],
            },
        )
    return _MODEL


def _call_with_retry(prompt: str) -> str:
    """Call generate_text with automatic retry on 429 rate-limit errors."""
    model = get_llm_model()
    last_err: Exception | None = None

    for attempt in range(_MAX_RETRIES + 1):
        try:
            return model.generate_text(prompt=prompt)
        except Exception as exc:
            msg = str(exc)
            if "429" in msg or "consumption_limit_reached" in msg:
                if attempt < _MAX_RETRIES:
                    wait = _RETRY_DELAYS[attempt]
                    print(f"[IBM API] Rate limited. Retrying in {wait}s (attempt {attempt+1}/{_MAX_RETRIES})…")
                    time.sleep(wait)
                    last_err = exc
                    continue
            raise  # non-429 errors bubble up immediately

    # All retries exhausted → return fallback
    print(f"[IBM API] All retries exhausted. Returning fallback. Last error: {last_err}")
    return _fallback_response(prompt)


def _fallback_response(prompt: str) -> str:
    """
    Rule-based fallback used when IBM API is rate-limited.
    Returns a short, useful generic advisory so the UI stays functional.
    """
    p = prompt.lower()
    if "weather" in p or "irrigation" in p or "rain" in p:
        return (
            "⚠️ IBM API is busy — showing cached advice.\n\n"
            "**Weather & Irrigation Tip:** Check local weather before irrigating. "
            "As a rule, irrigate when soil moisture at 15 cm depth feels dry. "
            "For most crops, morning irrigation reduces evaporation losses by 20–30%."
        )
    if "pest" in p or "disease" in p or "symptom" in p:
        return (
            "⚠️ IBM API is busy — showing cached advice.\n\n"
            "**Pest/Disease Tip:** Yellow leaves often indicate nitrogen deficiency or aphid infestation. "
            "Spray neem oil (5 mL/L) as a first step. If symptoms persist after 3 days, apply "
            "imidacloprid 17.8 SL @ 0.5 mL/L. Consult your local KVK for lab diagnosis."
        )
    if "market" in p or "price" in p or "sell" in p:
        return (
            "⚠️ IBM API is busy — showing cached advice.\n\n"
            "**Market Tip:** Avoid selling immediately after harvest when prices are lowest. "
            "Store produce for 4–8 weeks if possible. Register on eNAM for transparent price discovery. "
            "Join an FPO to improve bargaining power and reduce input costs by 15–20%."
        )
    return (
        "⚠️ IBM API is currently rate-limited (free plan: 10 concurrent requests max).\n\n"
        "**General Farming Tip:** Conduct a soil test before every season, "
        "use certified seeds from reputable sources, split fertilizer doses for better uptake, "
        "and scout fields weekly for early pest/disease detection. "
        "Try again in 30 seconds for a personalised AI response."
    )


def generate_with_system(
    system_prompt: str,
    user_message: str,
    model: ModelInference | None = None,   # kept for backward-compat, ignored
) -> str:
    """Prompt the model with a system + user turn and return the response text."""
    prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{user_message}\n<|assistant|>\n"
    return _call_with_retry(prompt)


def generate_text(prompt: str, model: ModelInference | None = None) -> str:
    """Raw generate_text call with retry."""
    return _call_with_retry(prompt)
