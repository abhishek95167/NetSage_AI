"""
NetSage AI — OpenAI-Compatible AI Provider
Sends structured prompts to OpenAI-compatible APIs and validates responses.
"""

import json
import os
import httpx
from typing import Dict, Optional
from ai.schemas.diagnosis_schema import validate_diagnosis


DIAGNOSIS_PROMPT_TEMPLATE = """You are NetSage AI, an expert Cisco network troubleshooting assistant.

Analyze the following network troubleshooting case and provide a structured diagnosis.

## Symptom
{symptom}

## Topology Notes
{topology_notes}

## Show Command Output
```
{show_outputs}
```

## Instructions
1. Analyze the symptom, topology, and show command output carefully.
2. Identify the most likely root cause based ONLY on the provided evidence.
3. Do NOT invent or fabricate any evidence not present in the show output.
4. If evidence is insufficient, explicitly state this and recommend the next command.
5. Return your diagnosis as a JSON object with this exact schema:

{{
  "root_cause": "Clear description of the most likely root cause",
  "confidence": 85,
  "osi_layer": "Layer X",
  "evidence": ["Specific evidence from show output"],
  "next_command": "show command to run next",
  "fix_steps": ["Step 1", "Step 2"],
  "alternative_causes": ["Alt cause if confidence < 90%"]
}}

Return ONLY the JSON object. No additional text before or after."""


async def get_openai_diagnosis(
    symptom: str,
    topology_notes: str,
    show_outputs: str,
    expected_fault: str = "",
    api_key: Optional[str] = None,
    base_url: str = "https://api.openai.com/v1",
    model: str = "gpt-4o-mini"
) -> Dict:
    """
    Send a diagnosis request to an OpenAI-compatible API.
    Returns validated diagnosis dict.
    """
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY", "")

    if not api_key:
        raise ValueError("No API key provided. Set OPENAI_API_KEY environment variable.")

    prompt = DIAGNOSIS_PROMPT_TEMPLATE.format(
        symptom=symptom,
        topology_notes=topology_notes,
        show_outputs=show_outputs
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are NetSage AI, a Cisco network troubleshooting expert. Always respond with valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 1500
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")

        result = response.json()
        content = result["choices"][0]["message"]["content"].strip()

        # Try to parse JSON from the response
        # Handle potential markdown code blocks
        if content.startswith("```"):
            lines = content.split("\n")
            json_lines = []
            in_block = False
            for line in lines:
                if line.startswith("```") and not in_block:
                    in_block = True
                    continue
                elif line.startswith("```") and in_block:
                    break
                elif in_block:
                    json_lines.append(line)
            content = "\n".join(json_lines)

        try:
            diagnosis = json.loads(content)
        except json.JSONDecodeError:
            raise Exception(f"AI response was not valid JSON: {content[:200]}")

        # Validate against schema
        is_valid, errors = validate_diagnosis(diagnosis)
        if not is_valid:
            raise Exception(f"AI diagnosis failed schema validation: {errors}")

        # Ensure confidence is int
        diagnosis["confidence"] = int(diagnosis["confidence"])

        return diagnosis
