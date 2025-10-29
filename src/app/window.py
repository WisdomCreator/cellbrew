import arcade

from src.app.game_app import GameApp
from src.entities import Bacteria
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
        for bacteria in self.app.world.bacteria_list:
            self.__draw_bacteria_info(bacteria)

        messages = self.app.console_messages
        line_spacing = 20
        for i, message in enumerate(reversed(messages)):
            # TODO: fix performance warning
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

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.app.set_bounds(width, height)

    def __draw_bacteria_info(self, bacteria: Bacteria):
        x = bacteria.center_x
        energy_bar_y = bacteria.center_y + bacteria.diameter / 2 + 8
        energy_ratio = bacteria.energy / bacteria.max_energy
        bar_width = 36
        bar_height = 6
        bar_gap = 2
        outline_size = 1
        arcade.draw_rect_filled(
            arcade.LBWH(
                x - bar_width / 2, energy_bar_y - bar_height / 2, bar_width, bar_height
            ),
            (20, 20, 20, 160),
        )  # energy_bar background
        arcade.draw_rect_filled(
            arcade.LBWH(
                x - (bar_width - outline_size * 2) / 2,
                energy_bar_y - (bar_height - outline_size * 2) / 2,
                bar_width * energy_ratio - outline_size * 2,
                bar_height - outline_size * 2,
            ),
            (70, 160, 255, 200),
        )  # energy_bar
        health_ratio = bacteria.hp / bacteria.max_hp
        health_bar_y = energy_bar_y + bar_height + bar_gap
        arcade.draw_rect_filled(
            arcade.LBWH(
                x - bar_width / 2, health_bar_y - bar_height / 2, bar_width, bar_height
            ),
            (20, 20, 20, 160),
        )
        arcade.draw_rect_filled(
            arcade.LBWH(
                x - (bar_width - outline_size * 2) / 2,
                health_bar_y - (bar_height - outline_size * 2) / 2,
                bar_width * health_ratio - outline_size * 2,
                bar_height - outline_size * 2,
            ),
            (50, 220, 60, 200),
        )  # health_bar

        name_y = health_bar_y + bar_height + bar_gap
        # TODO: fix performance warning
        arcade.draw_text(
            bacteria.name,
            x,
            name_y,
            (235, 240, 255, 255),
            10,
            anchor_x="center",
            anchor_y="bottom",
        )
