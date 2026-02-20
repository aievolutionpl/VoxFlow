"""VoxFlow Hotkey Manager - Hold-to-record with configurable key.

Press and HOLD key → recording starts
Release key → recording stops → auto-transcribe → auto-type

Supports:
- Single function keys: f2, f3, ..., f10
- Combo keys: ctrl+space, ctrl+shift+space
- Special keys: caps lock, insert, scroll lock
"""
import threading
from typing import Optional, Callable


class HotkeyManager:
    """Manages hold-to-record hotkey using keyboard hook.
    
    Uses keyboard.hook_key() or keyboard.add_hotkey() depending on
    whether the hotkey is a single key or a combination.
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
        self._is_combo = "+" in hotkey

    def start(self):
        """Start listening for the hold-to-record hotkey."""
        if self._active:
            return

        try:
            import keyboard

            if self._is_combo:
                # Combo hotkeys: use suppress=True press/release hooks
                self._hook_ref = keyboard.hook(self._on_key_event_combo)
            else:
                # Single key: hook_key fires for BOTH down and up events
                self._hook_ref = keyboard.hook_key(
                    self.hotkey,
                    callback=self._on_key_event,
                    suppress=False,
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
        self._is_combo = "+" in new_hotkey
        if was_active:
            self.start()

    def capture_next_key(self, timeout: float = 5.0) -> Optional[str]:
        """Block and wait for the next key press, return its name.
        
        Used by the UI to let users interactively pick their hotkey.
        Returns None if timeout expires or an error occurs.
        """
        try:
            import keyboard
            event = keyboard.read_event(suppress=False)
            if event and event.event_type == "down":
                name = event.name.lower()
                # Filter out just-modifier presses
                if name not in ("shift", "ctrl", "alt", "windows", "left shift",
                                "right shift", "left ctrl", "right ctrl",
                                "left alt", "right alt"):
                    return name
        except Exception as e:
            print(f"capture_next_key error: {e}")
        return None

    def _on_key_event(self, event):
        """Handle single key events — detect press (down) and release (up)."""
        try:
            if event.event_type == "down":
                if not self._is_held:
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

    def _on_key_event_combo(self, event):
        """Handle combo hotkey events via global keyboard hook."""
        try:
            import keyboard
            # Check if currently held keys match the combo
            keys = [k.strip() for k in self.hotkey.split("+")]
            all_pressed = all(keyboard.is_pressed(k) for k in keys)

            if event.event_type == "down" and all_pressed:
                if not self._is_held:
                    self._is_held = True
                    if self.on_press:
                        threading.Thread(target=self.on_press, daemon=True).start()
            elif event.event_type == "up" and self._is_held:
                main_key = keys[-1]
                if event.name.lower() == main_key or not all_pressed:
                    self._is_held = False
                    if self.on_release:
                        threading.Thread(target=self.on_release, daemon=True).start()
        except Exception as e:
            print(f"Combo hotkey event error: {e}")

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def is_held(self) -> bool:
        return self._is_held

    @staticmethod
    def get_available_hotkeys() -> list[str]:
        """Return list of recommended hotkeys for hold-to-record."""
        return [
            "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10",
            "ctrl+space", "ctrl+shift+space", "caps lock", "insert",
            "scroll lock",
        ]
