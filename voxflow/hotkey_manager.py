"""VoxFlow Hotkey Manager - Hold-to-record with F2 key.

Press and HOLD F2 → recording starts
Release F2 → recording stops → auto-transcribe → auto-type
"""
import threading
from typing import Optional, Callable


class HotkeyManager:
    """Manages hold-to-record hotkey using keyboard hook.
    
    This uses keyboard.hook_key() which properly detects
    both key-down and key-up events for a single key.
    """

    def __init__(
        self,
        hotkey: str = "f2",
        on_press: Optional[Callable] = None,
        on_release: Optional[Callable] = None,
    ):
        self.hotkey = hotkey.lower()
        self.on_press = on_press
        self.on_release = on_release
        self._active = False
        self._is_held = False
        self._hook_ref = None

    def start(self):
        """Start listening for the hold-to-record hotkey."""
        if self._active:
            return

        try:
            import keyboard
            # hook_key fires for BOTH down and up events on this key
            self._hook_ref = keyboard.hook_key(
                self.hotkey,
                callback=self._on_key_event,
                suppress=False,  # Don't suppress — works without admin
            )
            self._active = True
            print(f"Hotkey '{self.hotkey.upper()}' registered (hold-to-record)")
        except Exception as e:
            print(f"Hotkey registration failed: {e}")

    def stop(self):
        """Stop listening for hotkeys."""
        if not self._active:
            return
        try:
            import keyboard
            if self._hook_ref is not None:
                keyboard.unhook(self._hook_ref)
                self._hook_ref = None
        except Exception:
            pass
        self._active = False
        self._is_held = False

    def update_hotkey(self, new_hotkey: str):
        """Change the hotkey binding."""
        was_active = self._active
        if was_active:
            self.stop()
        self.hotkey = new_hotkey.lower()
        if was_active:
            self.start()

    def _on_key_event(self, event):
        """Handle key events — detect press (down) and release (up)."""
        try:
            if event.event_type == "down":
                if not self._is_held:
                    # First press (ignore key repeats)
                    self._is_held = True
                    if self.on_press:
                        threading.Thread(target=self.on_press, daemon=True).start()
            elif event.event_type == "up":
                if self._is_held:
                    self._is_held = False
                    if self.on_release:
                        threading.Thread(target=self.on_release, daemon=True).start()
        except Exception as e:
            print(f"Hotkey event error: {e}")

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def is_held(self) -> bool:
        return self._is_held

    @staticmethod
    def get_available_hotkeys() -> list[str]:
        """Return list of recommended single-key hotkeys for hold-to-record."""
        return [
            "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10",
        ]
