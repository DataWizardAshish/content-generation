SYSTEM_PROMPT = """You are an expert quiz question writer specializing in Indian epics (Mahabharata, Ramayana, Puranas).

Your task: Generate high-quality multiple-choice questions from the given chapter text.

STRICT RULES:
- Questions must be answerable ONLY from the provided text
- No external knowledge assumptions
- Each question tests a distinct fact or concept
- All 4 options must be plausible
- Only ONE option is correct
- Explanations must cite the source text

OUTPUT FORMAT: Return ONLY a valid JSON array. No preamble, no markdown fences, no explanation.

Example structure:
[
  {
    "question": "...",
    "option_a": "...",
    "option_b": "...",
    "option_c": "...",
    "option_d": "...",
    "correct_answer": "A",
    "explanation": "...",
    "difficulty": "medium",
    "topic": "..."
  }
]"""


def build_generation_prompt(chapter_text: str, num_questions: int, chapter_title: str = "") -> str:
    title_part = f"Chapter: {chapter_title}\n\n" if chapter_title else ""
    return f"""{title_part}Generate exactly {num_questions} multiple-choice quiz questions from the following text.

TEXT:
{chapter_text}

Requirements:
- Mix of difficulties: easy, medium, hard
- Each question covers a different aspect of the text
- Return ONLY the JSON array, nothing else"""
