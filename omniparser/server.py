"""
Omniparser server entry point.

This module starts the Omniparser API server.
To run locally from the project root:
    python -m omniparser.server
"""

from typing import List, Tuple
from som.models import UIElement, BoundingBox
from som import OmniParser
from pydantic import BaseModel
from fastapi import FastAPI
import time
import uvicorn

def get_bbox_center(bbox: BoundingBox, screen_size : Tuple[float, float]) -> Tuple[int, int]: 
    img_width, img_height = screen_size
    # Scale box coordinates
    x1,y1,x2,y2 = bbox.coordinates
    x1 = x1 * img_width
    y1 = y1 * img_height
    x2 = x2 * img_width
    y2 = y2 * img_height
    # find center of bbox
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return (int(center_x), int(center_y))

def process_image_elements(elements: List[UIElement], screen_size) : 
    processed_elements = []
    for element in elements: 
        if element.type == "text": 
            processed_elements.append(
                {
                    "id": element.id,
                    "type" : "text",
                    "content": element.content, 
                    "center" : get_bbox_center(element.bbox, screen_size)
                }
            )
        elif element.type == "icon": 
            processed_elements.append(
                {
                    "id": element.id,
                    "type" : "icon",
                    "center" : get_bbox_center(element.bbox, screen_size)
                }
            )
        else: 
            pass 
    return processed_elements

app = FastAPI()

# initialize omniparser
parser = OmniParser()

class ParseRequest(BaseModel):
    base64_image: str

@app.post("/parse")
async def parse(parse_request: ParseRequest):
    print('start parsing...')
    start = time.time()
    # Parse screenshot
    parse_result = parser.parse(screenshot_data=parse_request.base64_image)
    latency = time.time() - start
    print(f"time: {latency:0.3f} s")
    return {"som_image_base64": parse_result.annotated_image_base64, "parsed_content_list": process_image_elements(parse_result.elements, (parse_result.width, parse_result.height)), 'latency': latency}

@app.get("/probe/")
async def root():
    return {"message": "Omniparser API ready"}

@app.get("/health")
async def health():
    return {"status": "ok"}
