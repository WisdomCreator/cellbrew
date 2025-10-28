from typing import Callable, TYPE_CHECKING
from src.settings import bacteria_specs

if TYPE_CHECKING:
    from src.app.game_app import GameApp


class CommandBus:
    def __init__(self, app: "GameApp"):
        self.app = app
        self.handlers: dict[str, Callable[[list[str]], str]] = {"spawn": self.__spawn}

    def execute(self, command: str) -> str | None:
        command = command.strip()
        if not command:
            return None
        parts = command.split()
        action = parts[0]
        handler = self.handlers.get(action)
        if not handler:
            return f"Unknown command: {action}"
        return handler(parts[1:])

    # Handlers
    def __spawn(self, args: list[str]) -> str:
        # TODO: Добавить проверку аргументов
        bacteria_type = args[0].lower()
        if bacteria_type in bacteria_specs:
            self.app.spawn_bacteria(bacteria_type)
            return "Bacteria spawned: " + bacteria_type
        return "Unknown bacteria type: " + bacteria_type
