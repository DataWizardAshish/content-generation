QUESTIONS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "scene_setup": {"type": "string"},
                    "question": {"type": "string"},
                    "option_a": {"type": "string"},
                    "option_b": {"type": "string"},
                    "option_c": {"type": "string"},
                    "option_d": {"type": "string"},
                    "correct_answer": {"type": "string", "enum": ["A", "B", "C", "D"]},
                    "source_quote": {"type": "string"},
                    "narrative_continuation": {"type": "string"},
                    "deep_context": {"type": "string"},
                    "forward_hook": {"type": "string"},
                    "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]},
                    "topic": {"type": "string"},
                    "story_phase": {
                        "type": "string",
                        "enum": [
                            "Early Life of Rama",
                            "Exile Phase",
                            "Sita Haran",
                            "Search for Sita",
                            "Lanka War",
                            "Return and Reunion",
                            "Other",
                        ],
                    },
                    "narrative_arc": {"type": "string"},
                },
                "required": [
                    "scene_setup", "question",
                    "option_a", "option_b", "option_c", "option_d",
                    "correct_answer", "source_quote",
                    "narrative_continuation", "deep_context", "forward_hook",
                    "difficulty", "topic", "story_phase", "narrative_arc",
                ],
            },
        }
    },
    "required": ["questions"],
}

VALIDATION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "question": {"type": "string"},
                    "status": {"type": "string", "enum": ["approved", "rejected"]},
                    "reason": {"type": "string"},
                    "supporting_text": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                    "confidence_score": {"type": "integer"},
                },
                "required": ["question", "status", "reason", "supporting_text", "confidence_score"],
            },
        }
    },
    "required": ["results"],
}

CRITIQUE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "question": {"type": "string"},
                    "engagement_score": {"type": "integer"},
                    "enrichment_score": {"type": "integer"},
                    "narrative_flow_score": {"type": "integer"},
                    "engagement_reason": {"type": "string"},
                    "is_daily_insight_candidate": {"type": "boolean"},
                    "improvement_suggestion": {"anyOf": [{"type": "string"}, {"type": "null"}]},
                },
                "required": [
                    "question", "engagement_score", "enrichment_score", "narrative_flow_score",
                    "engagement_reason", "is_daily_insight_candidate", "improvement_suggestion",
                ],
            },
        }
    },
    "required": ["results"],
}
