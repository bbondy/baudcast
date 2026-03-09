"""Audio device wrappers for Baudcast."""

from __future__ import annotations

from typing import Any


def _require_sounddevice() -> Any:
    try:
        import sounddevice as sounddevice
    except ImportError as exc:  # pragma: no cover - depends on local environment
        raise RuntimeError(
            "sounddevice is required for live audio I/O. Install it with "
            "`python -m pip install -e .`."
        ) from exc
    try:
        import numpy  # noqa: F401
    except ImportError as exc:  # pragma: no cover - depends on local environment
        raise RuntimeError(
            "numpy is required for live audio I/O. Install it with "
            "`python -m pip install -e .`."
        ) from exc
    return sounddevice


def _validate_device(sounddevice: Any, kind: str, sample_rate: int, device: int | None) -> None:
    check = sounddevice.check_input_settings if kind == "input" else sounddevice.check_output_settings
    try:
        check(device=device, samplerate=sample_rate, channels=1)
    except sounddevice.PortAudioError as exc:  # pragma: no cover - depends on local environment
        available = sounddevice.query_devices()
        if not available:
            raise RuntimeError(
                f"No {kind} audio devices are available via PortAudio. "
                "Check macOS microphone/audio permissions and device configuration."
            ) from exc
        target = f"device {device}" if device is not None else f"default {kind} device"
        raise RuntimeError(
            f"Unable to use the {target}. Run `python -m baudcast devices` "
            "to inspect available device IDs."
        ) from exc


def list_devices() -> list[str]:
    """Return human-readable audio device descriptions."""
    sounddevice = _require_sounddevice()
    devices = sounddevice.query_devices()
    if not devices:
        return ["No audio devices available via PortAudio."]
    descriptions: list[str] = []
    for index, device in enumerate(devices):
        descriptions.append(
            f"{index}: {device['name']} "
            f"(in={device['max_input_channels']}, out={device['max_output_channels']})"
        )
    return descriptions


def play_samples(
    samples: list[float],
    sample_rate: int,
    *,
    device: int | None = None,
) -> None:
    """Play a mono sample buffer through the selected output device."""
    sounddevice = _require_sounddevice()
    _validate_device(sounddevice, "output", sample_rate, device)
    sounddevice.play(samples, samplerate=sample_rate, device=device, blocking=True)


def record_samples(
    duration_seconds: float,
    sample_rate: int,
    *,
    device: int | None = None,
) -> list[float]:
    """Record mono audio for a fixed duration."""
    sounddevice = _require_sounddevice()
    _validate_device(sounddevice, "input", sample_rate, device)
    frame_count = max(1, round(duration_seconds * sample_rate))
    recording = sounddevice.rec(
        frame_count,
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
        device=device,
        blocking=True,
    )
    return [float(sample[0]) for sample in recording]
