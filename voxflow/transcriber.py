"""VoxFlow Transcriber - High-quality speech-to-text using faster-whisper.

Optimized for Polish and English with:
- initial_prompt to bias towards correct Polish diacritics
- Temperature fallback for reliability
- Audio normalization for consistent input levels
- Post-processing auto-correction
- Tuned VAD parameters for dictation
"""
import os
import numpy as np
from typing import Optional
from pathlib import Path

from voxflow.post_processor import post_process, get_initial_prompt


class VoxTranscriber:
    """Handles speech-to-text transcription using faster-whisper."""

    def __init__(self, model_size: str = "small", device: str = "cpu", compute_type: str = "int8"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None
        self._model_loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._model_loaded

    @staticmethod
    def get_models_dir() -> Path:
        """Get the directory where models are cached."""
        app_data = os.environ.get("APPDATA", os.path.expanduser("~"))
        models_dir = Path(app_data) / "VoxFlow" / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        return models_dir

    def load_model(self, model_size: Optional[str] = None, on_progress: Optional[callable] = None):
        """Load the Whisper model. Downloads on first use."""
        if model_size:
            self.model_size = model_size

        if on_progress:
            size_info = self.estimate_model_size(self.model_size)
            on_progress(f"⏳ Ładowanie modelu '{self.model_size}' ({size_info})...")

        try:
            from faster_whisper import WhisperModel

            models_dir = self.get_models_dir()

            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root=str(models_dir),
                num_workers=2,  # Parallel decoding workers
            )
            self._model_loaded = True

            if on_progress:
                on_progress(f"✅ Model '{self.model_size}' gotowy")

        except Exception as e:
            self._model_loaded = False
            error_msg = f"Błąd ładowania modelu: {e}"
            if on_progress:
                on_progress(error_msg)
            raise RuntimeError(error_msg) from e

    def transcribe(
        self,
        audio_data: np.ndarray,
        language: str = "auto",
        beam_size: int = 5,
        vad_enabled: bool = True,
        auto_correct: bool = True,
        on_progress: Optional[callable] = None,
    ) -> dict:
        """Transcribe audio data to text with maximum quality.
        
        Args:
            audio_data: numpy array of audio samples (float32, 16kHz mono)
            language: Language code ("pl", "en") or "auto" for detection
            beam_size: Beam search width (higher = more accurate, slower)
            vad_enabled: Use Voice Activity Detection filtering
            auto_correct: Apply post-processing auto-correction
            on_progress: Callback for progress updates
            
        Returns:
            dict with keys: text, raw_text, language, segments, duration
        """
        if not self._model_loaded or self._model is None:
            raise RuntimeError("Model nie jest załadowany. Wywołaj load_model() najpierw.")

        if audio_data is None or len(audio_data) == 0:
            return {"text": "", "raw_text": "", "language": "", "segments": [], "duration": 0.0}

        # ─── Prepare audio ────────────────────────────────────────
        audio_data = self._prepare_audio(audio_data)

        if on_progress:
            on_progress("🔍 Transkrybuję...")

        # ─── Build transcription params ───────────────────────────
        lang_code = None if language == "auto" else language

        # Get initial_prompt — this is KEY for Polish quality
        # It biases the model towards outputting proper Polish diacritics
        initial_prompt = get_initial_prompt(language)

        kwargs = {
            "beam_size": beam_size,
            "best_of": min(beam_size, 3),  # Sample multiple, pick best
            "patience": 1.5,  # More patient beam search for accuracy
            "initial_prompt": initial_prompt,
            "condition_on_previous_text": True,  # Context from prev segments
            "temperature": [0.0, 0.2, 0.4, 0.6, 0.8],  # Temperature fallback
            "compression_ratio_threshold": 2.4,
            "log_prob_threshold": -1.0,
            "no_speech_threshold": 0.6,
            "word_timestamps": False,
        }

        if lang_code:
            kwargs["language"] = lang_code

        # VAD parameters tuned for dictation (short pauses OK)
        if vad_enabled:
            kwargs["vad_filter"] = True
            kwargs["vad_parameters"] = {
                "min_silence_duration_ms": 300,  # Short silence = still speaking
                "speech_pad_ms": 250,  # Pad speech segments
                "threshold": 0.35,  # Speech detection sensitivity
                "min_speech_duration_ms": 100,  # Catch short words
                "max_speech_duration_s": 60,  # Max segment length
            }
        else:
            kwargs["vad_filter"] = False

        # ─── Transcribe ──────────────────────────────────────────
        try:
            segments_gen, info = self._model.transcribe(audio_data, **kwargs)

            segments = []
            text_parts = []

            for segment in segments_gen:
                seg_text = segment.text.strip()
                if seg_text:
                    segments.append({
                        "start": segment.start,
                        "end": segment.end,
                        "text": seg_text,
                    })
                    text_parts.append(seg_text)

            raw_text = " ".join(text_parts)

            # ─── Post-processing / auto-correction ────────────────
            if auto_correct and raw_text:
                corrected_text = post_process(
                    raw_text,
                    language=info.language,
                    fix_capitalization=True,
                    fix_punctuation=True,
                    remove_fillers=True,
                    fix_repetitions=True,
                    apply_corrections=True,
                )
            else:
                corrected_text = raw_text

            result = {
                "text": corrected_text,
                "raw_text": raw_text,
                "language": info.language,
                "language_probability": info.language_probability,
                "segments": segments,
                "duration": info.duration,
            }

            if on_progress:
                flag = "🇵🇱" if info.language == "pl" else "🇬🇧" if info.language == "en" else "🌍"
                prob = info.language_probability * 100
                on_progress(f"✅ {flag} {info.language.upper()} ({prob:.0f}%) • {info.duration:.1f}s")

            return result

        except Exception as e:
            error_msg = f"Błąd transkrypcji: {e}"
            if on_progress:
                on_progress(error_msg)
            raise RuntimeError(error_msg) from e

    def _prepare_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Prepare audio for transcription: normalize, ensure format."""
        # Ensure float32
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        # Ensure mono 1D
        if audio_data.ndim > 1:
            audio_data = audio_data[:, 0]

        # ─── Normalize audio volume ───────────────────────────────
        # This is critical for consistent transcription quality.
        # Whisper expects audio roughly in [-1, 1] range with good SNR.
        max_val = np.max(np.abs(audio_data))
        if max_val > 0 and max_val < 0.9:
            # Normalize to ~90% of max range
            audio_data = audio_data * (0.9 / max_val)
        elif max_val > 1.0:
            # Clip and normalize if clipping
            audio_data = np.clip(audio_data, -1.0, 1.0)

        # ─── Remove DC offset ────────────────────────────────────
        # Some microphones have a DC bias that hurts recognition
        audio_data = audio_data - np.mean(audio_data)

        return audio_data

    def unload_model(self):
        """Unload the model to free memory."""
        self._model = None
        self._model_loaded = False

    @staticmethod
    def estimate_model_size(model_name: str) -> str:
        """Estimate download/memory size for a model."""
        sizes = {
            "tiny": "~75 MB",
            "base": "~150 MB",
            "small": "~500 MB",
            "medium": "~1.5 GB",
            "large-v3": "~3 GB",
        }
        return sizes.get(model_name, "Nieznany")
