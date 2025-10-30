from collections import deque

from src.command_bus import CommandBus
from src.integration.redis_bridge import RedisBridge
from src.settings import RedisSettings
from src.sound_manager import SoundManager
from src.world import World, WorldConfig

redis_settings = RedisSettings()


class GameApp:
    def __init__(self) -> None:
        self.world_config = WorldConfig(10000, 10000)
        self.world = World(self.world_config)
        self.bounds: tuple[int, int, int, int]
        self.paused = False
        self.command_bus = CommandBus(self)
        self.console_messages: deque[str] = deque(maxlen=10)
        self.redis_bridge = RedisBridge(
            redis_settings.host,
            redis_settings.port,
            redis_settings.db,
            redis_settings.events_channel,
            redis_settings.responses_chanel,
            self.execute_command,
        )
        self.redis_bridge.start()
        self.sound_manager = SoundManager()
        self.sound_manager.play()

    def execute_command(self, command: str, source: str, username: str) -> str | None:
        response = self.command_bus.execute(command, source, username)
        if response:
            self.console_messages.append(response)
        return response

    def set_bounds(self, width: int, height: int):
        self.bounds = (0, width, 0, height)
        self.world.set_bounds(self.bounds)

    def update(self, delta: float):
        self.redis_bridge.poll()
        if self.paused:
            return

        self.world.update(delta)

    def spawn_bacteria(self, bacteria_type: str, name: str):
        self.world.spawn_bacteria(bacteria_type, name)
