"""VoxFlow Auto-Typer - Types transcribed text into the active window.

Built by AI Evolution Polska
"""
import sys
import time
from typing import Optional

# Maximum text length to auto-type (safety guard)
MAX_AUTO_TYPE_LENGTH = 10000

# Valid typing methods
VALID_METHODS = {"clipboard", "keyboard"}


class AutoTyper:
    """Types text into the currently active window/input field."""

    @staticmethod
    def type_text(text: str, method: str = "clipboard"):
        """Type text into the active window.
        
        Args:
            text: The text to type
            method: "clipboard" (paste via Ctrl+V) or "keyboard" (simulate keypresses)
        """
        if not text or not text.strip():
            return

        text = text.strip()

        # Safety: limit text length
        if len(text) > MAX_AUTO_TYPE_LENGTH:
            text = text[:MAX_AUTO_TYPE_LENGTH]

        # Validate method
        if method not in VALID_METHODS:
            method = "clipboard"

        if method == "clipboard":
            AutoTyper._paste_via_clipboard(text)
        elif method == "keyboard":
            AutoTyper._type_via_keyboard(text)

    @staticmethod
    def _paste_via_clipboard(text: str):
        """Paste text using clipboard (Ctrl+V) - fastest and most reliable."""
        import pyperclip
        import keyboard

        # Save current clipboard (optional, some users may not want this)
        try:
            old_clipboard = pyperclip.paste()
        except Exception:
            old_clipboard = None

        # Set new text to clipboard
        pyperclip.copy(text)

        # Small delay to ensure clipboard is ready
        time.sleep(0.05)

        # Simulate paste — macOS uses Cmd+V, everything else Ctrl+V
        paste_combo = "command+v" if sys.platform == "darwin" else "ctrl+v"
        keyboard.press_and_release(paste_combo)

        # Optional: restore old clipboard after a delay
        # (disabled by default to keep pasted text accessible)

    @staticmethod
    def _type_via_keyboard(text: str):
        """Type text character by character using keyboard simulation."""
        import keyboard
        # Small delay before typing
        time.sleep(0.1)
        keyboard.write(text, delay=0.02)

    @staticmethod
    def get_typing_methods() -> dict:
        """Return available typing methods with descriptions."""
        return {
            "clipboard": "📋 Wklej (Ctrl+V) — szybkie i niezawodne",
            "keyboard": "⌨️ Symuluj klawiaturę — wolniejsze, ale nie używa schowka",
        }
