from opik.integrations.adk import OpikTracer
from google.genai.types import Part, FileData, Content
import opik
from dotenv import load_dotenv
from utils import png_bytes_to_data_uri
import os

load_dotenv()

# Configure with your Opik API key
opik.configure(
    api_key=os.getenv("OPIK_API_KEY")
)

class CustomOpikTracer(OpikTracer):
    def before_model_callback(self, callback_context, llm_request, *args, **kwargs):
        modified_llm_request = llm_request.model_copy()
        modified_contents = []
        for content in modified_llm_request.contents:
            modified_content = Content(parts = list(), role=content.role)
            for idx, part in enumerate(content.parts):
                if part.inline_data!=None:
                    modified_content.parts.append(Part(file_data=FileData(file_uri = png_bytes_to_data_uri(part.inline_data.data), mime_type="image/png")))
                else:
                    modified_content.parts.append(part)
            modified_contents.append(modified_content)

        # set contents of modified_llm_request with updated contents
        modified_llm_request.contents = modified_contents
        return super().before_model_callback(callback_context, modified_llm_request, *args, **kwargs)
