from dataclasses import dataclass
from math import hypot

import arcade

from src.app.game_app import GameApp
from src.entities import Bacteria
from src.settings import SYSTEM_USERNAME, WindowSettings

window_settings = WindowSettings()


@dataclass
class AttackIndicator:
    origin: tuple[float, float]
    target: tuple[float, float]
    damage: int
    elapsed: float = 0.0
    travel_time: float = 0.22
    linger_time: float = 0.36
    text_speed: float = 56.0

    @property
    def alpha(self) -> float:
        if self.elapsed <= self.travel_time:
            return 1.0
        return max(0.0, 1.0 - self.fade_progress)

    @property
    def travel_progress(self) -> float:
        return arcade.math.clamp(self.elapsed / self.travel_time, 0, 1)

    @property
    def fade_progress(self) -> float:
        linger = max(0.001, self.linger_time)
        if self.elapsed <= self.travel_time:
            return 0.0
        elapsed_in_linger = self.elapsed - self.travel_time
        return arcade.math.clamp(elapsed_in_linger / linger, 0, 1)

    @property
    def is_alive(self) -> bool:
        return self.elapsed < self.travel_time + self.linger_time

    def update(self, delta_time: float) -> None:
        self.elapsed += delta_time


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
        # arcade.set_background_color(window_settings.background_color)
        self.background = arcade.load_texture("assets/images/background/1.png")
        self.app = app
        self.app.set_bounds(window_settings.window_width, window_settings.window_height)
        self.command_mode = False
        self.command_buffer = ""
        self.command_text = arcade.Text("> _", 16, 50, arcade.color.WHITE, 14)
        self.console_messages = []
        self.attack_indicators: list[AttackIndicator] = []

        self.app.event_bus.subscribe("bacteria_attack", self.__on_bacteria_attack)

    def on_update(self, delta_time: float) -> bool | None:
        self.app.update(delta_time)
        self.__update_attack_indicators(delta_time)

    def on_draw(self) -> None:
        self.clear()
        arcade.draw_texture_rect(
            self.background, arcade.LBWH(0, 0, self.width, self.height)
        )
        self.app.world.resource_list.draw()
        self.app.world.bacteria_list.draw()
        for bacteria in self.app.world.bacteria_list:
            self.__draw_bacteria_info(bacteria)
        self.__draw_attack_indicators()

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
                    response = self.app.execute_command(
                        self.command_buffer, "console", SYSTEM_USERNAME
                    )
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
        bar_width = 70
        bar_height = 10
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

        name_y = health_bar_y + bar_gap * 2
        # TODO: fix performance warning
        arcade.draw_text(
            bacteria.name,
            x,
            name_y,
            (235, 240, 255, 255),
            14,
            anchor_x="center",
            anchor_y="bottom",
        )

    def __update_attack_indicators(self, delta: float):
        for indicator in self.attack_indicators:
            indicator.update(delta)
        self.attack_indicators[:] = [
            indicator for indicator in self.attack_indicators if indicator.is_alive
        ]

    def __draw_attack_indicators(self):
        if not self.attack_indicators:
            return
        trail_r, trail_g, trail_b, trail_a = (200, 255, 210, 190)
        for indicator in self.attack_indicators:
            travel_progress = indicator.travel_progress
            fade_progress = indicator.fade_progress
            intensity = indicator.alpha
            if intensity <= 0.0:
                continue
            origin_x, origin_y = indicator.origin
            target_x, target_y = indicator.target
            dx = target_x - origin_x
            dy = target_y - origin_y
            distance = hypot(dx, dy)
            if distance <= 1e-3:
                continue

            head_x = origin_x + dx * travel_progress
            head_y = origin_y + dy * travel_progress

            if travel_progress > 0.0:
                samples = max(3, int(6 + travel_progress * 12))
                prev_x, prev_y = origin_x, origin_y
                for idx in range(1, samples):
                    segment_t = travel_progress * (idx / (samples - 1))
                    seg_x = origin_x + dx * segment_t
                    seg_y = origin_y + dy * segment_t
                    segment_strength = (idx / max(1, samples - 1)) ** 1.35
                    segment_alpha = int(trail_a * intensity * segment_strength)
                    if segment_alpha > 0:
                        segment_color = (trail_r, trail_g, trail_b, segment_alpha)
                        arcade.draw_line(prev_x, prev_y, seg_x, seg_y, segment_color, 3)

    def __on_bacteria_attack(self, attacker: Bacteria, target: Bacteria, damage: int):
        dx = target.center_x - attacker.center_x
        dy = target.center_y - attacker.center_y
        distance = hypot(dx, dy)

        indicator = AttackIndicator(
            origin=attacker.position,
            target=target.position,
            damage=damage,
        )
        self.attack_indicators.append(indicator)
        self.app.sound_manager.play_sfx("attack")
