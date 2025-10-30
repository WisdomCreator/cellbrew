import math
import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

import arcade

from src.settings import bacteria_specs

if TYPE_CHECKING:
    from src.world import Bounds

Position = tuple[float, float]

BACTERIA_TEXTURE_CACHE = {
    bacteria_type: arcade.make_soft_circle_texture(
        spec["diameter"], spec["color"], outer_alpha=150
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
        name: str | None,
        creator_id: str,
        position: Position,
    ):
        self.name = name
        self.creator_id = creator_id
        self.type_name = bacteria_specs[bacteria_type]["name"]
        self.max_hp = bacteria_specs[bacteria_type]["max_hp"]
        self.hp = self.max_hp
        self.max_energy = bacteria_specs[bacteria_type]["max_energy"]
        self.energy = self.max_energy
        self.diameter = bacteria_specs[bacteria_type]["diameter"]
        self.speed = bacteria_specs[bacteria_type]["speed"]
        self.damage = bacteria_specs[bacteria_type]["damage"]
        self.attack_cooldown = bacteria_specs[bacteria_type]["attack_cooldown"]
        self.defense = bacteria_specs[bacteria_type]["defense"]
        self.metabolism: float = bacteria_specs[bacteria_type]["metabolism"]
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
        self.energy -= self.metabolism * delta
        if self.hp <= 0 or self.energy <= 0:
            self.die()
            return
        self.wander_timer -= delta
        if self.wander_timer <= 0:
            self.__reset_wander_direction()
        self.move_forward(delta, bounds)

    def move_forward(self, delta: float, bounds: "Bounds"):
        heading = math.radians(self.velocity_angle)
        new_x = self.center_x + self.speed * delta * math.cos(heading)
        new_y = self.center_y + self.speed * delta * math.sin(heading)
        left, right, bottom, top = self.compute_inner_bounds(bounds)
        if (left < new_x < right) and (bottom < new_y < top):
            self.center_x = new_x
            self.center_y = new_y
            return
        self.__reset_wander_direction()
        self.move_forward(delta, bounds)

    def move_towards(self, point: Position, delta: float):
        dx = point[0] - self.center_x
        dy = point[1] - self.center_y
        distance = math.hypot(dx, dy)
        heading = math.atan2(dy, dx)
        self.velocity_angle = math.degrees(heading)
        step = self.speed * delta
        if step > distance:
            step = distance
        self.center_x += step * math.cos(heading)
        self.center_y += step * math.sin(heading)

    def compute_inner_bounds(self, bounds: "Bounds") -> "Bounds":
        left, right, bottom, top = bounds
        left += self.diameter / 2
        right -= self.diameter / 2
        bottom += self.diameter / 2
        top -= self.diameter / 2
        return (left, right, bottom, top)

    def die(self):
        self.target_point = None
        self.target_resource = None
        self.kill()

    def __reset_wander_direction(self):
        self.velocity_angle = random.uniform(0, 360)
        self.wander_timer = random.uniform(0.6, 2)
