from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    resources_path: Path = Path("RESOURCES.md")
    data_dir: Path = Path("data")
    database_url: str = "sqlite:///data/wraeclast_quant.db"


def get_settings() -> Settings:
    return Settings()

