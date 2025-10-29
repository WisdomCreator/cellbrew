import random
from arcade import SpriteList
from arcade.math import clamp
from dataclasses import dataclass
from typing import Iterable, Optional
from src.entities import Bacteria, Position

Bounds = tuple[int, int, int, int]


@dataclass
class WorldConfig:
    max_bacteria: int
    max_resources: int


class World:
    def __init__(self, config: WorldConfig):
        self.config = config
        self.rand_gen = random.Random()
        self.bounds: Bounds
        self.bacteria_list: SpriteList[Bacteria] = SpriteList(
            use_spatial_hash=True, spatial_hash_cell_size=64
        )

    def set_bounds(self, bounds: Bounds):
        self.bounds = bounds
        for bacteria in self.bacteria_list:
            left, right, bottom, top = bacteria.compute_inner_bounds(bounds)
            bacteria.center_x = clamp(bacteria.center_x, left, right)
            bacteria.center_y = clamp(bacteria.center_y, bottom, top)

    def apply_config(self, config: WorldConfig):
        self.config = config

    def rand_gen_choice(self, items: Iterable[str]) -> Optional[str]:
        items = list(items)
        if not items:
            return None
        return self.rand_gen.choice(items)

    def spawn_bacteria(
        self,
        bacteria_type: str,
        position: Optional[Position] = None,
        energy: Optional[int] = None,
    ) -> Bacteria:
        position = position or self.__pick_spawn_position()
        bacteria = Bacteria(bacteria_type, "test", position)
        self.bacteria_list.append(bacteria)
        return bacteria

    def update(self, delta: float):
        for bacteria in self.bacteria_list:
            bacteria.update(delta, self.bounds)

    def __pick_spawn_position(self, margin: int = 40) -> Position:
        left, right, bottom, top = self.bounds
        return (
            random.uniform(left + margin, right - margin),
            random.uniform(bottom + margin, top - margin),
        )
