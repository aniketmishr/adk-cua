import asyncio
import json
import litellm
from typing import Tuple
from omniparserclient import parse_ui_from_image_bytes
from opik import track, opik_context
from utils import png_bytes_to_data_uri
from config import settings

MODEL: str = settings.grounding.model

GROUNDING_SYSTEM_PROMPT: str = """
You are a Computer Use Agent.

You are given:
1. A UI screenshot with elements labeled by numeric IDs.
2. A textual list of detected UI elements. Each element may include:
   - id
   - type (text or icon) 
   - content (only for text label)
   - center coordinate [x, y] (may be missing for some elements)

Your task:
- Understand the user instruction.
- Identify the UI element the user wants to interact with.
- Output ONLY the coordinate [x, y] of the point to click.

Rules:
- If the desired element has an explicit coordinate in the UI text, output that exact coordinate.
- If the desired element does NOT have a coordinate in the UI text:
  - Use the labeled image and spatial relationships between elements
  - Infer the most likely click coordinate based on visual position (e.g., top-right, near another element, alignment, grouping).
- Use the image as the primary source of spatial information when coordinates are missing.
- Do NOT output the element ID.
- Do NOT explain your reasoning.
- Do NOT output anything except a valid JSON in the form:
  {
  "center" : [x,y]
  }
"""

class VisualGroundingError(Exception):
    """Raised when visual grounding fails or returns invalid output."""


@track(ignore_arguments=["image_bytes"])
async def locate_visual_element(
    image_bytes: bytes,
    visual_description: str,
) -> Tuple[float, float]:
    """
    Resolve the screen coordinates of a visually described UI element
    by grounding a natural-language visual description against the UI image.
    """
    opik_context.update_current_span(
        input = {"image_base64": png_bytes_to_data_uri(image_bytes)}, 
    )
    if not image_bytes:
        raise ValueError("image_bytes must not be empty")

    if not visual_description:
        raise ValueError("visual_description must not be empty")
    
    assert litellm.supports_vision(model=MODEL) == True, f"Provided MODEL : {MODEL} doesn't support vision capability "

    # Apply UI parsing / annotation
    try:
        annotated_image_b64, ui_elements = await parse_ui_from_image_bytes(image_bytes)
    except Exception as exc:
        raise VisualGroundingError(
            "Failed to parse UI image before visual grounding"
        ) from exc

    # Call grounding model via LiteLLM
    try:
        response = await call_grounding_model(annotated_image_b64, ui_elements, visual_description)
    except Exception as exc:
        raise VisualGroundingError(
            "Visual grounding model call failed via LiteLLM"
        ) from exc

    # Extract model output text
    try:
        output_text = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise VisualGroundingError(
            "Unexpected response structure from grounding model"
        ) from exc

    # Parse and validate JSON output
    try:
        result = json.loads(output_text)
    except json.JSONDecodeError as exc:
        raise VisualGroundingError(
            f"Model output is not valid JSON: {output_text}"
        ) from exc

    if not isinstance(result, dict):
        raise VisualGroundingError(
            "Model output JSON must be an object with a 'center' field"
        )

    center = result.get("center")

    if (
        not isinstance(center, list)
        or len(center) != 2
        or not all(isinstance(v, (int, float)) for v in center)
    ):
        raise VisualGroundingError(
            "Model output must be of the form: { \"center\": [x, y] }"
        )

    return float(center[0]), float(center[1])

@track
async def call_grounding_model(annotated_image_b64:str, ui_elements:list[dict], visual_description:str):
    response = await litellm.acompletion(
            model=MODEL,
            api_key=settings.grounding.api_key.get_secret_value(),
            messages=[
                {
                    "role": "system",
                    "content": GROUNDING_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url" : annotated_image_b64,
                            }
                        },
                        {
                            "type": "text",
                            "text": (
                                "UI ELEMENTS:\n"
                                f"{ui_elements}\n\n"
                                "INSTRUCTION:\n"
                                f"Target visual description: {visual_description}"
                            ),
                        },
                    ],
                },
            ],
        )
    
    cost = litellm.completion_cost(
        completion_response=response
    )
    opik_context.update_current_span(
        total_cost=cost,
        model = MODEL
    )
    return response