import asyncio

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.rule import Rule
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts
from engine.agent import get_agent_and_computer
from utils import _process_agent_event
import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

console = Console()

# Define constants for identifying the interaction context
APP_NAME = "cua_app"
USER_ID = "user_1"
SESSION_ID = "session_001" # Using a fixed ID for simplicity

async def setup_agent_conversation(): 
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    session = await session_service.create_session(
        app_name=APP_NAME, 
        user_id=USER_ID, 
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")
    
    cua_agent, computer_instance = get_agent_and_computer(litellm_model="openai/gpt-5-mini")

    runner = Runner(
        agent = cua_agent,
        app_name=APP_NAME,
        session_service=session_service, 
        artifact_service=artifact_service
    )
    print(f"Runner created for agent '{runner.agent.name}'.")
    return session, runner, computer_instance


async def call_agent_async(query: str, computer_state: bytes ,runner, user_id, session_id): 
    """Sends a query to the agent and yeilds model response."""
    # Prepare the user's message in ADK format
    content = types.Content(role='user', parts = [types.Part(inline_data=types.Blob(mime_type="image/png",data=computer_state)), types.Part(text=query)])

    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message = content): 
        for r in _process_agent_event(event): 
            yield r

async def main():
    session, runner, computer_instance = await setup_agent_conversation()

    console.print(
        Panel.fit(
            "[bold cyan]Computer Use Agent[/bold cyan]\nType your task below",
            border_style="cyan"
        )
    )

    async with computer_instance as c: 
        while True: 
            console.print("[dim]Type /bye to exit conversation[/dim]")
            task: str = console.input("[bold green][user] >>> [/bold green]")
            if task.strip().lower() == '/bye': 
                await runner.close()
                break
            current_computer_state = await c.current_state()
            console.print(Rule("[bold yellow]Agent Execution[/bold yellow]"))

            async for response in call_agent_async(
                query=task,
                computer_state = current_computer_state.screenshot,
                runner=runner,
                user_id=USER_ID,
                session_id=SESSION_ID,
            ):
                # Reasoning 
                if response.reasoning:
                    console.print(
                        Panel(
                            Text(response.reasoning, style="dim italic"),
                            title="🧠 Reasoning",
                            border_style="magenta",
                        )
                    )

                # Tool call
                if response.tool_call:
                    console.print(
                        Panel(
                            Markdown(f"\n{response.tool_call}`"),
                            title="🛠 Tool Call",
                            border_style="blue",
                        )
                    )

                # Final answer
                if response.final_answer:
                    console.print(
                        Panel(
                            Markdown(response.final_answer),
                            title="✅ Final Answer",
                            border_style="green",
                        )
                    )

                # Error
                if response.error:
                    console.print(
                        Panel(
                            Text(response.error, style="bold red"),
                            title="❌ Error",
                            border_style="red",
                        )
                    )

            console.print(Rule("[bold green]Done[/bold green]"))

if __name__=='__main__': 
    asyncio.run(main())