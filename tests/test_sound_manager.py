from pathlib import Path
from unittest.mock import Mock

import pytest

from src.sound_manager import SoundManager


class TestSoundManagerLoading:
    def test_init_loads_sounds(self, monkeypatch: pytest.MonkeyPatch):
        music_files = [Path("test_music_1.mp3"), Path("test_music_2.mp3")]
        sfx_files = [Path("test_sfx_1.mp3"), Path("test_sfx_2.mp3")]

        fake_music_dir = Mock()
        fake_music_dir.iterdir.return_value = music_files
        fake_sfx_dir = Mock()
        fake_sfx_dir.iterdir.return_value = sfx_files

        monkeypatch.setattr(
            "src.sound_manager.sound_settings.music_path",
            fake_music_dir,
        )
        monkeypatch.setattr("src.sound_manager.sound_settings.sfx_path", fake_sfx_dir)

        load_sound_mock = Mock(return_value=Mock())
        monkeypatch.setattr("src.sound_manager.arcade.load_sound", load_sound_mock)

        sound_manager = SoundManager()

        assert set(sound_manager.tracks) == {"test_music_1", "test_music_2"}
        assert set(sound_manager.sound_effects) == {"test_sfx_1", "test_sfx_2"}

        for path in music_files:
            load_sound_mock.assert_any_call(path, streaming=True)

        for path in sfx_files:
            load_sound_mock.assert_any_call(path)
