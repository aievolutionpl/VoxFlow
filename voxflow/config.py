"""VoxFlow Configuration Management

Built by AI Evolution Polska
"""
import json
import os
from pathlib import Path
from dataclasses import dataclass, field, asdict


def get_config_dir() -> Path:
    """Get the configuration directory for VoxFlow."""
    app_data = os.environ.get("APPDATA", os.path.expanduser("~"))
    config_dir = Path(app_data) / "VoxFlow"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


# Valid value ranges for security validation
_VALID_MODELS = {"tiny", "base", "small", "medium", "large-v3"}
_VALID_LANGUAGES = {"auto", "pl", "en"}
_VALID_HOTKEYS = {"f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10"}
_VALID_TYPING_METHODS = {"clipboard", "keyboard"}
_VALID_THEMES = {"dark", "light"}


def _validate_config(data: dict) -> dict:
    """Validate and sanitize configuration values loaded from JSON.
    
    Prevents malformed config files from causing unexpected behavior.
    Returns sanitized dict with invalid values replaced by defaults.
    """
    defaults = VoxFlowConfig()
    validated = {}
    
    for key, value in data.items():
        if key not in VoxFlowConfig.__dataclass_fields__:
            continue  # Skip unknown keys
        
        field_obj = VoxFlowConfig.__dataclass_fields__[key]
        default_val = getattr(defaults, key)
        
        # Type validation
        expected_type = field_obj.type
        if expected_type == "str" and not isinstance(value, str):
            validated[key] = default_val
            continue
        elif expected_type == "int" and not isinstance(value, (int, float)):
            validated[key] = default_val
            continue
        elif expected_type == "float" and not isinstance(value, (int, float)):
            validated[key] = default_val
            continue
        elif expected_type == "bool" and not isinstance(value, bool):
            validated[key] = default_val
            continue
        
        # Range and value validation
        if key == "model_size" and value not in _VALID_MODELS:
            validated[key] = default_val
        elif key == "language" and value not in _VALID_LANGUAGES:
            validated[key] = default_val
        elif key == "hotkey" and str(value).lower() not in _VALID_HOTKEYS:
            validated[key] = default_val
        elif key == "typing_method" and value not in _VALID_TYPING_METHODS:
            validated[key] = default_val
        elif key == "theme" and value not in _VALID_THEMES:
            validated[key] = default_val
        elif key == "beam_size":
            validated[key] = max(1, min(20, int(value)))
        elif key == "sample_rate" and (not isinstance(value, int) or value <= 0):
            validated[key] = default_val
        elif key == "max_recording_duration":
            validated[key] = max(1.0, min(600.0, float(value)))
        elif key == "silence_threshold":
            validated[key] = max(0.001, min(1.0, float(value)))
        elif key == "silence_duration":
            validated[key] = max(0.1, min(30.0, float(value)))
        elif key == "window_width":
            validated[key] = max(400, min(1920, int(value)))
        elif key == "window_height":
            validated[key] = max(500, min(1080, int(value)))
        elif key == "vad_silence_ms":
            validated[key] = max(50, min(5000, int(value)))
        else:
            validated[key] = value
    
    return validated


@dataclass
class VoxFlowConfig:
    """Application configuration."""
    # Model settings
    model_size: str = "small"
    language: str = "auto"  # "auto", "pl", "en"
    device: str = "cpu"  # "cpu" or "cuda"
    compute_type: str = "int8"  # "int8" for CPU, "float16" for GPU

    # Audio settings
    sample_rate: int = 16000
    channels: int = 1
    silence_threshold: float = 0.01
    silence_duration: float = 2.0
    max_recording_duration: float = 300.0  # 5 min max

    # Hotkey - hold-to-record
    hotkey: str = "f2"

    # Typing behavior
    auto_type_enabled: bool = True
    typing_method: str = "clipboard"  # "clipboard" or "keyboard"
    auto_copy_to_clipboard: bool = True

    # UI & Behavior
    minimize_to_tray: bool = True
    start_minimized: bool = False
    start_with_windows: bool = False
    show_notifications: bool = True
    play_sounds: bool = True
    theme: str = "dark"
    window_width: int = 500
    window_height: int = 750

    # Advanced
    beam_size: int = 5
    vad_enabled: bool = True
    vad_silence_ms: int = 300
    auto_correct: bool = True

    def save(self):
        """Save configuration to JSON file."""
        config_path = get_config_dir() / "config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls) -> "VoxFlowConfig":
        """Load configuration from JSON file with validation."""
        config_path = get_config_dir() / "config.json"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    raise TypeError("Config must be a JSON object")
                validated = _validate_config(data)
                return cls(**validated)
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
        config = cls()
        config.save()
        return config

    @property
    def available_models(self) -> list:
        return ["tiny", "base", "small", "medium", "large-v3"]

    @property
    def available_languages(self) -> dict:
        return {
            "auto": "🌍 Auto-detect",
            "pl": "🇵🇱 Polski",
            "en": "🇬🇧 English",
        }

    @property
    def available_hotkeys(self) -> list:
        return ["f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10"]

    @property
    def available_typing_methods(self) -> dict:
        return {
            "clipboard": "📋 Wklej (Ctrl+V)",
            "keyboard": "⌨️ Klawiatura",
        }
