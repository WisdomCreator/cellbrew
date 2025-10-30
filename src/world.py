import itertools
import random
from dataclasses import dataclass
from typing import Iterable, Optional

from arcade import SpriteList
from arcade.math import clamp

from src.entities import Bacteria, Position, Resource
from src.settings import resource_specs

Bounds = tuple[int, int, int, int]


@dataclass
class WorldConfig:
    max_bacteria: int
    max_resources: int


class ResourceSpawnTimer:
    def __init__(self, resource_type: str):
        self.resource_type = resource_type
        self.min_interval, self.max_interval = resource_specs[resource_type][
            "spawn_interval"
        ]
        self.__accumulator: float
        self.__interval: float
        self.reset()

    def reset(self):
        self.__accumulator = 0.0
        self.__interval = random.uniform(self.min_interval, self.max_interval)

    def should_spawn(self) -> bool:
        return self.__accumulator >= self.__interval

    def tick(self, delta: float):
        self.__accumulator += delta


class World:
    def __init__(self, config: WorldConfig):
        self.config = config
        self.rand_gen = random.Random()
        self.bounds: Bounds
        self.resource_list: SpriteList[Resource] = SpriteList(
            use_spatial_hash=True, spatial_hash_cell_size=32
        )
        self.bacteria_list: SpriteList[Bacteria] = SpriteList(
            use_spatial_hash=True, spatial_hash_cell_size=64
        )
        self.resource_spawn_timers: list[ResourceSpawnTimer] = [
            ResourceSpawnTimer(resource_type) for resource_type in resource_specs
        ]

    def set_bounds(self, bounds: Bounds):
        self.bounds = bounds
        for entity in itertools.chain(self.resource_list, self.bacteria_list):
            left, right, bottom, top = entity.compute_inner_bounds(bounds)
            entity.center_x = clamp(entity.center_x, left, right)
            entity.center_y = clamp(entity.center_y, bottom, top)

    def apply_config(self, config: WorldConfig):
        self.config = config

    def rand_gen_choice(self, items: Iterable[str]) -> Optional[str]:
        items = list(items)
        if not items:
            return None
        return self.rand_gen.choice(items)

    def spawn_resource(self, resource_type: str, position: Optional[Position] = None):
        if len(self.resource_list) >= self.config.max_resources:
            oldest = self.resource_list[0]
            oldest.remove_from_sprite_lists()
        position = position or self.__pick_spawn_position(40)
        resource = Resource(resource_type, position)
        self.resource_list.append(resource)
        return resource

    def spawn_bacteria(
        self,
        bacteria_type: str,
        name: str,
        position: Optional[Position] = None,
        energy: Optional[int] = None,
    ) -> Bacteria:
        position = position or self.__pick_spawn_position()
        bacteria = Bacteria(bacteria_type, name, "creator_id", position)
        self.bacteria_list.append(bacteria)
        return bacteria

    def update(self, delta: float):
        for resource_spawn_timer in self.resource_spawn_timers:
            resource_spawn_timer.tick(delta)
            if resource_spawn_timer.should_spawn():
                self.spawn_resource(resource_spawn_timer.resource_type)
                resource_spawn_timer.reset()

        self.resource_list.update(delta)  # type: ignore
        self.bacteria_list.update(delta, self.bounds)  # type: ignore

    def __pick_spawn_position(self, margin: int = 40) -> Position:
        left, right, bottom, top = self.bounds
        return (
            random.uniform(left + margin, right - margin),
            random.uniform(bottom + margin, top - margin),
        )
