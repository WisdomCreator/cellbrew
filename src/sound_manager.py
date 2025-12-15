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
        self.tracks: dict[str, Sound] = {}
        self.sound_effects: dict[str, Sound] = {}
        self.load_sounds()

    def load_sounds(self):
        for path in sound_settings.music_path.iterdir():
            sound = arcade.load_sound(path, streaming=True)
            self.tracks[path.stem] = Sound(name=path.stem, path=path, sound=sound)
        for path in sound_settings.sfx_path.iterdir():
            sound = arcade.load_sound(path)
            self.sound_effects[path.stem] = Sound(
                name=path.stem, path=path, sound=sound
            )

    def play_music(self):
        if self.tracks:
            track = choice(list(self.tracks.values()))
            track.sound.play(volume=1.0, loop=True)

    def play_sfx(self, name: str):
        sound_effect = self.sound_effects.get(name)
        if sound_effect:
            sound_effect.sound.play(volume=1.0)
        else:
            raise KeyError(f"sfx {name} is not exist")
