import math
import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

import arcade

from src.event_bus import EventBus
from src.settings import bacteria_specs, resource_specs

if TYPE_CHECKING:
    from src.world import Bounds

Position = tuple[float, float]

BACTERIA_TEXTURE_CACHE = {
    bacteria_type: arcade.make_soft_circle_texture(
        spec["diameter"], spec["color"], outer_alpha=150
    )
    for bacteria_type, spec in bacteria_specs.items()
}

RESOURCE_TEXTURE_CACHE = {
    resource_type: arcade.make_soft_circle_texture(
        spec["diameter"], spec["color"], outer_alpha=160
    )
    for resource_type, spec in resource_specs.items()
}


@dataclass
class CommandResult:
    success: bool
    message: str


class Entity(arcade.Sprite):
    def __init__(
        self,
        diameter: int,
        position: Position,
        texture: arcade.Texture,
        event_bus: EventBus,
    ):
        self.diameter = diameter
        super().__init__(texture)
        self.center_x, self.center_y = position
        self.event_bus = event_bus

    def compute_inner_bounds(self, bounds: "Bounds") -> "Bounds":
        left, right, bottom, top = bounds
        left += int(self.diameter / 2)
        right -= int(self.diameter / 2)
        bottom += int(self.diameter / 2)
        top -= int(self.diameter / 2)
        return (left, right, bottom, top)


class Resource(Entity):
    def __init__(self, resource_type: str, position: Position, event_bus: EventBus):
        self.resource_type = resource_type
        self.lifetime = random.uniform(*resource_specs[resource_type]["lifetime"])
        self.energy = resource_specs[resource_type]["energy"]

        diameter = resource_specs[resource_type]["diameter"]
        texture = RESOURCE_TEXTURE_CACHE[resource_type]
        super().__init__(diameter, position, texture, event_bus)

    def update(self, delta: float):
        self.lifetime -= delta
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()


class Bacteria(Entity):
    def __init__(
        self,
        bacteria_type: str,
        name: str | None,
        creator_id: str,
        position: Position,
        event_bus: EventBus,
    ):
        self.name = name
        self.creator_id = creator_id
        self.type_name = bacteria_specs[bacteria_type]["name"]
        self.max_hp = bacteria_specs[bacteria_type]["max_hp"]
        self.hp = self.max_hp
        self.max_energy = bacteria_specs[bacteria_type]["max_energy"]
        self.energy = self.max_energy
        self.speed = bacteria_specs[bacteria_type]["speed"]
        self.damage = bacteria_specs[bacteria_type]["damage"]
        self.attack_cooldown = bacteria_specs[bacteria_type]["attack_cooldown"]
        self.attack_range = bacteria_specs[bacteria_type]["attack_range"]
        self.defense = bacteria_specs[bacteria_type]["defense"]
        self.metabolism: float = bacteria_specs[bacteria_type]["metabolism"]
        self.vision = bacteria_specs[bacteria_type]["vision"]
        self.reproduction = bacteria_specs[bacteria_type]["reproduction"]
        self.aggression = bacteria_specs[bacteria_type]["aggression"]
        self.available_resources = bacteria_specs[bacteria_type]["available_resources"]

        diameter = bacteria_specs[bacteria_type]["diameter"]
        texture = BACTERIA_TEXTURE_CACHE[bacteria_type]
        super().__init__(diameter, position, texture, event_bus)

        self.velocity_angle = random.uniform(0, 360)
        self.wander_timer = 0.0
        self.target_resource: Resource | None = None
        self.target_bacteria: Bacteria | None = None
        self.__time_since_attack = 0.0

    def update(
        self,
        delta: float,
        bounds: "Bounds",
    ):
        self.__time_since_attack += delta
        self.energy -= self.metabolism * delta
        if self.hp <= 0 or self.energy <= 0:
            self.remove_from_sprite_lists()
            return
        if self.target_resource and self.target_bacteria:
            dist_to_resource = arcade.get_distance_between_sprites(
                self, self.target_resource
            )
            dist_to_bacteria = arcade.get_distance_between_sprites(
                self, self.target_bacteria
            )
            if dist_to_bacteria < dist_to_resource:
                self.move_towards(self.target_bacteria.position, delta)
            else:
                self.move_towards(self.target_resource.position, delta)
        elif self.target_resource:
            self.move_towards(self.target_resource.position, delta)
        elif self.target_bacteria:
            self.move_towards(self.target_bacteria.position, delta)
        else:
            self.wander_timer -= delta
            if self.wander_timer <= 0:
                self.__reset_wander_direction()
            self.move_forward(delta, bounds)

        if self.target_bacteria:
            dist_to_bacteria = arcade.get_distance_between_sprites(
                self, self.target_bacteria
            )
            if (
                dist_to_bacteria <= self.attack_range
                and self.__time_since_attack >= self.attack_cooldown
            ):
                self.attack_bacteria(self.target_bacteria)

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

    def consume_resource(self, resource: Resource):
        self.energy = min(self.energy + resource.energy, self.max_energy)
        resource.remove_from_sprite_lists()
        self.event_bus.emit("resource_consume")

    def attack_bacteria(self, bacteria: "Bacteria"):
        damage = max(0, self.damage - bacteria.defense)
        bacteria.hp -= damage
        self.__time_since_attack = 0.0
        self.event_bus.emit("bacteria_attack", self, bacteria, damage)

    def __reset_wander_direction(self):
        self.velocity_angle = random.uniform(0, 360)
        self.wander_timer = random.uniform(0.6, 2)
