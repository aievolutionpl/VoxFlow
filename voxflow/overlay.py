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
            win.attributes("-alpha", 0.0)   # start invisible, fade in

            sw = win.winfo_screenwidth()
            sh = win.winfo_screenheight()
            x = (sw - self.W) // 2
            y = sh - self.H - self.MARGIN_BOTTOM
            win.geometry(f"{self.W}x{self.H}+{x}+{y}")

            # Match canvas background to panel color — no transparent key needed
            win.configure(bg="#0d0b1e")

            self._canvas = tk.Canvas(
                win, width=self.W, height=self.H,
                bg="#0d0b1e", highlightthickness=0,
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
            self._alpha = max(0.0, self._alpha - 0.08)
            try:
                self._root.attributes("-alpha", self._alpha)
            except Exception:
                pass
            if self._alpha <= 0.0:
                if self._parent:
                    self._parent.after(0, self._destroy_window)
                return
        elif self._alpha < 0.93:
            self._alpha = min(0.93, self._alpha + 0.07)
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

        # ── Border glow  (layered rectangles, outer→inner) ────────
        glow_colors = ["#3b1f6a", "#4c2181", "#5d28a0", "#6d28d9"]
        radii = [16, 14, 13, 12]
        for col, r in zip(glow_colors, radii):
            pad = radii[0] - r
            self._rrect(c, pad, pad, W - pad, H - pad, r=r, fill="", outline=col, width=2)

        # ── Glass panel fill ──────────────────────────────────────
        self._rrect(c, 3, 3, W - 3, H - 3, r=12,
                    fill="#100e28", outline="")

        # Inner top-shine strip
        self._rrect(c, 4, 4, W - 4, 4 + H // 3, r=11,
                    fill="#ffffff0a", outline="")

        # Thin bright border top-cap
        self._rrect(c, 3, 3, W - 3, H - 3, r=12,
                    fill="", outline="#7c3aed", width=1)

        # ── Pulsing record dot (left) ─────────────────────────────
        pulse = (math.sin(self._phase * 3.0) + 1) / 2
        cx, cy = 38, H // 2

        # Outer glow rings
        for ri, col in [(22, "#ef444418"), (16, "#ef444438"), (12, "#ef444470")]:
            r = ri + pulse * 4
            c.create_oval(cx - r, cy - r, cx + r, cy + r,
                          fill=col, outline="")

        # Core dot
        dr = 9 + pulse * 2
        c.create_oval(cx - dr, cy - dr, cx + dr, cy + dr,
                      fill="#ef4444", outline="#fca5a5", width=1)

        # Mic icon inside dot
        c.create_oval(cx - 3, cy - 6, cx + 3, cy, fill="white", outline="")
        c.create_line(cx, cy, cx, cy + 5, fill="white", width=2)
        c.create_line(cx - 4, cy + 5, cx + 4, cy + 5, fill="white", width=2)

        # ── Text ──────────────────────────────────────────────────
        c.create_text(62, cy - 9,
                      text="Nagrywam...",
                      fill="#fca5a5", font=("Segoe UI", 11, "bold"),
                      anchor="w")
        c.create_text(62, cy + 9,
                      text="VoxFlow  \u2022  zwolnij klawisz aby zakonczyc",
                      fill="#6d5fa0", font=("Segoe UI", 8),
                      anchor="w")

        # Thin separator line
        c.create_line(230, 12, 230, H - 12, fill="#3d2d70", width=1)

        # ── Waveform bars ─────────────────────────────────────────
        n_bars = 32
        bw = 4
        gap = 2
        x0 = 238
        max_h = 20

        for i in range(n_bars):
            if x0 + i * (bw + gap) > W - 8:
                break
            t = self._phase * 2.6 + i * 0.38
            wave = abs(math.sin(t)) * 0.6 + abs(math.sin(t * 0.7 + 1.1)) * 0.4
            amp = (wave * 0.45 + self._level * 0.7) * max_h + 3
            amp = min(amp, max_h)

            x = x0 + i * (bw + gap)

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
            c.create_rectangle(x, cy - amp, x + bw, cy + amp,
                                fill=col, outline="")
            # Rounded top cap
            c.create_oval(x - 1, cy - amp - 2, x + bw + 1, cy - amp + 2,
                          fill=col, outline="")

    # ── Helper ────────────────────────────────────────────────────

    @staticmethod
    def _rrect(canvas, x1, y1, x2, y2, r=12, **kw):
        """Draw a rounded rectangle on canvas."""
        # Clamp radius
        r = min(r, (x2 - x1) // 2, (y2 - y1) // 2)
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
            x1 + r, y1,
        ]
        canvas.create_polygon(points, smooth=True, **kw)
