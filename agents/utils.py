import json
import re
from typing import Any, Dict, Optional


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON from text, handling various formats:
    - Markdown code blocks (```json ... ```)
    - Plain JSON
    - Multiple JSON objects (returns the first valid one)

    Args:
        text: The text containing JSON

    Returns:
        Parsed JSON dict or None if no valid JSON found
    """
    if not text or not text.strip():
        return None

    content = text.strip()

    json_patterns = [
        r"```json\s*(\{.*?\})\s*```",  # ```json {json} ```
        r"```\s*(\{.*?\})\s*```",  # ``` {json} ```
        r"`(\{.*?\})`",  # `{json}`
    ]

    for pattern in json_patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue

    json_objects = re.findall(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", content)

    for json_str in json_objects:
        try:
            return json.loads(json_str.strip())
        except json.JSONDecodeError:
            continue

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None
