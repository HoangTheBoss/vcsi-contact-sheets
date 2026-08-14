import pytest
from vcsi.vcsi import (
    MediaInfo,
    timestamp_generator,
    generate_hybrid_timestamps,
)


class DummyMediaInfo:
    def __init__(self, duration_seconds=1000.0):
        self.duration_seconds = duration_seconds


class DummyArgs:
    def __init__(self, num_samples=5, start_delay_percent=7, end_delay_percent=7,
                 random=False, seed=None, random_min_spacing=None, interval=None):
        self.num_samples = num_samples
        self.start_delay_percent = start_delay_percent
        self.end_delay_percent = end_delay_percent
        self.random = random
        self.seed = seed
        self.random_min_spacing = random_min_spacing
        self.interval = interval


def test_uniform_timestamp_distribution():
    media_info = DummyMediaInfo(1000.0)
    args = DummyArgs(num_samples=4, start_delay_percent=10, end_delay_percent=10)

    ts = list(timestamp_generator(media_info, args))
    assert len(ts) == 4
    times = [t[0] for t in ts]
    expected_step = (900.0 - 100.0) / 5
    for i, t in enumerate(times):
        assert abs(t - (100.0 + (i + 1) * expected_step)) < 1e-5


def test_random_timestamp_reproducibility():
    media_info = DummyMediaInfo(1000.0)
    args1 = DummyArgs(num_samples=10, random=True, seed=42)
    args2 = DummyArgs(num_samples=10, random=True, seed=42)

    ts1 = list(timestamp_generator(media_info, args1))
    ts2 = list(timestamp_generator(media_info, args2))

    assert len(ts1) == 10
    assert len(ts2) == 10
    assert [x[0] for x in ts1] == [x[0] for x in ts2]


def test_random_timestamp_min_spacing():
    media_info = DummyMediaInfo(1000.0)
    args = DummyArgs(num_samples=5, random=True, seed=123, random_min_spacing=50.0)

    ts = list(timestamp_generator(media_info, args))
    times = [t[0] for t in ts]
    for i in range(len(times) - 1):
        assert times[i + 1] - times[i] >= 50.0


def test_hybrid_timestamps_manual_dodging():
    media_info = DummyMediaInfo(1000.0)
    manual_ts = [(200.0, "00:03:20"), (500.0, "00:08:20")]
    grid_total = 6

    args = DummyArgs(start_delay_percent=10, end_delay_percent=10)
    combined = generate_hybrid_timestamps(media_info, args, manual_ts, grid_total)

    assert len(combined) == 6
    times = [t[0] for t in combined]

    assert 200.0 in times
    assert 500.0 in times

    min_time = 100.0
    max_time = 900.0
    for t in times:
        assert min_time <= t <= max_time

    ideal_step = (max_time - min_time) / (grid_total + 1)
    delta = 0.20 * ideal_step

    for t in times:
        if t not in (200.0, 500.0):
            assert abs(t - 200.0) >= delta
            assert abs(t - 500.0) >= delta
