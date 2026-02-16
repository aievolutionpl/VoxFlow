"""VoxFlow Sound Effects — Generate notification beeps for recording.

Uses numpy to generate pleasant tones and sounddevice to play them.
No external audio files needed — everything is generated programmatically.
"""
import threading
import numpy as np


# Pre-generate sounds at import time for zero-latency playback
_SAMPLE_RATE = 44100


def _generate_tone(frequencies: list[float], duration: float = 0.15,
                   volume: float = 0.3, fade_ms: float = 15) -> np.ndarray:
    """Generate a smooth multi-frequency tone."""
    t = np.linspace(0, duration, int(_SAMPLE_RATE * duration), dtype=np.float32)
    signal = np.zeros_like(t)
    for freq in frequencies:
        signal += np.sin(2 * np.pi * freq * t)
    signal /= len(frequencies)
    signal *= volume

    # Fade in/out to avoid clicks
    fade_samples = int(_SAMPLE_RATE * fade_ms / 1000)
    if fade_samples > 0 and fade_samples < len(signal) // 2:
        fade_in = np.linspace(0, 1, fade_samples, dtype=np.float32)
        fade_out = np.linspace(1, 0, fade_samples, dtype=np.float32)
        signal[:fade_samples] *= fade_in
        signal[-fade_samples:] *= fade_out

    return signal


def _generate_start_sound() -> np.ndarray:
    """Rising two-note chime: 'recording started'."""
    note1 = _generate_tone([523.25], duration=0.08, volume=0.25)  # C5
    gap = np.zeros(int(_SAMPLE_RATE * 0.03), dtype=np.float32)
    note2 = _generate_tone([659.25, 783.99], duration=0.12, volume=0.3)  # E5+G5 chord
    return np.concatenate([note1, gap, note2])


def _generate_stop_sound() -> np.ndarray:
    """Falling two-note chime: 'recording stopped'."""
    note1 = _generate_tone([783.99], duration=0.08, volume=0.25)  # G5
    gap = np.zeros(int(_SAMPLE_RATE * 0.03), dtype=np.float32)
    note2 = _generate_tone([523.25, 392.00], duration=0.15, volume=0.25)  # C5+G4 chord
    return np.concatenate([note1, gap, note2])


def _generate_done_sound() -> np.ndarray:
    """Triple ascending chime: 'transcription done'."""
    note1 = _generate_tone([523.25], duration=0.06, volume=0.2)  # C5
    gap = np.zeros(int(_SAMPLE_RATE * 0.025), dtype=np.float32)
    note2 = _generate_tone([659.25], duration=0.06, volume=0.22)  # E5
    note3 = _generate_tone([783.99], duration=0.10, volume=0.25)  # G5
    return np.concatenate([note1, gap, note2, gap, note3])


def _generate_error_sound() -> np.ndarray:
    """Low buzz: 'error occurred'."""
    return _generate_tone([220, 185], duration=0.25, volume=0.2)  # Low dissonant


# Pre-generate all sounds
_SOUNDS = {
    "start": _generate_start_sound(),
    "stop": _generate_stop_sound(),
    "done": _generate_done_sound(),
    "error": _generate_error_sound(),
}


def play(name: str):
    """Play a named sound effect in a background thread.
    
    Args:
        name: One of 'start', 'stop', 'done', 'error'
    """
    sound = _SOUNDS.get(name)
    if sound is None:
        return

    def _play():
        try:
            import sounddevice as sd
            sd.play(sound, samplerate=_SAMPLE_RATE, blocking=True)
        except Exception:
            pass

    threading.Thread(target=_play, daemon=True).start()
