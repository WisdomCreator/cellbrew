from pathlib import Path
from random import choice

import arcade
from attr import dataclass

from src.settings import SoundSettings

sound_settings = SoundSettings()


@dataclass
class Sound:
    name: str
    path: Path
    sound: arcade.Sound


class SoundManager:
    def __init__(self):
        self.tracks: list[Sound] = []
        self.load_sounds()

    def load_sounds(self):
        for path in sound_settings.music_path.iterdir():
            sound = arcade.load_sound(path, streaming=True)
            self.tracks.append(Sound(name=path.stem, path=path, sound=sound))

    def play(self):
        if self.tracks:
            track = choice(self.tracks)
            track.sound.play(volume=1.0, loop=True)
