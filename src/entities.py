import math
import random
import arcade
from typing import Optional
from dataclasses import dataclass
from src.settings import bacteria_specs

Position = tuple[float, float]

BACTERIA_TEXTURE_CACHE = {
    bacteria_type: arcade.make_soft_circle_texture(30, spec["color"], outer_alpha=150)
    for bacteria_type, spec in bacteria_specs.items()
}


@dataclass
class CommandResult:
    success: bool
    message: str


class Resource(arcade.Sprite):
    def __init__(self, resource_type: str, position: Position, energy: int):
        self.resource_type = resource_type
        self.energy = energy
        self.lifetime = random.uniform(5, 20)

    def update(self, delta: float):
        self.lifetime -= delta
        if self.lifetime <= 0:
            ...


class Bacteria(arcade.Sprite):
    def __init__(
        self,
        bacteria_type: str,
        name: str,
        position: Position,
    ):
        self.name = name
        self.type_name = bacteria_specs[bacteria_type]["name"]
        self.max_hp = bacteria_specs[bacteria_type]["hp"]
        self.hp = self.max_hp
        self.energy = bacteria_specs[bacteria_type]["energy"]
        self.speed = bacteria_specs[bacteria_type]["speed"]
        self.damage = bacteria_specs[bacteria_type]["damage"]
        self.attack_cooldown = bacteria_specs[bacteria_type]["attack_cooldown"]
        self.defense = bacteria_specs[bacteria_type]["defense"]
        self.metabolism = bacteria_specs[bacteria_type]["metabolism"]
        self.vision = bacteria_specs[bacteria_type]["vision"]
        self.reproduction = bacteria_specs[bacteria_type]["reproduction"]
        self.aggression = bacteria_specs[bacteria_type]["aggression"]
        self.availableResources = bacteria_specs[bacteria_type]["available_resources"]
        self.color_rgb = bacteria_specs[bacteria_type]["color"]

        texture = BACTERIA_TEXTURE_CACHE[bacteria_type]
        super().__init__(texture)
        self.center_x, self.center_y = position

        self.velocity_angle = random.uniform(0, 360)
        self.wander_timer = 0.0
        self.target_point: Optional[tuple[float, float]] = None
        self.target_resource: Optional[Resource] = None

    def update(self, delta: float):
        self.wander_timer -= delta
        if self.wander_timer <= 0:
            self.velocity_angle = random.uniform(0, 360)
            self.wander_timer = random.uniform(0.6, 2)
        self.move_forward(delta)

    def move_forward(self, delta: float):
        heading = math.radians(self.velocity_angle)
        self.center_x += self.speed * delta * math.cos(heading)
        self.center_y += self.speed * delta * math.sin(heading)
