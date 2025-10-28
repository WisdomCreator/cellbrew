from src.world import World, WorldConfig
from src.command_bus import CommandBus
from collections import deque


class GameApp:
    def __init__(self) -> None:
        self.world_config = WorldConfig(10000, 10000)
        self.world = World(self.world_config)
        self.bounds: tuple[int, int, int, int]
        self.paused = False
        self.command_bus = CommandBus(self)
        self.console_messages: deque[str] = deque(maxlen=10)

    def execute_command(self, command: str) -> str | None:
        response = self.command_bus.execute(command)
        if response:
            self.console_messages.append(response)
        return response

    def set_bounds(self, width: int, height: int):
        self.bounds = (0, width, 0, height)
        self.world.set_bounds(self.bounds)

    def update(self, delta: float):
        if self.paused:
            return

        self.world.update(delta)

    def spawn_bacteria(self, bacteria_type: str):
        self.world.spawn_bacteria(bacteria_type)
