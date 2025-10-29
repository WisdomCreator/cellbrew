from typing import Any
from pydantic import BaseModel

FPS = 60
SYSTEM_CREATOR_ID = "console"


class WindowSettings(BaseModel):
    window_width: int = 1280
    window_height: int = 720
    window_title: str = "Cellbrew"
    fullscreen: bool = False
    resizable: bool = False
    update_rate: float = 1 / FPS
    antialiasing: bool = False
    background_color: tuple[int, int, int, int] = (28, 40, 50, 255)


bacteria_specs: dict[str, dict[str, Any]] = {
    "grazer": {
        "name": "Grazer",
        "hp": 120,
        "diameter": 30,
        "energy": 110,
        "speed": 80,
        "damage": 20,
        "attack_cooldown": 1,
        "defense": 30,
        "metabolism": 2,
        "vision": 220,
        "reproduction": 100,
        "aggression": 0.00,
        "available_resources": ["phytoplasma"],
        "color": (60, 200, 120),
    },
    "predator": {
        "name": "Predator",
        "hp": 120,
        "diameter": 20,
        "energy": 110,
        "speed": 80,
        "damage": 20,
        "attack_cooldown": 1,
        "defense": 30,
        "metabolism": 2,
        "vision": 220,
        "reproduction": 100,
        "aggression": 0.00,
        "available_resources": ["phytoplasma"],
        "color": (220, 40, 40),
    },
}
