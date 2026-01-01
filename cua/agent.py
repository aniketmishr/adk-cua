
import os
import tempfile

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from .browser_computer import PlaywrightComputer
from .model_agnostic_toolset import ModelAgnosticComputerToolSet
from .model_callbacks import before_model_modifier
from .prompt import COMPUTER_USE_SYSTEM_PROMPT
from dotenv import load_dotenv

load_dotenv()

# Define user_data_dir path for persistent browser session
profile_name = 'browser_profile_for_adk'
profile_path = os.path.join(tempfile.gettempdir(), profile_name)
os.makedirs(profile_path, exist_ok=True)

# Initialize the Playwright computer instance
computer_with_profile = PlaywrightComputer(
    screen_size=(936, 684),
    user_data_dir=profile_path,
    highlight_mouse=True,  # Visual feedback for debugging
)

root_agent = None

try: 
    # Create the model-agnostic agent with LiteLLM support
    root_agent = Agent(

        model=LiteLlm('openai/gpt-5-mini'),  # Change this to your preferred model
        
        name='computer_use_agent',
        
        description=(
            'A model-agnostic computer use agent that can operate a browser to complete '
            'user tasks. Works with any LLM through LiteLLM integration.'
        ),
        
        instruction=COMPUTER_USE_SYSTEM_PROMPT,
        
        before_model_callback=before_model_modifier,

        # Use the model-agnostic toolset instead of Gemini-specific one
        tools=[ModelAgnosticComputerToolSet(
            computer=computer_with_profile,
            virtual_screen_size=(1000, 1000)  # Standard coordinate space for LLMs
        )],
    )
    print(f"✅ Agent '{root_agent.name}' created using model '{root_agent.model}'.")
except Exception as e:
    print(f"❌ Could not create {root_agent.name}. Check API Key ({root_agent.model}). Error: {e}")
