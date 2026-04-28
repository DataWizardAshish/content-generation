import openai
from src.config import OPENAI_API_KEY, MODEL
from src.logger import get_logger

logger = get_logger("llm_client")

_client: openai.OpenAI | None = None


def get_client() -> openai.OpenAI:
    global _client
    if _client is None:
        _client = openai.OpenAI(api_key=OPENAI_API_KEY)
    return _client


def call_responses(
    prompt: str,
    system: str = "",
    schema: dict | None = None,
) -> str:
    """Responses API call. Passes schema as Structured Output when provided."""
    client = get_client()
    input_messages = []
    if system:
        input_messages.append({"role": "system", "content": system})
    input_messages.append({"role": "user", "content": prompt})

    text_config: dict = {"verbosity": "low"}
    if schema is not None:
        text_config["format"] = {
            "type": "json_schema",
            "name": "output",
            "schema": schema,
            "strict": True,
        }

    logger.info("=== RESPONSES API [model=%s] ===\n%s", MODEL, prompt[:500] + ("..." if len(prompt) > 500 else ""))
    try:
        response = client.responses.create(
            model=MODEL,
            input=input_messages,
            text=text_config,
        )
        raw = response.output_text or ""
        logger.info("=== RESPONSE ===\n%s", raw[:1000] + ("..." if len(raw) > 1000 else ""))
        return raw
    except openai.APIError as e:
        logger.error("Responses API error: %s", e)
        raise


def call_llm(prompt: str, system: str = "") -> str:
    """Generation call with Structured Output."""
    from src.schemas import QUESTIONS_SCHEMA
    return call_responses(prompt, system, schema=QUESTIONS_SCHEMA)
