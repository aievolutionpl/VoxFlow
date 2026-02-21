"""VoxFlow Recording Overlay — minimalist indicator badge.

Created fresh on show(), destroyed completely on hide().
No persistent window, no fade tricks — guaranteed to appear
only during active recording.
"""
import math
import tkinter as tk
from typing import Optional


class RecordingOverlay:
    """Small badge shown at bottom-center of screen while recording."""

    W = 240
    H = 50
    BOTTOM_MARGIN = 70

    def __init__(self):
        self._win: Optional[tk.Toplevel] = None
        self._canvas: Optional[tk.Canvas] = None
        self._phase = 0.0
        self._level = 0.0
        self._running = False
        self._parent = None

    # ── Public API ────────────────────────────────────────────────

    def show(self, parent=None):
        """Show badge — creates a fresh window on every call."""
        if self._win is not None:
            return
        self._parent = parent
        self._running = True
        if parent:
            parent.after(0, self._create)

    def hide(self):
        """Destroy the badge window completely."""
        self._running = False
        if self._parent:
            self._parent.after(0, self._destroy)

    def set_level(self, level: float):
        """Set current audio amplitude (0.0 – 1.0)."""
        self._level = max(0.0, min(1.0, level))

    # ── Window ────────────────────────────────────────────────────

    def _create(self):
        if self._win is not None:
            return
        try:
            win = tk.Toplevel(self._parent)
            self._win = win

            win.overrideredirect(True)
            win.attributes("-topmost", True)
            win.attributes("-alpha", 0.95)

            sw = win.winfo_screenwidth()
            sh = win.winfo_screenheight()
            x = (sw - self.W) // 2
            y = sh - self.H - self.BOTTOM_MARGIN
            win.geometry(f"{self.W}x{self.H}+{x}+{y}")
            win.configure(bg="#120d2b")

            self._canvas = tk.Canvas(
                win,
                width=self.W, height=self.H,
                bg="#120d2b",
                highlightthickness=0,
                bd=0,
            )
            self._canvas.pack()

            self._tick()
        except Exception as e:
            print(f"[Overlay] Error: {e}")
            self._win = None
            self._canvas = None

    def _destroy(self):
        self._running = False
        try:
            if self._canvas:
                self._canvas.delete("all")
        except Exception:
            pass
        try:
            if self._win:
                self._win.destroy()
        except Exception:
            pass
        self._win = None
        self._canvas = None

    # ── Animation ─────────────────────────────────────────────────

    def _tick(self):
        if not self._running or not self._win or not self._canvas:
            return
        self._phase += 0.13
        self._draw()
        try:
            self._win.after(40, self._tick)
        except Exception:
            pass

    def _draw(self):
        c = self._canvas
        W, H = self.W, self.H
        c.delete("all")

        # Background with thin purple border
        c.create_rectangle(0, 0, W, H, fill="#120d2b", outline="#5b21b6", width=2)

        cy = H // 2

        # ── Pulsing red dot ───────────────────────────────────────
        pulse = (math.sin(self._phase * 3.5) + 1) / 2
        dot_x = 22
        outer_r = int(10 + pulse * 3)
        inner_r = 7

        # Outer glow
        c.create_oval(dot_x - outer_r, cy - outer_r,
                      dot_x + outer_r, cy + outer_r,
                      fill="#7f1d1d", outline="")
        # Core
        c.create_oval(dot_x - inner_r, cy - inner_r,
                      dot_x + inner_r, cy + inner_r,
                      fill="#ef4444", outline="")

        # ── Label ─────────────────────────────────────────────────
        c.create_text(42, cy - 8,
                      text="NAGRYWAM",
                      fill="#fca5a5",
                      font=("Segoe UI", 9, "bold"),
                      anchor="w")
        c.create_text(42, cy + 8,
                      text="zwolnij klawisz aby zakonczyc",
                      fill="#6b5e9b",
                      font=("Segoe UI", 7),
                      anchor="w")

        # ── 7 mini waveform bars ──────────────────────────────────
        n = 7
        bw = 5
        gap = 4
        total = n * bw + (n - 1) * gap
        x0 = W - total - 12

        for i in range(n):
            t = self._phase * 2.8 + i * 0.55
            wave = abs(math.sin(t)) * 0.65 + abs(math.sin(t * 0.6 + 1.0)) * 0.35
            amp = max(3, min(18, int((wave * 0.5 + self._level * 0.7) * 18)))

            x = x0 + i * (bw + gap)
            ratio = amp / 18
            col = "#f43f5e" if ratio > 0.75 else "#a78bfa" if ratio > 0.45 else "#7c3aed"

            c.create_rectangle(x, cy - amp, x + bw, cy + amp,
                                fill=col, outline="")
