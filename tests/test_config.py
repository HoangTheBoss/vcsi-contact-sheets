import pytest
from vcsi.vcsi import Config, MediaCapture


def test_config_attributes():
    assert hasattr(Config, "ffmpeg_args")
    assert hasattr(Config, "random_min_spacing")
    assert Config.ffmpeg_args is None
    assert Config.random_min_spacing is None


def test_media_capture_init_ffmpeg_args():
    mc = MediaCapture("/path/to/video.mp4", ffmpeg_args="-hwaccel cuda")
    assert mc.ffmpeg_args == "-hwaccel cuda"
