from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class LLMConfig(BaseSettings):
    """Generic schema for LLM providers."""
    provider: str
    model: str
    api_key: SecretStr
    base_url: Optional[str] = None

class OrchestratorSettings(LLMConfig):
    model_config = SettingsConfigDict(env_prefix="orchestrator_", env_file = ".env", extra="ignore")

class GroundingSettings(LLMConfig):
    model_config = SettingsConfigDict(env_prefix="grounding_", env_file = ".env", extra="ignore")

class OpikConfig(BaseSettings):
    """Configuration for Opik tracing."""
    api_key: SecretStr = Field(validation_alias="opik_api_key")
    project_name: str = Field(validation_alias="opik_project_name")
    track_disable: bool = Field(default=False, validation_alias="opik_track_disable")

    model_config = SettingsConfigDict(case_sensitive=False, env_file = ".env", extra="ignore")

class ServiceEndpoints(BaseSettings):
    """Configuration for dependent service endpoints."""
    playwright_url: str = Field(
        default="ws://playwright:37367/default",
        validation_alias="playwright_service_url"
    )
    omniparser_url: str = Field(
        default="http://omniparser:5000/parse",
        validation_alias="omniparser_service_url"
    )
    model_config = SettingsConfigDict(env_prefix="service_", env_file = ".env", extra="ignore")

class GlobalConfig(BaseSettings):
    orchestrator: OrchestratorSettings = Field(default_factory=OrchestratorSettings)
    grounding: GroundingSettings = Field(default_factory=GroundingSettings)
    opik: OpikConfig = Field(default_factory=OpikConfig)
    services: ServiceEndpoints = Field(default_factory=ServiceEndpoints)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = GlobalConfig()
