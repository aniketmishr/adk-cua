
import os
import tempfile
from typing import Tuple

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from computer.browser_computer import PlaywrightComputer
from computer.base_computer import BaseComputer
from .toolset import ComputerToolSet
from .model_callbacks import before_model_modifier
from .prompt import COMPUTER_USE_SYSTEM_PROMPT
from dotenv import load_dotenv
from custom_opik_tracer import CustomOpikTracer
load_dotenv()

SCREEN_SIZE = (936, 684)

# Configure Opik tracer
opik_tracer = CustomOpikTracer(
    tags=["v1","omni", "single-agent"],
    metadata={
        "environment": "playwright",
        "env_screen_size": str(SCREEN_SIZE),
        "framework": "google-adk",
        "version": "1"
    },
    project_name="adk-cua"
)

def get_agent_and_computer(litellm_model = 'openai/gpt-5-mini', screen_size = SCREEN_SIZE) -> Tuple[Agent, BaseComputer]: 
    # Create Computer instance

    ## Define user_data_dir path for persistent browser session
    profile_name = 'browser_profile_for_adk'
    profile_path = os.path.join(tempfile.gettempdir(), profile_name)
    os.makedirs(profile_path, exist_ok=True)

    ## Initialize the Playwright computer instance
    computer_with_profile = PlaywrightComputer(
        screen_size=SCREEN_SIZE,
        user_data_dir=profile_path,
        highlight_mouse=True,  # Visual feedback for debugging
        )
    
    # Create Agent instance
    root_agent = None

    try: 
        # Create the computer agent with LiteLLM support
        root_agent = Agent(

            model=LiteLlm(litellm_model), 
            
            name='computer_use_agent',
            
            description=(
                'A computer use agent that can operate a browser to complete '
                'user tasks. Works with any LLM.'
            ),

            instruction=COMPUTER_USE_SYSTEM_PROMPT,
            
            before_agent_callback=opik_tracer.before_agent_callback,
            after_agent_callback=opik_tracer.after_agent_callback,
            before_model_callback=[before_model_modifier,opik_tracer.before_model_callback],
            after_model_callback=opik_tracer.after_model_callback,
            before_tool_callback=opik_tracer.before_tool_callback,
            after_tool_callback=opik_tracer.after_tool_callback,

            tools=[ComputerToolSet(
                computer=computer_with_profile,
            )],
        )
        print(f"✅ Agent '{root_agent.name}' created using model '{root_agent.model}'.")
    except Exception as e:
        raise ValueError(f"❌ Could not create {root_agent.name}. Check API Key ({root_agent.model}). Error: {e}")

    return (root_agent, computer_with_profile)
        

root_agent, playwright_computer = get_agent_and_computer()
    
