import math
import random
import arcade
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass
from src.settings import bacteria_specs

if TYPE_CHECKING:
    from src.world import Bounds

Position = tuple[float, float]

BACTERIA_TEXTURE_CACHE = {
    bacteria_type: arcade.make_soft_circle_texture(
        spec["size"], spec["color"], outer_alpha=150
    )
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
        self.bacteria_size = bacteria_specs[bacteria_type]["size"]
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

    def update(self, delta: float, bounds: "Bounds"):
        self.wander_timer -= delta
        if self.wander_timer <= 0:
            self.__reset_wander_direction()
        self.move_forward(delta, bounds)

    def move_forward(self, delta: float, bounds: "Bounds"):
        heading = math.radians(self.velocity_angle)
        new_x = self.center_x + self.speed * delta * math.cos(heading)
        new_y = self.center_y + self.speed * delta * math.sin(heading)
        left, right, bottom, top = bounds
        left += self.bacteria_size / 2
        right -= self.bacteria_size / 2
        bottom += self.bacteria_size / 2
        top -= self.bacteria_size / 2
        if (left <= new_x <= right) and (bottom <= new_y <= top):
            self.center_x = new_x
            self.center_y = new_y
            return
        self.__reset_wander_direction()
        self.move_forward(delta, bounds)

    def __reset_wander_direction(self):
        self.velocity_angle = random.uniform(0, 360)
        self.wander_timer = random.uniform(0.6, 2)
