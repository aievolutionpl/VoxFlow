"""VoxFlow Recording Overlay — On-screen animation while recording.

Shows a small floating, always-on-top indicator with a pulsing red dot
and audio waveform animation. The overlay is transparent and click-through
so it doesn't interfere with the user's work.

Built by AI Evolution Polska
"""
import threading
import math
import time
import tkinter as tk
from typing import Optional


class RecordingOverlay:
    """Floating overlay that shows recording animation on screen."""

    WIDTH = 200
    HEIGHT = 60
    CORNER_MARGIN = 20

    def __init__(self):
        self._root: Optional[tk.Toplevel] = None
        self._canvas: Optional[tk.Canvas] = None
        self._alive = False
        self._phase = 0.0
        self._level = 0.0
        self._thread: Optional[threading.Thread] = None
        self._parent = None

    def show(self, parent=None):
        """Show the recording overlay on screen."""
        if self._alive:
            return
        self._parent = parent
        self._alive = True
        if parent:
            parent.after(0, self._create_window)
        else:
            self._thread = threading.Thread(target=self._run_standalone, daemon=True)
            self._thread.start()

    def hide(self):
        """Hide the recording overlay."""
        self._alive = False
        if self._root and self._parent:
            try:
                self._parent.after(0, self._destroy_window)
            except Exception:
                pass
        elif self._root:
            try:
                self._root.destroy()
            except Exception:
                pass
        self._root = None
        self._canvas = None

    def set_level(self, level: float):
        """Update the audio level (0.0 - 1.0)."""
        self._level = min(1.0, level * 5)

    def _create_window(self):
        """Create the overlay window (must be called from main thread)."""
        try:
            if self._parent:
                self._root = tk.Toplevel(self._parent)
            else:
                self._root = tk.Tk()

            win = self._root
            win.overrideredirect(True)  # No window decorations
            win.attributes("-topmost", True)  # Always on top
            win.attributes("-alpha", 0.9)  # Slightly transparent

            # Position: top-right corner of screen
            screen_w = win.winfo_screenwidth()
            x = screen_w - self.WIDTH - self.CORNER_MARGIN
            y = self.CORNER_MARGIN
            win.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

            # Dark background with rounded appearance
            win.configure(bg="#1a1a2e")
            
            self._canvas = tk.Canvas(
                win, width=self.WIDTH, height=self.HEIGHT,
                bg="#1a1a2e", highlightthickness=0,
            )
            self._canvas.pack(fill="both", expand=True)

            self._animate()
        except Exception as e:
            print(f"Overlay error: {e}")

    def _destroy_window(self):
        """Destroy the overlay window."""
        try:
            if self._root:
                self._root.destroy()
        except Exception:
            pass
        self._root = None
        self._canvas = None

    def _run_standalone(self):
        """Run overlay in its own event loop (fallback)."""
        self._create_window()
        if self._root:
            self._root.mainloop()

    def _animate(self):
        """Animation loop — pulsing dot + waveform bars."""
        if not self._alive or not self._canvas:
            return

        self._phase += 0.15
        c = self._canvas
        c.delete("all")

        # Background rounded rect
        self._round_rect(c, 2, 2, self.WIDTH - 2, self.HEIGHT - 2, 12, 
                         fill="#1a1a2e", outline="#ef4444", width=2)

        # Pulsing red dot
        pulse = (math.sin(self._phase * 2) + 1) / 2
        dot_r = 6 + pulse * 3
        dot_x, dot_y = 22, self.HEIGHT // 2
        # Glow
        glow_r = dot_r + 4 + pulse * 4
        c.create_oval(dot_x - glow_r, dot_y - glow_r,
                      dot_x + glow_r, dot_y + glow_r,
                      fill="#ef444430", outline="")
        # Dot
        c.create_oval(dot_x - dot_r, dot_y - dot_r,
                      dot_x + dot_r, dot_y + dot_r,
                      fill="#ef4444", outline="#dc2626", width=1)

        # "REC" text
        c.create_text(48, dot_y - 8, text="● REC", fill="#ef4444",
                      font=("Segoe UI", 11, "bold"), anchor="w")
        # "VoxFlow" small
        c.create_text(48, dot_y + 10, text="VoxFlow • AIEP", fill="#94a3b8",
                      font=("Segoe UI", 8), anchor="w")

        # Waveform bars (right side)
        bar_start = 115
        num_bars = 10
        bar_width = 4
        bar_gap = 3
        max_h = 20

        for i in range(num_bars):
            # Mix of audio level and animation
            wave = abs(math.sin(self._phase * 2.5 + i * 0.6))
            amp = (self._level * 0.7 + wave * 0.3) * max_h + 2
            x = bar_start + i * (bar_width + bar_gap)
            cy = self.HEIGHT // 2

            # Color gradient from purple to red based on amplitude
            if amp > max_h * 0.7:
                color = "#ef4444"
            elif amp > max_h * 0.4:
                color = "#a78bfa"
            else:
                color = "#8b5cf6"

            c.create_rectangle(x, cy - amp, x + bar_width, cy + amp,
                               fill=color, outline="")

        try:
            if self._root:
                self._root.after(50, self._animate)
        except Exception:
            pass

    @staticmethod
    def _round_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
        """Draw a rounded rectangle on a canvas."""
        r = radius
        canvas.create_arc(x1, y1, x1 + 2*r, y1 + 2*r, start=90, extent=90,
                          style="pieslice", **kwargs)
        canvas.create_arc(x2 - 2*r, y1, x2, y1 + 2*r, start=0, extent=90,
                          style="pieslice", **kwargs)
        canvas.create_arc(x1, y2 - 2*r, x1 + 2*r, y2, start=180, extent=90,
                          style="pieslice", **kwargs)
        canvas.create_arc(x2 - 2*r, y2 - 2*r, x2, y2, start=270, extent=90,
                          style="pieslice", **kwargs)
        canvas.create_rectangle(x1 + r, y1, x2 - r, y2, **kwargs)
        canvas.create_rectangle(x1, y1 + r, x1 + r, y2 - r, **kwargs)
        canvas.create_rectangle(x2 - r, y1 + r, x2, y2 - r, **kwargs)
