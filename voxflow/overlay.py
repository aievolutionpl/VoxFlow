"""VoxFlow Recording Overlay — On-screen animation while recording.

Shows a sleek floating bar at the BOTTOM-CENTER of the screen with
an animated audio waveform. The overlay is transparent and click-through
so it doesn't interfere with the user's work.

Built by AI Evolution Polska
"""
import threading
import math
import tkinter as tk
from typing import Optional


class RecordingOverlay:
    """Floating overlay that shows recording waveform animation at bottom of screen."""

    WIDTH = 560
    HEIGHT = 72
    BOTTOM_MARGIN = 80   # pixels from bottom of screen

    # Colours
    BG     = "#0d0d1f"
    BORDER = "#7c3aed"
    RED    = "#ef4444"
    PURPLE = "#a78bfa"
    PURPLE2 = "#7c3aed"
    GREY   = "#94a3b8"

    def __init__(self):
        self._root: Optional[tk.Toplevel] = None
        self._canvas: Optional[tk.Canvas] = None
        self._alive = False
        self._phase = 0.0
        self._level = 0.0
        self._parent = None

    # ── Public API ────────────────────────────────────────────────

    def show(self, parent=None):
        """Show the recording overlay on screen."""
        if self._alive:
            return
        self._parent = parent
        self._alive = True
        if parent:
            parent.after(0, self._create_window)
        else:
            threading.Thread(target=self._run_standalone, daemon=True).start()

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
        self._level = min(1.0, max(0.0, level))

    # ── Window management ─────────────────────────────────────────

    def _create_window(self):
        """Create the overlay window (must be called from main thread)."""
        try:
            if self._parent:
                self._root = tk.Toplevel(self._parent)
            else:
                self._root = tk.Tk()

            win = self._root
            win.overrideredirect(True)          # No title bar / borders
            win.attributes("-topmost", True)    # Always on top
            win.attributes("-alpha", 0.93)      # Slightly transparent

            # Position: bottom-center of screen
            screen_w = win.winfo_screenwidth()
            screen_h = win.winfo_screenheight()
            x = (screen_w - self.WIDTH) // 2
            y = screen_h - self.HEIGHT - self.BOTTOM_MARGIN
            win.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

            win.configure(bg=self.BG)

            self._canvas = tk.Canvas(
                win, width=self.WIDTH, height=self.HEIGHT,
                bg=self.BG, highlightthickness=0,
            )
            self._canvas.pack(fill="both", expand=True)

            self._animate()
        except Exception as e:
            print(f"Overlay error: {e}")

    def _destroy_window(self):
        try:
            if self._root:
                self._root.destroy()
        except Exception:
            pass
        self._root = None
        self._canvas = None

    def _run_standalone(self):
        self._create_window()
        if self._root:
            self._root.mainloop()

    # ── Animation ─────────────────────────────────────────────────

    def _animate(self):
        if not self._alive or not self._canvas:
            return

        self._phase += 0.12
        c = self._canvas
        W, H = self.WIDTH, self.HEIGHT
        c.delete("all")

        # ── Rounded background panel ──────────────────────────────
        self._round_rect(c, 2, 2, W - 2, H - 2, r=16,
                         fill=self.BG, outline=self.BORDER, width=2)

        # ── Pulsing mic icon (left side) ──────────────────────────
        pulse = (math.sin(self._phase * 2.5) + 1) / 2
        cx, cy = 36, H // 2

        # Outer glow ring
        glow_r = 18 + pulse * 5
        c.create_oval(cx - glow_r, cy - glow_r,
                      cx + glow_r, cy + glow_r,
                      fill="", outline=self.RED, width=1)

        # Inner filled dot
        dot_r = 12 + pulse * 3
        c.create_oval(cx - dot_r, cy - dot_r,
                      cx + dot_r, cy + dot_r,
                      fill=self.RED, outline="")

        # Mic body (white)
        c.create_oval(cx - 5, cy - 10, cx + 5, cy + 1,
                      fill="white", outline="")
        # Mic stand
        c.create_line(cx, cy + 1, cx, cy + 8, fill="white", width=2)
        c.create_line(cx - 6, cy + 8, cx + 6, cy + 8, fill="white", width=2)

        # ── Label text ────────────────────────────────────────────
        c.create_text(64, cy - 10, text="🎤  Nagrywam...",
                      fill=self.RED, font=("Segoe UI", 11, "bold"), anchor="w")
        c.create_text(64, cy + 9, text="VoxFlow • zwolnij klawisz aby zakończyć",
                      fill=self.GREY, font=("Segoe UI", 8), anchor="w")

        # ── Waveform bars (right section) ─────────────────────────
        num_bars = 28
        bar_w = 4
        bar_gap = 2
        bar_section_x = 240
        max_h = 22

        for i in range(num_bars):
            # Combine audio level with animated sine waves
            t = self._phase * 2.8 + i * 0.42
            wave1 = abs(math.sin(t))
            wave2 = abs(math.sin(t * 1.37 + 1.2)) * 0.5
            combined = wave1 * 0.55 + wave2 * 0.15

            # Boost by real audio level
            amp = (combined + self._level * 0.6) * max_h + 3
            amp = min(amp, max_h)

            x = bar_section_x + i * (bar_w + bar_gap)
            bar_cy = cy

            # Colour gradient: centre bars brighter
            ratio = amp / max_h
            if ratio > 0.75:
                color = self.RED
            elif ratio > 0.45:
                color = self.PURPLE
            else:
                color = self.PURPLE2

            # Draw symmetric bar
            c.create_rectangle(
                x, bar_cy - amp, x + bar_w, bar_cy + amp,
                fill=color, outline="",
            )
            # Rounded cap top
            c.create_oval(
                x, bar_cy - amp - 2, x + bar_w, bar_cy - amp + 2,
                fill=color, outline="",
            )

        try:
            if self._root:
                self._root.after(40, self._animate)
        except Exception:
            pass

    # ── Helper ────────────────────────────────────────────────────

    @staticmethod
    def _round_rect(canvas, x1, y1, x2, y2, r=12, **kw):
        """Draw a rounded rectangle on a tk Canvas."""
        canvas.create_arc(x1,     y1,     x1+2*r, y1+2*r, start=90,  extent=90,  style="pieslice", **kw)
        canvas.create_arc(x2-2*r, y1,     x2,     y1+2*r, start=0,   extent=90,  style="pieslice", **kw)
        canvas.create_arc(x1,     y2-2*r, x1+2*r, y2,     start=180, extent=90,  style="pieslice", **kw)
        canvas.create_arc(x2-2*r, y2-2*r, x2,     y2,     start=270, extent=90,  style="pieslice", **kw)
        canvas.create_rectangle(x1+r, y1,   x2-r, y2,   **kw)
        canvas.create_rectangle(x1,   y1+r, x1+r, y2-r, **kw)
        canvas.create_rectangle(x2-r, y1+r, x2,   y2-r, **kw)
