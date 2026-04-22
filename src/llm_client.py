import anthropic
from src.config import ANTHROPIC_API_KEY, MODEL, MAX_TOKENS
from src.logger import get_logger

logger = get_logger("llm_client")

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def call_claude(prompt: str, system: str = "") -> str:
    client = get_client()
    messages = [{"role": "user", "content": prompt}]

    logger.info("=== PROMPT SENT TO LLM ===\n%s", prompt[:500] + ("..." if len(prompt) > 500 else ""))

    kwargs = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": messages,
    }
    if system:
        kwargs["system"] = system

    try:
        response = client.messages.create(**kwargs)
        raw = response.content[0].text
        logger.info("=== RAW LLM RESPONSE ===\n%s", raw[:1000] + ("..." if len(raw) > 1000 else ""))
        return raw
    except anthropic.APIError as e:
        logger.error("LLM API error: %s", e)
        raise
