"""VoxFlow System Tray Integration.

Built by AI Evolution Polska
"""
import threading
from typing import Optional, Callable
from PIL import Image, ImageDraw


def create_tray_icon_image(recording: bool = False) -> Image.Image:
    """Create a simple tray icon image.
    
    Args:
        recording: If True, shows red recording indicator
    """
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if recording:
        # Red circle when recording
        draw.ellipse([4, 4, size - 4, size - 4], fill=(239, 68, 68, 255))
        # White inner mic shape
        draw.ellipse([20, 12, 44, 40], fill=(255, 255, 255, 255))
        draw.rectangle([26, 36, 38, 48], fill=(255, 255, 255, 255))
        draw.rectangle([18, 46, 46, 52], fill=(255, 255, 255, 255))
    else:
        # Purple gradient circle
        draw.ellipse([4, 4, size - 4, size - 4], fill=(139, 92, 246, 255))
        # White inner mic shape
        draw.ellipse([20, 12, 44, 40], fill=(255, 255, 255, 255))
        draw.rectangle([26, 36, 38, 48], fill=(255, 255, 255, 255))
        draw.rectangle([18, 46, 46, 52], fill=(255, 255, 255, 255))

    return img


class TrayManager:
    """Manages the system tray icon and menu."""

    def __init__(
        self,
        on_show: Optional[Callable] = None,
        on_toggle_recording: Optional[Callable] = None,
        on_quit: Optional[Callable] = None,
    ):
        self.on_show = on_show
        self.on_toggle_recording = on_toggle_recording
        self.on_quit = on_quit
        self._tray = None
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Start the system tray icon in a separate thread."""
        try:
            import pystray
            from pystray import MenuItem, Menu

            icon_image = create_tray_icon_image(recording=False)

            menu = Menu(
                MenuItem("🖥️ Pokaż VoxFlow", self._on_show_click, default=True),
                MenuItem("🎤 Nagrywaj / Zatrzymaj", self._on_toggle_click),
                Menu.SEPARATOR,
                MenuItem("❌ Zamknij", self._on_quit_click),
            )

            self._tray = pystray.Icon(
                name="VoxFlow",
                icon=icon_image,
                title="VoxFlow — by AI Evolution Polska",
                menu=menu,
            )

            self._thread = threading.Thread(target=self._tray.run, daemon=True)
            self._thread.start()

        except Exception as e:
            print(f"System tray failed: {e}")

    def stop(self):
        """Stop the system tray icon."""
        if self._tray:
            try:
                self._tray.stop()
            except Exception:
                pass

    def set_recording(self, recording: bool):
        """Update the tray icon to show recording state."""
        if self._tray:
            try:
                self._tray.icon = create_tray_icon_image(recording=recording)
                self._tray.title = "VoxFlow — 🔴 Nagrywam..." if recording else "VoxFlow — by AI Evolution Polska"
            except Exception:
                pass

    def _on_show_click(self, icon=None, item=None):
        if self.on_show:
            self.on_show()

    def _on_toggle_click(self, icon=None, item=None):
        if self.on_toggle_recording:
            self.on_toggle_recording()

    def _on_quit_click(self, icon=None, item=None):
        if self.on_quit:
            self.on_quit()
