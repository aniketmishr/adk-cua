from __future__ import annotations

import logging
from typing import Any, Callable, Optional
from google.genai import types
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.models.llm_request import LlmRequest
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_context import ToolContext
from computer.base_computer import BaseComputer, ComputerState

logger = logging.getLogger("google_adk." + __name__)

# Methods that should be excluded when creating tools from BaseComputer methods
EXCLUDED_METHODS = {"screen_size", "environment", "close", "initialize", "current_state"}


class ModelAgnosticComputerTool(FunctionTool):
    """A model-agnostic tool that wraps computer control functions.
    
    This tool normalizes coordinates and formats output for any LLM model,
    not just Gemini's computer use API.
    """

    def __init__(
        self,
        *,
        func: Callable[..., Any],
        screen_size: tuple[int, int],
    ):
        super().__init__(func=func)
        self._screen_size = screen_size

        # Validate screen size
        if not isinstance(screen_size, tuple) or len(screen_size) != 2:
            raise ValueError("screen_size must be a tuple of (width, height)")
        if screen_size[0] <= 0 or screen_size[1] <= 0:
            raise ValueError("screen_size dimensions must be positive")


    async def run_async(self, *, args: dict[str, Any], tool_context: ToolContext) -> dict[str, str]:
        """Run the computer control function with normalized coordinates."""
        
        try:
            # Execute the actual computer control function
            result = await super().run_async(args=args, tool_context=tool_context)

            # Process the result if it's a ComputerState
            if isinstance(result, ComputerState):
                # save screenshot in result as artifact
                # TODO('check for result.screenshot is bytes')
                image_part = types.Part.from_bytes(data = result.screenshot, mime_type='image/png')
                artifact_id = f'computer_screenshot_{tool_context.function_call_id}.png'
                await tool_context.save_artifact(filename=artifact_id, artifact=image_part)
                return {
                    "status": "success",
                    "computer_screenshot_artifact_id": artifact_id,
                    "url": result.url,
                    "message": f"Action completed successfully. Current URL: {result.url}"
                }
            else:
                return result

        except Exception as e:
            logger.error("Error in ModelAgnosticComputerTool.run_async: %s", e)
            return {
                "status": "error",
                "error": str(e),
                "message": f"Action failed: {str(e)}"
            }


class ModelAgnosticComputerToolSet(BaseToolset):
    """A model-agnostic toolset for computer control that works with any LLM via LiteLLM.
    
    Unlike the Gemini-specific ComputerUseToolset, this toolset creates standard
    function tools that can be used with any model through LiteLLM.
    """

    def __init__(
        self,
        *,
        computer: BaseComputer,
    ):
        """Initialize the model-agnostic computer toolset.
        
        Args:
            computer: The BaseComputer instance to control
        """
        super().__init__()
        self._computer = computer
        self._initialized = False
        self._tools = None

    async def _ensure_initialized(self) -> None:
        """Ensure the computer is initialized before use."""
        if not self._initialized:
            await self._computer.initialize()
            self._initialized = True

    async def get_tools(
        self,
        readonly_context: Optional[ReadonlyContext] = None,
    ) -> list[ModelAgnosticComputerTool]:
        """Get all computer control tools as standard function tools."""
        
        if self._tools:
            return self._tools
            
        await self._ensure_initialized()
        
        # Get screen size for tool configuration
        screen_size = await self._computer.screen_size()
        
        # Get all methods defined in BaseComputer abstract base class
        computer_methods = []
        
        for method_name in dir(BaseComputer):
            # Skip private methods
            if method_name.startswith("_"):
                continue
                
            # Skip excluded methods
            if method_name in EXCLUDED_METHODS:
                continue
                
            # Check if it's a method defined in BaseComputer class
            attr = getattr(BaseComputer, method_name, None)
            if attr is not None and callable(attr):
                # Get the corresponding method from the concrete instance
                instance_method = getattr(self._computer, method_name)
                computer_methods.append(instance_method)
        
        # Create ModelAgnosticComputerTool instances for each method
        self._tools = [
            ModelAgnosticComputerTool(
                func=method,
                screen_size=screen_size,
            )
            for method in computer_methods
        ]
        
        logger.info(f"Created {len(self._tools)} model-agnostic computer tools")
        return self._tools

    async def close(self) -> None:
        """Close the computer instance."""
        await self._computer.close()

    async def process_llm_request(
        self, *, tool_context: ToolContext, llm_request: LlmRequest
    ) -> None:
        """Add tools to the LLM request in a model-agnostic way.
        
        This method adds standard function tools that work with any LLM,
        not just Gemini's computer use API.
        """
        try:
            # Ensure tools are created
            if not self._tools:
                await self.get_tools()
            
            # Add each tool to the tools dictionary
            for tool in self._tools:
                llm_request.tools_dict[tool.name] = tool
                logger.debug(f"Added model-agnostic tool: {tool.name}")
            
            logger.info(f"Added {len(self._tools)} tools to LLM request for model-agnostic usage")
            
        except Exception as e:
            logger.error("Error in ModelAgnosticComputerToolSet.process_llm_request: %s", e)
            raise