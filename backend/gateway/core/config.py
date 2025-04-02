from backend.common.core.config import Settings, SettingsConfigDict

class ServiceSettings(Settings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )
    SERVICE_NAME: str = "gateway"

settings = ServiceSettings()
