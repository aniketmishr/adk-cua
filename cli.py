import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts
from cua.agent import root_agent
import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

# Define constants for identifying the interaction context
APP_NAME = "cua_app"
USER_ID = "user_1"
SESSION_ID = "session_001" # Using a fixed ID for simplicity

async def setup_session_and_runner(): 
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    session = await session_service.create_session(
        app_name=APP_NAME, 
        user_id=USER_ID, 
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")
    runner = Runner(
        agent = root_agent,
        app_name=APP_NAME,
        session_service=session_service, 
        artifact_service=artifact_service
    )
    print(f"Runner created for agent '{runner.agent.name}'.")
    return session, runner


async def call_agent_async(query: str, runner, user_id, session_id): 
    """Sends a query to the agent and prints the final response."""
    # Prepare the user's message in ADK format
    content = types.Content(role='user', parts = [types.Part(text=query)])

    final_response_text = "Agent did not produce a final response." # Default

    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message = content): 
        # print(event)
        if event.is_final_response(): 
            if event.content and event.content.parts: 
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate: # Handle potential errors/escalations
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break

    return final_response_text

async def main(): 
    session, runner = await setup_session_and_runner()
    task: str = input("[user] >>> ")
    response = await call_agent_async(query=task, runner=runner, user_id=USER_ID, session_id=SESSION_ID)
    print('[assistant] >>> ', response) 

if __name__=='__main__': 
    asyncio.run(main())