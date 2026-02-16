"""VoxFlow Audio Recorder - Captures microphone input."""
import threading
import numpy as np
import sounddevice as sd
from typing import Optional, Callable


class AudioRecorder:
    """Records audio from the microphone into a numpy buffer."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        silence_threshold: float = 0.01,
        silence_duration: float = 2.0,
        max_duration: float = 300.0,
        on_level_change: Optional[Callable[[float], None]] = None,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.max_duration = max_duration
        self.on_level_change = on_level_change

        self._recording = False
        self._audio_chunks: list[np.ndarray] = []
        self._stream: Optional[sd.InputStream] = None
        self._lock = threading.Lock()
        self._silence_counter = 0
        self._has_speech = False

    @property
    def is_recording(self) -> bool:
        return self._recording

    def start(self):
        """Start recording audio from the default microphone."""
        if self._recording:
            return

        self._audio_chunks = []
        self._recording = True
        self._silence_counter = 0
        self._has_speech = False

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            blocksize=int(self.sample_rate * 0.1),  # 100ms blocks
            callback=self._audio_callback,
        )
        self._stream.start()

    def stop(self) -> Optional[np.ndarray]:
        """Stop recording and return the audio data as a numpy array."""
        if not self._recording:
            return None

        self._recording = False

        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        with self._lock:
            if not self._audio_chunks:
                return None
            audio = np.concatenate(self._audio_chunks, axis=0)
            self._audio_chunks = []

        # Flatten to 1D mono
        if audio.ndim > 1:
            audio = audio[:, 0]

        return audio

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        """Callback for audio stream - stores chunks and monitors levels."""
        if not self._recording:
            return

        with self._lock:
            self._audio_chunks.append(indata.copy())

        # Calculate audio level (RMS)
        level = float(np.sqrt(np.mean(indata ** 2)))

        # Report level to UI
        if self.on_level_change:
            try:
                self.on_level_change(level)
            except Exception:
                pass

        # Track if we've heard any speech
        if level > self.silence_threshold:
            self._has_speech = True
            self._silence_counter = 0
        else:
            self._silence_counter += 1

        # Check recording limits
        total_samples = sum(c.shape[0] for c in self._audio_chunks)
        total_duration = total_samples / self.sample_rate

        if total_duration >= self.max_duration:
            self._recording = False

    @staticmethod
    def list_devices() -> list[dict]:
        """List available audio input devices."""
        devices = sd.query_devices()
        input_devices = []
        for i, dev in enumerate(devices):
            if dev["max_input_channels"] > 0:
                input_devices.append({
                    "index": i,
                    "name": dev["name"],
                    "channels": dev["max_input_channels"],
                    "sample_rate": dev["default_samplerate"],
                })
        return input_devices
