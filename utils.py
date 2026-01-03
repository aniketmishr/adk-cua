from typing import List, Optional
from google.genai.types import Part
from google.adk.events import Event
from pydantic import BaseModel, Field
import json

class AgentResponse(BaseModel): 
     reasoning : Optional[str] = Field(
          default=None, 
          description="The reasoning before calling a tool"
     )
     tool_call : Optional[str] = Field(
          default=None, 
          description="Describes the tool call by the LLM, it's name and args."
     )
     tool_response : Optional[str] = Field(
          default=None, 
          description="Tool response from agent, dict[str, Any]"
     )
     final_answer : Optional[str] = Field(
          default=None, 
          description="The final answer for the query"
     )
     error : Optional[str] = Field(
          default=None, 
          description="Any error during execution"
     )

def _process_agent_event(event: Event) -> List[AgentResponse]:
     "Process Parts from event and return List of AgentResponse"
     responses = []
     if event.is_final_response(): 
          if event.content and event.content.parts: 
               responses.append(AgentResponse(final_answer=event.content.parts[0].text))
          elif event.actions and event.actions.escalate: # Handle potential errors/escalations
               responses.append(AgentResponse(error = f"Agent escalated: {event.error_message or 'No specific message.'}"))
     else:
          if event.content and event.content.parts: 
               for part in event.content.parts:
                    if ("text" in part.model_fields_set):
                         responses.append(AgentResponse(reasoning=part.text))
                    elif ("function_call" in part.model_fields_set):
                         responses.append(AgentResponse(tool_call=f"Tool Name : {part.function_call.name} \nTool Args : {part.function_call.args}"))
                    elif ("function_response" in part.model_fields_set):
                         responses.append(AgentResponse(tool_response=json.dumps(part.function_response.response, indent=3)))
                    else:
                         continue

     return responses

