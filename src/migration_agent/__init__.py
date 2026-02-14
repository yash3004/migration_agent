from dataclasses import dataclass
import os
import logging
import yaml
from dacite import from_dict

_logger = logging.getLogger("migration.agent.core")


@dataclass
class OpenAI:
    api_key: str

@dataclass
class Config:
    openai: OpenAI


_cached_config = None


def load_config() -> Config:
    global _cached_config
    if _cached_config is not None:
        return _cached_config

    cfg = os.environ.get("CONFIG_LOCATION", "config.yaml")
    _logger.info(f"loading config from file {cfg}")

    with open(cfg, "r") as f:
        config = yaml.safe_load(f)

    _cached_config = from_dict(data_class=Config, data=config)
    print(f"loaded config: {_cached_config}")
    return _cached_config
