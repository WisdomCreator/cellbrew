from pathlib import Path
from typing import Any

from pydantic import BaseModel

FPS = 60
SYSTEM_USERNAME = "console"


class WindowSettings(BaseModel):
    window_width: int = 1280
    window_height: int = 720
    window_title: str = "Cellbrew"
    fullscreen: bool = False
    resizable: bool = False
    update_rate: float = 1 / FPS
    antialiasing: bool = False
    background_color: tuple[int, int, int, int] = (28, 40, 50, 255)


class RedisSettings(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    events_channel: str = "cellbrew_events"
    responses_chanel: str = "cellbrew_responses"


class SoundSettings(BaseModel):
    music_path: Path = Path("assets/sounds/music")
    sfx_path: Path = Path("assets/sounds/sfx")


bacteria_specs: dict[str, dict[str, Any]] = {
    "grazer": {
        "name": "Grazer",
        "max_hp": 120,
        "max_energy": 110,
        "diameter": 60,
        "speed": 80,
        "damage": 20,
        "attack_cooldown": 1,
        "defense": 30,
        "metabolism": 2.0,
        "vision": 220,
        "reproduction": 100,
        "aggression": 0.00,
        "available_resources": ["phytoplasma"],
        "color": (60, 200, 120),
    },
    "predator": {
        "name": "Predator",
        "max_hp": 120,
        "max_energy": 110,
        "diameter": 45,
        "speed": 120,
        "damage": 20,
        "attack_cooldown": 1,
        "defense": 30,
        "metabolism": 10.0,
        "vision": 220,
        "reproduction": 100,
        "aggression": 0.00,
        "available_resources": ["phytoplasma"],
        "color": (220, 40, 40),
    },
}

resource_specs: dict[str, dict[str, Any]] = {
    "phytoplasma": {
        "diameter": 10,
        "color": (120, 255, 150),
        "energy": 45,
        "spawn_interval": [0.5, 2.0],
        "lifetime": [5.0, 10.0],
    },
    "biomass": {
        "diameter": 6,
        "color": (190, 120, 80),
        "energy": 70,
        "spawn_interval": [5.0, 10.0],
        "lifetime": [7.0, 15.0],
    },
}
