from collections import deque
from typing import TYPE_CHECKING

from src.command_bus import CommandBus
from src.event_bus import EventBus
from src.integration.redis_bridge import RedisBridge
from src.settings import RedisSettings
from src.sound_manager import SoundManager
from src.world import World, WorldConfig

if TYPE_CHECKING:
    from src.entities import Bacteria

redis_settings = RedisSettings()


class GameApp:
    def __init__(self) -> None:
        self.event_bus = EventBus()
        self.world_config = WorldConfig(10000, 10000)
        self.world = World(self.world_config, self.event_bus)
        self.bounds: tuple[int, int, int, int]
        self.paused = False
        self.command_bus: CommandBus = CommandBus(self)
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
        self.sound_manager.play_music()

        self.event_bus.subscribe("bacteria_attack", self.__on_bacteria_attack)
        self.event_bus.subscribe("resource_consume", self.__on_resource_consume)

    def execute_command(self, command: str, username: str, source: str) -> str | None:
        if not command:
            return
        response = self.command_bus.execute_str(command, source, username)
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

    def spawn_bacteria(self, bacteria_type: str, name: str | None = None):
        name = name or "Console"
        self.world.spawn_bacteria(bacteria_type, name)

    # Handlers
    def __on_bacteria_attack(
        self, attacker: "Bacteria", target: "Bacteria", damage: int
    ):
        self.sound_manager.play_sfx("attack")

    def __on_resource_consume(self):
        self.sound_manager.play_sfx("consume")
