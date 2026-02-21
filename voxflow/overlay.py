"""VoxFlow Recording Overlay - Bottom-center animated waveform bar.

Shows only while recording (show/hide called from app.py).
Built by AI Evolution Polska
"""
import threading
import math
import tkinter as tk
from typing import Optional


class RecordingOverlay:
    """Floating overlay that shows recording waveform at bottom-center of screen."""

    W = 520
    H = 68
    MARGIN_BOTTOM = 70

    def __init__(self):
        self._root: Optional[tk.Toplevel] = None
        self._canvas: Optional[tk.Canvas] = None
        self._alive = False
        self._phase = 0.0
        self._level = 0.0
        self._alpha = 0.0          # current opacity (for fade in/out)
        self._fading_out = False
        self._parent = None

    # ── Public API ────────────────────────────────────────────────

    def show(self, parent=None):
        """Show the overlay — called when recording starts."""
        if self._alive:
            return
        self._parent = parent
        self._alive = True
        self._fading_out = False
        self._alpha = 0.0
        if parent:
            parent.after(0, self._create_window)

    def hide(self):
        """Hide the overlay — called when recording stops."""
        self._alive = False
        self._fading_out = True

    def set_level(self, level: float):
        """Update audio level (0.0–1.0) for waveform animation."""
        self._level = min(1.0, max(0.0, level))

    # ── Window ────────────────────────────────────────────────────

    def _create_window(self):
        try:
            self._root = tk.Toplevel(self._parent)
            win = self._root
            win.overrideredirect(True)
            win.attributes("-topmost", True)
            win.attributes("-alpha", 0.0)          # start invisible, fade in
            win.attributes("-transparentcolor", "#010101")  # key-colour transparency

            sw = win.winfo_screenwidth()
            sh = win.winfo_screenheight()
            x = (sw - self.W) // 2
            y = sh - self.H - self.MARGIN_BOTTOM
            win.geometry(f"{self.W}x{self.H}+{x}+{y}")
            win.configure(bg="#010101")

            self._canvas = tk.Canvas(
                win, width=self.W, height=self.H,
                bg="#010101", highlightthickness=0,
            )
            self._canvas.pack()
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
        self._fading_out = False

    # ── Animation loop ────────────────────────────────────────────

    def _animate(self):
        if not self._canvas or not self._root:
            return

        # --- Fade in / fade out ---
        if self._fading_out:
            self._alpha = max(0.0, self._alpha - 0.07)
            try:
                self._root.attributes("-alpha", self._alpha)
            except Exception:
                pass
            if self._alpha <= 0.0:
                if self._parent:
                    self._parent.after(0, self._destroy_window)
                return
        elif self._alpha < 0.95:
            self._alpha = min(0.95, self._alpha + 0.06)
            try:
                self._root.attributes("-alpha", self._alpha)
            except Exception:
                pass

        self._phase += 0.11
        self._draw()

        try:
            self._root.after(35, self._animate)
        except Exception:
            pass

    def _draw(self):
        c = self._canvas
        W, H = self.W, self.H
        c.delete("all")

        # ── Outer glow (shadow layer) ─────────────────────────────
        # Subtle purple glow border drawn as stacked rounded rects
        for i in range(4, 0, -1):
            alpha_colors = ["#1a0a2e", "#1e0d38", "#220f42", "#26114a"]
            self._rrect(c, i, i, W - i, H - i, r=18, fill=alpha_colors[i-1], outline="")

        # ── Glass panel ───────────────────────────────────────────
        self._rrect(c, 3, 3, W - 3, H - 3, r=16,
                    fill="#0d0b1e", outline="#6d28d9", width=2)

        # Inner highlight line (top edge shine)
        self._rrect(c, 4, 4, W - 4, 18, r=14,
                    fill="#ffffff08", outline="")

        # ── Pulsing record dot (left) ─────────────────────────────
        pulse = (math.sin(self._phase * 3.0) + 1) / 2
        cx, cy = 38, H // 2

        # Outer glow rings
        for ri, col, fade in [(22, "#ef444420", 1.0),
                               (17, "#ef444440", 1.0),
                               (13, "#ef444480", 1.0)]:
            r = ri + pulse * 3
            c.create_oval(cx - r, cy - r, cx + r, cy + r,
                          fill=col, outline="")

        # Core dot
        dr = 9 + pulse * 2
        c.create_oval(cx - dr, cy - dr, cx + dr, cy + dr,
                      fill="#ef4444", outline="#fca5a5", width=1)

        # Tiny white mic icon inside dot
        c.create_oval(cx - 3, cy - 6, cx + 3, cy, fill="white", outline="")
        c.create_line(cx, cy, cx, cy + 5, fill="white", width=2)
        c.create_line(cx - 4, cy + 5, cx + 4, cy + 5, fill="white", width=2)

        # ── Text labels ───────────────────────────────────────────
        c.create_text(62, cy - 9,
                      text="Nagrywam...",
                      fill="#fca5a5", font=("Segoe UI", 11, "bold"),
                      anchor="w")
        c.create_text(62, cy + 8,
                      text="VoxFlow  \u2022  zwolnij klawisz aby zakonczyc",
                      fill="#7c6fa0", font=("Segoe UI", 8),
                      anchor="w")

        # ── Waveform bars (right section) ─────────────────────────
        n_bars = 30
        bw = 4
        gap = 2
        x0 = 230
        max_h = 20

        for i in range(n_bars):
            t = self._phase * 2.6 + i * 0.38
            wave = abs(math.sin(t)) * 0.6 + abs(math.sin(t * 0.7 + 1.1)) * 0.4
            amp = (wave * 0.5 + self._level * 0.65) * max_h + 3
            amp = min(amp, max_h)

            x = x0 + i * (bw + gap)
            bar_cy = cy

            # Gradient colour: low=purple, mid=violet, high=rose
            ratio = amp / max_h
            if ratio > 0.78:
                col = "#f43f5e"
            elif ratio > 0.50:
                col = "#a78bfa"
            elif ratio > 0.28:
                col = "#7c3aed"
            else:
                col = "#4c1d95"

            # Bar body
            c.create_rectangle(x, bar_cy - amp, x + bw, bar_cy + amp,
                                fill=col, outline="")
            # Rounded cap
            c.create_oval(x - 1, bar_cy - amp - 2, x + bw + 1, bar_cy - amp + 2,
                          fill=col, outline="")

        # ── Right accent line ─────────────────────────────────────
        rx = x0 + n_bars * (bw + gap) + 6
        c.create_line(rx, 12, rx, H - 12,
                      fill="#6d28d950", width=1)

    # ── Helper ────────────────────────────────────────────────────

    @staticmethod
    def _rrect(canvas, x1, y1, x2, y2, r=12, **kw):
        """Draw a rounded rectangle."""
        canvas.create_arc(x1,       y1,       x1+2*r, y1+2*r, start=90,  extent=90,  style="pieslice", **kw)
        canvas.create_arc(x2 - 2*r, y1,       x2,     y1+2*r, start=0,   extent=90,  style="pieslice", **kw)
        canvas.create_arc(x1,       y2 - 2*r, x1+2*r, y2,     start=180, extent=90,  style="pieslice", **kw)
        canvas.create_arc(x2 - 2*r, y2 - 2*r, x2,     y2,     start=270, extent=90,  style="pieslice", **kw)
        canvas.create_rectangle(x1 + r, y1,     x2 - r, y2,     **kw)
        canvas.create_rectangle(x1,     y1 + r, x1 + r, y2 - r, **kw)
        canvas.create_rectangle(x2 - r, y1 + r, x2,     y2 - r, **kw)
