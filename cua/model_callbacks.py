from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.genai.types import Part
from typing import List

async def before_model_modifier(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> LlmResponse | None:
    """Modify LLM request to include artifact references for images."""
    for content in llm_request.contents:
        if not content.parts:
            continue

        modified_parts = []
        for idx, part in enumerate(content.parts):
            # Handle function response parts 
            if part.function_response:
                if part.function_response.name:
                    processed_parts = await _process_function_response_part(
                        part, callback_context
                    )
                else:
                    processed_parts = [part]
            # Default: keep part as-is
            else:
                processed_parts = [part]

            modified_parts.extend(processed_parts)

        content.parts = modified_parts


async def _process_function_response_part(
    part: Part, callback_context: CallbackContext
) -> List[Part]:
    """Process function response parts and append artifacts.

    Returns:
        List of parts including the original function response and artifact.
    """
    artifact_id = part.function_response.response.get("computer_screenshot_artifact_id")

    if not artifact_id:
        return [part]

    artifact = await callback_context.load_artifact(filename=artifact_id)

    return [
        part,  # Original function response
        Part(
            text=f"[Computer Screenshot Artifact] Below is the content of artifact ID : {artifact_id}"
        ),
        artifact,
    ]
