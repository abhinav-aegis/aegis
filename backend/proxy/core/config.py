from backend.common.core.config import Settings, SettingsConfigDict

class AgentSettings(Settings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )
    PROJECT_NAME: str = "Proxy Microservice"

settings = AgentSettings()
