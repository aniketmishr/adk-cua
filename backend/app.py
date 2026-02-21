"""
FastAPI Application for Computer Use Agent
Provides streaming API endpoints for agent interactions
"""

import asyncio
import logging
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, ConfigDict

from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.genai import types

from engine.agent import get_agent_and_computer
from utils import _process_agent_event

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler('fastapi_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TaskRequest(BaseModel):
    """Request model for submitting a task to the agent"""

    task: str = Field(..., description="The task/query for the agent to execute", min_length=1)
    session_id: Optional[str] = Field(default="session_001", description="Session ID for conversation continuity")
    user_id: Optional[str] = Field(default="user_1", description="User identifier")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task": "Open Google and search for 'FastAPI documentation'",
                "session_id": "session_001",
                "user_id": "user_1"
            }
        }
    )


class AgentResponse(BaseModel):
    """Response model for agent events"""
    reasoning: Optional[str] = Field(
        default=None, 
        description="The reasoning before calling a tool"
    )
    tool_call: Optional[str] = Field(
        default=None, 
        description="Describes the tool call by the LLM, its name and args"
    )
    tool_response: Optional[str] = Field(
        default=None, 
        description="Tool response from agent"
    )
    final_answer: Optional[str] = Field(
        default=None, 
        description="The final answer for the query"
    )
    error: Optional[str] = Field(
        default=None, 
        description="Any error during execution"
    )


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    agent_initialized: bool


# Global State Management 

class AppState:
    """Manages the application's global state"""
    def __init__(self):
        self.session_service: Optional[InMemorySessionService] = None
        self.artifact_service: Optional[InMemoryArtifactService] = None
        self.runner: Optional[Runner] = None
        self.computer_instance = None
        self.app_name = "cua_app"
        self.initialized = False
    
    async def initialize(self):
        """Initialize agent, session services, and computer instance"""
        if self.initialized:
            logger.info("App already initialized, skipping...")
            return
        
        try:
            logger.info("Initializing application state...")
            
            # Initialize session and artifact services
            self.session_service = InMemorySessionService()
            self.artifact_service = InMemoryArtifactService()
            
            # Create agent and computer instance
            cua_agent, self.computer_instance = get_agent_and_computer()
            
            # Create runner
            self.runner = Runner(
                agent=cua_agent,
                app_name=self.app_name,
                session_service=self.session_service,
                artifact_service=self.artifact_service
            )
            
            # Initialize computer instance
            await self.computer_instance.__aenter__()
            
            self.initialized = True
            logger.info("Application state initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize application state: {e}", exc_info=True)
            raise
    
    async def cleanup(self):
        """Cleanup resources on shutdown"""
        logger.info("Cleaning up application state...")
        try:
            if self.runner:
                await self.runner.close()
            if self.computer_instance:
                await self.computer_instance.__aexit__(None, None, None)
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)


# Global app state
app_state = AppState()


# Lifespan Management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Application starting up...")
    await app_state.initialize()
    yield
    # Shutdown
    logger.info("Application shutting down...")
    await app_state.cleanup()


# FastAPI Application

app = FastAPI(
    title="Computer Use Agent API",
    description="API for controlling browser automation agent with streaming responses",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper Functions

async def get_or_create_session(user_id: str, session_id: str):
    """Get existing session or create a new one"""
    try:
        # Try to get existing session
        session = await app_state.session_service.get_session(
            app_name=app_state.app_name,
            user_id=user_id,
            session_id=session_id
        )
        if session==None: #### TODO(there is a better way to write this)
            raise ValueError(f"session_id: {session_id} not found.")
        logger.info(f"Retrieved existing session: {session_id}")
        return session
    except Exception:
        # Create new session if it doesn't exist
        session = await app_state.session_service.create_session(
            app_name=app_state.app_name,
            user_id=user_id,
            session_id=session_id
        )
        logger.info(f"Created new session: {session_id}")
        return session


async def stream_agent_responses(
    task: str,
    user_id: str,
    session_id: str
) -> AsyncGenerator[str, None]:
    """
    Generator function that streams agent responses in SSE format
    """
    try:
        # Ensure session exists
        await get_or_create_session(user_id, session_id)
        
        # Get current computer state (screenshot)
        current_computer_state = await app_state.computer_instance.current_state()
        
        # Prepare the user's message in ADK format
        content = types.Content(
            role='user',
            parts=[
                types.Part(
                    inline_data=types.Blob(
                        mime_type="image/png",
                        data=current_computer_state.screenshot
                    )
                ),
                types.Part(text=task)
            ]
        )
        
        # Stream agent execution
        async for event in app_state.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            # Process each event and yield responses
            for response in _process_agent_event(event):
                # Convert response to JSON and format as SSE
                response_json = response.model_dump_json()
                # ADD: Log each response
                logger.info(f"Streaming response: {response_json[:100]}...")
                yield f"data: {response_json}\n\n"
                # ADD: Small delay to ensure proper streaming
                await asyncio.sleep(0.01)
        
        # Send completion signal
        logger.info("Streaming completed, sending done signal")
        yield "data: {\"done\": true}\n\n"
        
    except Exception as e:
        logger.error(f"Error in stream_agent_responses: {e}", exc_info=True)
        error_response = AgentResponse(error=str(e))
        yield f"data: {error_response.model_dump_json()}\n\n"


# API Endpoints

@app.get("/", response_model=dict)
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Computer Use Agent API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "execute_task": "/api/execute (POST)",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns the current status of the application
    """
    return HealthResponse(
        status="healthy" if app_state.initialized else "initializing",
        message="Agent is ready" if app_state.initialized else "Agent is initializing",
        agent_initialized=app_state.initialized
    )


@app.post("/api/execute")
async def execute_task(request: TaskRequest):
    """Execute a task using the computer use agent"""
    
    if not app_state.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent is still initializing. Please try again in a moment."
        )
    
    logger.info(f"Received task: '{request.task}' for session {request.session_id}")
    
    return StreamingResponse(
        stream_agent_responses(
            task=request.task,
            user_id=request.user_id,
            session_id=request.session_id
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",  # CHANGED: Added no-transform
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Content-Type": "text/event-stream",  # ADD: Explicit content type
            "Transfer-Encoding": "chunked"  # ADD: Chunked encoding
        }
    )

@app.post("/api/reset-session")
async def reset_session(session_id: str = "session_001"):
    """
    Reset a specific session
    Useful for starting fresh conversations
    """
    try:
        # This will create a new session, effectively resetting it
        session = await app_state.session_service.create_session(
            app_name=app_state.app_name,
            user_id="user_1",
            session_id=session_id
        )
        logger.info(f"Session reset: {session_id}")
        return {"message": f"Session {session_id} has been reset", "session_id": session_id}
    except Exception as e:
        logger.error(f"Error resetting session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset session: {str(e)}"
        )


# Error Handlers

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "error": "Internal server error",
        "detail": str(exc)
    }
