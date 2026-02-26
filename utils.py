import os
from typing import Literal

import dspy
from dotenv import load_dotenv

load_dotenv()

ModelType = Literal["small_model", "reasoning_model", "sota_model"]

PROVIDER_CONFIG = {
    "OPENROUTER_API_KEY": {
        "small_model": "openrouter/openai/gpt-4o-mini",
        "reasoning_model": "openrouter/google/gemini-2.5-flash",
        "sota_model": "openrouter/anthropic/claude-opus-4.6",
    },
    "OPENAI_API_KEY": {
        "small_model": "openai/gpt-4o-mini",
        "reasoning_model": "openai/gpt-5-mini-2025-08-07",
        "sota_model": "openai/gpt-5.2-2025-12-11",
    },
    "ANTHROPIC_API_KEY": {
        "small_model": "anthropic/claude-haiku-4-5",
        "reasoning_model": "anthropic/claude-sonnet-4-6",
        "sota_model": "anthropic/claude-opus-4-6",
    },
    "GEMINI_API_KEY": {
        "small_model": "gemini/gemini-2.5-flash-lite",
        "reasoning_model": "gemini/gemini-2.5-flash",
        "sota_model": "gemini/gemini-3-pro-preview",
    },
}

# Models that need a specific temperature override
TEMPERATURE_OVERRIDES = {
    "openrouter/openai/gpt-4o-mini": 0.7,
    "openai/gpt-4o-mini": 0.7,
    "gemini/gemini-3-pro-preview": 1.0,
}


def initialize_dspy(model_type: ModelType = "small_model"):
    for env_key, models in PROVIDER_CONFIG.items():
        api_key = os.getenv(env_key)
        if not api_key:
            continue

        model = models[model_type]
        lm_kwargs = dict(
            model=model,
            api_key=api_key,
            cache=False,
            max_tokens=10000,
        )
        if model in TEMPERATURE_OVERRIDES:
            lm_kwargs["temperature"] = TEMPERATURE_OVERRIDES[model]

        lm = dspy.LM(**lm_kwargs)
        dspy.configure(lm=lm, track_usage=True)
        return lm

    raise RuntimeError(
        "No API key found. Set one of: "
        + ", ".join(PROVIDER_CONFIG.keys())
    )
