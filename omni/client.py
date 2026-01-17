import asyncio
import httpx
import base64
from typing import Tuple, List

API_URL = "http://127.0.0.1:8000/parse/"


def image_bytes_to_base64(image_bytes: bytes) -> str:
    """
    Convert image bytes to a base64-encoded string.

    :param image_bytes: Raw image bytes
    :return: Base64-encoded string
    """
    return base64.b64encode(image_bytes).decode("utf-8")


class UIParsingError(Exception):
    """Raised when UI parsing or response validation fails."""


async def parse_ui_from_image_bytes(img_bytes: bytes) -> Tuple[str, List[dict]]:
    """
    Parse UI elements from image bytes and return an annotated image (base64)
    along with detected UI elements metadata.
    """
    if not img_bytes:
        raise ValueError("img_bytes must not be empty")

    img_b64 = image_bytes_to_base64(img_bytes)

    payload = {
        "base64_image": img_b64
    }

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(40.0)) as client:
            response = await client.post(API_URL, json=payload)
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise UIParsingError("Request to UI parsing service timed out") from exc
    except httpx.HTTPStatusError as exc:
        raise UIParsingError(
            f"UI parsing service returned HTTP {exc.response.status_code}"
        ) from exc
    except httpx.RequestError as exc:
        raise UIParsingError("Failed to connect to UI parsing service") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise UIParsingError("Response is not valid JSON") from exc

    annotated_image_b64 = data.get("som_image_base64")
    ui_elements = data.get("parsed_content_list")

    if not annotated_image_b64:
        raise UIParsingError(
            "UI parsing response did not include an annotated image (som_image_base64)"
        )

    if ui_elements is None:
        raise UIParsingError(
            "UI parsing response did not include parsed UI elements (parsed_content_list)"
        )

    return annotated_image_b64, ui_elements

