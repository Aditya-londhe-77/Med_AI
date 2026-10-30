
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

_gemini_client_initialized = False
_init_attempted = False


def get_api_key() -> Optional[str]:
    """Retrieve Gemini or Vertex API key from environment."""
    key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("VERTEX_API_KEY")
    )

    if key and key.startswith("your-"):
        return None

    return key


def is_configured() -> bool:
    """Returns True if a Gemini API key is configured."""
    return bool(get_api_key())


def init_gemini() -> bool:
    global _gemini_client_initialized, _init_attempted

    if _gemini_client_initialized:
        return True

    if _init_attempted:
        return False

    _init_attempted = True
    api_key = get_api_key()

    if not api_key:
        logger.warning(
            "AEGIS LLM: No valid Gemini API key found. "
            "Set GEMINI_API_KEY in your .env file. "
            "Agents will use heuristic fallback mode."
        )
        return False

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        _gemini_client_initialized = True

        logger.info(
            "AEGIS LLM: Gemini client initialized successfully."
        )
        return True

    except Exception as e:
        logger.error(f"Could not configure Gemini client: {e}")
        return False


async def generate_text(
    prompt: str,
    model_name: Optional[str] = None,
    temperature: float = 0.2,
    system_instruction: Optional[str] = None
) -> Optional[str]:
    """
    Generate text using Gemini.
    Returns None on failure so callers can use heuristic fallback.
    """
    if not init_gemini():
        return None

    try:
        import google.generativeai as genai

        # Set GEMINI_MODEL in .env to a model supported by your API key.
        target_model = (
            model_name
            or os.getenv("GEMINI_MODEL")
            or "gemini-3.5-flash"
        )

        kwargs: Dict[str, Any] = {
            "model_name": target_model,
            "generation_config": {
                "temperature": temperature,
                "top_p": 0.95,
                "max_output_tokens": 2048,
            }
        }

        if system_instruction:
            kwargs["system_instruction"] = system_instruction

        model = genai.GenerativeModel(**kwargs)
        response = model.generate_content(prompt)

        if response and response.text:
            return response.text.strip()

        logger.warning("Gemini returned an empty response.")

    except Exception as e:
        logger.warning(
            "Gemini generation failed for the configured model: %s. "
            "Using heuristic fallback.", e
        )

    return None
