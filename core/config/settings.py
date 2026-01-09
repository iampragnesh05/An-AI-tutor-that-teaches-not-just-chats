from dataclasses import dataclass
import os
from dotenv import load_dotenv

# Loads variables from .env into environment (local dev)
load_dotenv()

@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_model: str

def _get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        return ""
    return value.strip()

settings = Settings(
    openai_api_key=_get_env("OPENAI_API_KEY", ""),
    openai_model=_get_env("OPENAI_MODEL", "gpt-4o-mini"),
)
