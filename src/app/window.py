import arcade

from src.app.game_app import GameApp
from src.settings import WindowSettings

window_settings = WindowSettings()


class GameWindow(arcade.Window):
    def __init__(self, app: GameApp):
        super().__init__(
            window_settings.window_width,
            window_settings.window_height,
            window_settings.window_title,
            window_settings.fullscreen,
            window_settings.resizable,
            window_settings.update_rate,
            window_settings.antialiasing,
        )
        arcade.set_background_color(window_settings.background_color)
        self.app = app
        self.app.set_bounds(window_settings.window_width, window_settings.window_height)
        self.command_mode = False
        self.command_buffer = ""
        self.command_text = arcade.Text("> _", 16, 50, arcade.color.WHITE, 14)
        self.console_messages = []

    def on_update(self, delta_time: float) -> bool | None:
        self.app.update(delta_time)

    def on_draw(self) -> None:
        self.clear()
        self.app.world.bacteria_list.draw()
        messages = self.app.console_messages
        line_spacing = 20
        for i, message in enumerate(reversed(messages)):
            arcade.draw_text(message, 16, 80 + line_spacing * i, arcade.color.WHITE, 12)

        if self.command_mode:
            self.command_text.text = f"> {self.command_buffer}_"
            self.command_text.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if self.command_mode:
            match symbol:
                case arcade.key.ESCAPE:
                    self.command_mode = False
                    self.command_buffer = ""
                case arcade.key.ENTER:
                    response = self.app.execute_command(self.command_buffer)
                    if response:
                        print(response)
                    self.command_buffer = ""
                    self.command_mode = False
                case arcade.key.BACKSPACE:
                    self.command_buffer = self.command_buffer[:-1]
                case _:
                    pass

        elif symbol in (arcade.key.ENTER, arcade.key.SLASH):
            self.command_mode = True

    def on_text(self, text: str):
        if self.command_mode and text.isprintable():
            self.command_buffer += text
