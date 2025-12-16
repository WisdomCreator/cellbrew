from typing import TYPE_CHECKING, Any, Callable

from pydantic import BaseModel, Field, ValidationError

from src.settings import bacteria_specs

if TYPE_CHECKING:
    from src.app.game_app import GameApp


class Command(BaseModel):
    username: str
    source: str
    action: str
    params: dict[str, Any] = Field(default_factory=dict)


class CommandBus:
    def __init__(self, app: "GameApp"):
        self.app = app
        self.handlers: dict[str, Callable[..., str]] = {"spawn": self.__spawn}

    def execute_str(self, command_str: str, username: str, source: str) -> str:
        parts = command_str.split()
        if len(parts) < 2:
            return "Invalid command"
        action = parts[0]
        params = {"bacteria_type": parts[1]}
        if len(parts) > 2:
            params["bacteria_name"] = parts[2]
        try:
            command = Command(
                username=username, source=source, action=action, params=params
            )
            return self.execute(command)
        except ValidationError as exc:
            return f"Invalid command: {exc.errors(include_url=False)}"

    def execute_json(self, command_json: dict[str, Any]) -> str:
        try:
            command = Command(**command_json)
            return self.execute(command)
        except ValidationError as exc:
            return f"Invalid command: {exc.errors(include_url=False)}"

    def execute(self, command: Command) -> str:
        try:
            handler = self.handlers[command.action]
            return handler(**command.params)
        except KeyError as exc:
            return f"Unknown command: {exc.args[0]}"

    # Handlers
    def __spawn(self, bacteria_type: str, bacteria_name: str | None = None) -> str:
        bacteria_type = bacteria_type.lower()
        if bacteria_type in bacteria_specs:
            self.app.spawn_bacteria(bacteria_type, bacteria_name)
            return "Bacteria spawned: " + bacteria_type
        return "Unknown bacteria type: " + bacteria_type
