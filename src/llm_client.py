import openai
from src.config import OPENAI_API_KEY, MODEL, MAX_TOKENS, TEMPERATURE
from src.logger import get_logger

logger = get_logger("llm_client")

_client: openai.OpenAI | None = None


def get_client() -> openai.OpenAI:
    global _client
    if _client is None:
        _client = openai.OpenAI(api_key=OPENAI_API_KEY)
    return _client


def call_llm_text(prompt: str, system: str = "") -> str:
    """Call LLM without json_object constraint — for validation which returns JSON arrays."""
    client = get_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    logger.info("=== VALIDATION PROMPT [model=%s] ===\n%s", MODEL, prompt[:500] + ("..." if len(prompt) > 500 else ""))
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0,
            max_tokens=MAX_TOKENS,
        )
        raw = response.choices[0].message.content or ""
        logger.info("=== VALIDATION RESPONSE ===\n%s", raw[:1000] + ("..." if len(raw) > 1000 else ""))
        return raw
    except openai.APIError as e:
        logger.error("LLM API error: %s", e)
        raise


def call_llm(prompt: str, system: str = "") -> str:
    client = get_client()

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    logger.info("=== PROMPT SENT TO LLM [model=%s] ===\n%s", MODEL, prompt[:500] + ("..." if len(prompt) > 500 else ""))

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content or ""
        logger.info("=== RAW LLM RESPONSE ===\n%s", raw[:1000] + ("..." if len(raw) > 1000 else ""))
        return raw
    except openai.APIError as e:
        logger.error("LLM API error: %s", e)
        raise
