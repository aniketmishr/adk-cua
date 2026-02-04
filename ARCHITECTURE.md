# Architecture

This document describes the core architecture and design decisions behind the **Computer Use Agent (CUA)**.  
Only the components essential to understanding how the system works are included.

---

## High-Level Design

- **Single-agent architecture** is used for the initial version to keep the system simple and easier to reason about.
- The agent performs **tool reasoning and tool execution in a single step** to reduce context bloat.
- Instead of predicting raw pixel coordinates, the agent uses **semantic descriptions of UI elements**, which are later grounded to screen locations.

---

## Core Components

The project is organized into three main directories:

```

computer/
engine/
omni/

````

---

## `computer/`

Responsible for programmatic control of a computer environment.

- **`BaseComputer`**
  - Abstract interface for a controllable computer.
  - Can be extended to support other environments (Linux containers, Android, etc.).

- **`PlaywrightComputer`**
  - Concrete implementation for controlling a browser using Playwright.

**Key design decision**  
The agent does **not** output raw pixel coordinates.  
It only describes the UI element it wants to interact with. Localization is handled separately by the grounding logic.

---

## `engine/`

Contains the agent logic and supporting components.  
The directory is named `engine` (not `agent`) to avoid conflicts with Google ADK internals.

### Key Files

- **`agent.py`**
  - Defines the computer-use agent (currently a single agent).
  - Factory function:
    ```python
    def get_agent_and_computer(
        litellm_model: str = "openai/gpt-5-mini",
        screen_size = SCREEN_SIZE
    ) -> Tuple[Agent, BaseComputer]
    ```
  - Returns both the agent and the computer instance.

- **`prompt.py`**
  - System prompt for the computer-use agent.

- **`toolset.py`**
  - Implements `ComputerToolSet`, exposing computer interaction tools to the agent.

- **`model_callbacks.py`**
  - Handles pre/post-processing of model calls.
  - Injects multi-modal artifacts (screenshots) into LLM requests.
  - Only the **latest tool artifact** is attached to reduce request size.

- **`visual_grounding.py`**
  - Converts a semantic UI description into screen coordinates.
  - Entry point:
    ```python
    async def locate_visual_element(
        image_bytes: bytes,
        visual_description: str,
    ) -> Tuple[float, float]
    ```

---

## Visual Grounding Pipeline

General-purpose VLMs are not trained for precise UI grounding.  
This system uses a **two-step grounding process**:

1. **UI Parsing (OmniParser)**
   - A screenshot is sent to the Omni server.
   - The server returns:
     - Annotated image (bounding boxes + element IDs)
     - Structured UI element metadata (ID, bounding box, text)

2. **Set-of-Mark Prompting**
   - The annotated image and UI metadata are sent to a VLM.
   - The model predicts the **pixel coordinates** of the target element.
   - The model is not required to select an element ID, allowing recovery even if the parser misses an element.

This approach improves robustness without requiring UI-specific model training.

---

## `omni/`

Handles UI understanding and grounding support.

- **`server.py`**
  - Runs OmniParser as a persistent server.
  - Avoids reloading heavy models for every request.
  - Can be hosted remotely for performance.

- **`client.py`**
  - Sends screenshots to the Omni server.
  - Receives annotated images and UI element metadata.

---

## CLI Interface

- **`cli.py`**
  - Provides a CLI-style interface to interact with the agent.
  - Supports transparent execution:
    - Agent reasoning
    - Tool calls
    - Final outputs
  - Useful for debugging and observing live browser automation.

---

## Observability (ADK + Opik)

- Uses **OpikTracer** for observability and tracing.
- Custom tracer extends the default implementation to:
  - Convert image bytes into base64 data URIs for dashboard visibility.
  - Avoid mutating the original LLM request seen by the model.

- Functions involved in visual grounding and Omni communication are manually instrumented using Opik’s `@track` decorator.

---
````
