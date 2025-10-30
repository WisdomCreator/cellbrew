from typing import TYPE_CHECKING, Callable

from src.settings import bacteria_specs

if TYPE_CHECKING:
    from src.app.game_app import GameApp


class CommandBus:
    def __init__(self, app: "GameApp"):
        self.app = app
        self.handlers: dict[str, Callable[[list[str]], str]] = {"spawn": self.__spawn}

    def execute(self, command: str, source: str, username: str) -> str | None:
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
        bacteria_type = args[0].lower()
        name = "Console"
        if len(args) == 2:
            name = args[1]
        if bacteria_type in bacteria_specs:
            self.app.spawn_bacteria(bacteria_type, name)
            return "Bacteria spawned: " + bacteria_type
        return "Unknown bacteria type: " + bacteria_type
