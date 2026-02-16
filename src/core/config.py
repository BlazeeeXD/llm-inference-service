import yaml
from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional

# ServerSettings: The structure of the server
# ModelSettings: The structure of the modle 
# Settings: Aggregates everything 

class ServerSettings(BaseModel):
    host: str
    port: int
    log_level: str

class ModelSettings(BaseModel):
    path: str
    context_size: int = 2048
    n_threads: Optional[int] = None
    n_gpu_layers: int = 0
    use_mmap: bool = True
    use_mlock: bool = False

class Settings(BaseSettings):
    server: ServerSettings
    model: ModelSettings

    @classmethod
    def load_from_yaml(cls, config_path: str = "config/config.yaml") -> "Settings":
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found at: {path.absolute()}")

        with open(path, "r") as f:
            config_data = yaml.safe_load(f)

        return cls(**config_data)


try:
    settings = Settings.load_from_yaml()
except Exception as e:
    print(f"CRITICAL: Failed to load config.yaml: {e}")
    raise e