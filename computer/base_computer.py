import abc
from enum import Enum
from typing import Literal
from typing import Optional

import pydantic

class ComputerEnvironment(str, Enum):
  """Case insensitive enum for computer environments."""

  ENVIRONMENT_UNSPECIFIED = "ENVIRONMENT_UNSPECIFIED"
  """Defaults to browser."""
  ENVIRONMENT_BROWSER = "ENVIRONMENT_BROWSER"
  """Operates in a web browser."""

class ComputerState(pydantic.BaseModel):
  """Represents the current state of the computer environment.

  Attributes:
    screenshot: The screenshot in PNG format as bytes.
    url: The current URL of the webpage being displayed.
  """

  screenshot: bytes = pydantic.Field(
      default=None, description="Screenshot in PNG format"
  )
  url: Optional[str] = pydantic.Field(
      default=None, description="Current webpage URL"
  )


class BaseComputer(abc.ABC):
  """async defines an interface for computer environments.

  This abstract base class async defines the standard interface for controlling
  computer environments, including web browsers and other interactive systems.
  """

  @abc.abstractmethod
  async def screen_size(self) -> tuple[int, int]:
    """Returns the screen size of the environment.

    Returns:
      A tuple of (width, height) in pixels.
    """

  @abc.abstractmethod
  async def open_web_browser(self) -> ComputerState:
    """Opens the web browser.

    Returns:
      The current state after opening the browser.
    """

  @abc.abstractmethod
  async def click_at(self, visual_description: str) -> ComputerState:
    """
    Clicks on a visible UI element on the webpage.

    Args:
      visual_description: A natural language description of the UI element to click.

    Returns:
      The current UI state after clicking the element.
    """


  @abc.abstractmethod
  async def hover_at(self, visual_description: str) -> ComputerState:
    """
    Hovers over a visible UI element on the webpage.

    Use this to reveal hover-triggered UI such as dropdowns or tooltips.

    Args:
      visual_description:
        A natural language description of the UI element to hover over,
        described visually as a human would identify it.

    Returns:
      The current UI state after hovering.
    """


  @abc.abstractmethod
  async def type_text(
      self,
      text: str,
      press_enter: bool = True,
      clear_before_typing: bool = True,
  ) -> ComputerState:
    """Types text on the focused element.

    The system automatically presses ENTER after typing. To disable this, set `press_enter` to False.
    The system automatically clears any existing content before typing the specified `text`. To disable this, set `clear_before_typing` to False.

    Args:
      text: The text to type.
      press_enter: Whether to press ENTER after typing.
      clear_before_typing: Whether to clear existing content before typing.

    Returns:
      The current state after typing.
    """

  @abc.abstractmethod
  async def scroll_document(
      self, direction: Literal["up", "down", "left", "right"]
  ) -> ComputerState:
    """Scrolls the entire webpage "up", "down", "left" or "right" based on direction.

    Args:
      direction: The direction to scroll.

    Returns:
      The current state after scrolling.
    """

  @abc.abstractmethod
  async def scroll_at(
      self,
      visual_description: str,
      direction: Literal["up", "down", "left", "right"],
      magnitude: int,
  ) -> ComputerState:
    """
    Scrolls at a specific visually identified location on the webpage.

    The cursor is first moved to the described UI element or area,
    and the scroll action is performed at that location. This is useful
    for scrolling inside scrollable containers (e.g., panels, lists,
    sidebars) rather than the entire page.

    Args:
      visual_description:
        A natural language description of the UI element or area where
        the cursor should be positioned before scrolling, described
        visually as a human would identify it.

      direction:
        The direction to scroll: "up", "down", "left", or "right".

      magnitude:
        The amount to scroll, expressed as an abstract or relative value
        interpreted by the system.

    Returns:
      The current UI state after scrolling.
    """


  @abc.abstractmethod
  async def wait(self, seconds: int) -> ComputerState:
    """Waits for n seconds to allow unfinished webpage processes to complete.

    Args:
      seconds: The number of seconds to wait.

    Returns:
      The current state after waiting.
    """

  @abc.abstractmethod
  async def go_back(self) -> ComputerState:
    """Navigates back to the previous webpage in the browser history.

    Returns:
      The current state after navigating back.
    """

  @abc.abstractmethod
  async def go_forward(self) -> ComputerState:
    """Navigates forward to the next webpage in the browser history.

    Returns:
      The current state after navigating forward.
    """

  @abc.abstractmethod
  async def search(self) -> ComputerState:
    """Directly jumps to a search engine home page.

    Used when you need to start with a search. For example, this is used when
    the current website doesn't have the information needed or because a new
    task is being started.

    Returns:
      The current state after navigating to search.
    """

  @abc.abstractmethod
  async def navigate(self, url: str) -> ComputerState:
    """Navigates directly to a specified URL.

    Args:
      url: The URL to navigate to.

    Returns:
      The current state after navigation.
    """

  @abc.abstractmethod
  async def key_combination(self, keys: list[str]) -> ComputerState:
    """Presses keyboard keys and combinations, such as "control+c" or "enter".

    Args:
      keys: List of keys to press in combination.

    Returns:
      The current state after key press.
    """

  @abc.abstractmethod
  async def drag_and_drop(
      self, source_visual_description: str, destination_visual_description: str
  ) -> ComputerState:
    """
    Drags a visible UI element and drops it onto another visible UI element.

    Args:
      source_visual_description:
        A natural language description of the UI element to drag,
        identified visually.

      destination_visual_description:
        A natural language description of the UI element or area
        where the source should be dropped, identified visually.

    Returns:
      The current UI state after the drag-and-drop action.
    """


  @abc.abstractmethod
  async def current_state(self) -> ComputerState:
    """Returns the current state of the current webpage.

    Returns:
      The current environment state.
    """

  async def initialize(self) -> None:
    """Initialize the computer."""
    pass

  async def close(self) -> None:
    """Cleanup resource of the computer."""
    pass

  @abc.abstractmethod
  async def environment(self) -> ComputerEnvironment:
    """Returns the environment of the computer."""
