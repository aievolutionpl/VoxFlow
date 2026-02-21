"""VoxFlow Recording Overlay – bottom-center waveform bar.

Uses CTkToplevel so it renders reliably on Windows without
canvas transparency tricks.

show()  – called when recording starts
hide()  – called when recording stops
set_level(0-1) – audio level (called from recorder callback)
"""
import math
import threading
import tkinter as tk
import customtkinter as ctk
from typing import Optional


class RecordingOverlay:
    """Elegant bottom-centre overlay shown only during recording."""

    W = 520
    H = 70
    BOTTOM_MARGIN = 80

    def __init__(self):
        self._win: Optional[ctk.CTkToplevel] = None
        self._canvas: Optional[tk.Canvas] = None
        self._alive = False
        self._phase = 0.0
        self._level = 0.0
        self._alpha = 0.0
        self._hiding = False
        self._parent = None
        self._after_id = None

    # ── Public API ────────────────────────────────────────────────

    def show(self, parent=None):
        """Make overlay visible – call from main thread."""
        if self._alive:
            return
        self._parent = parent
        self._alive = True
        self._hiding = False
        self._alpha = 0.0
        if parent:
            parent.after(0, self._create)

    def hide(self):
        """Start fade-out – call from main thread."""
        self._alive = False
        self._hiding = True

    def set_level(self, level: float):
        """Update audio amplitude for waveform (0.0–1.0)."""
        self._level = max(0.0, min(1.0, level))

    # ── Window lifecycle ──────────────────────────────────────────

    def _create(self):
        try:
            win = ctk.CTkToplevel(self._parent)
            self._win = win

            win.overrideredirect(True)
            win.attributes("-topmost", True)
            win.attributes("-alpha", 0.0)
            win.resizable(False, False)

            sw = win.winfo_screenwidth()
            sh = win.winfo_screenheight()
            x = (sw - self.W) // 2
            y = sh - self.H - self.BOTTOM_MARGIN
            win.geometry(f"{self.W}x{self.H}+{x}+{y}")

            # Dark panel background
            win.configure(fg_color="#0d0b1e")

            # Canvas fills entire window – draws waveform + mic dot
            self._canvas = tk.Canvas(
                win, width=self.W, height=self.H,
                bg="#0d0b1e", highlightthickness=0, bd=0,
            )
            self._canvas.pack(fill="both", expand=True)

            self._tick()
        except Exception as e:
            print(f"[Overlay] create error: {e}")

    def _destroy(self):
        try:
            if self._after_id and self._win:
                self._win.after_cancel(self._after_id)
        except Exception:
            pass
        try:
            if self._win:
                self._win.destroy()
        except Exception:
            pass
        self._win = None
        self._canvas = None
        self._hiding = False
        self._after_id = None

    # ── Animation ─────────────────────────────────────────────────

    def _tick(self):
        if not self._win or not self._canvas:
            return

        # Fade in / fade out
        if self._hiding:
            self._alpha = max(0.0, self._alpha - 0.085)
        elif self._alpha < 0.94:
            self._alpha = min(0.94, self._alpha + 0.07)

        try:
            self._win.attributes("-alpha", self._alpha)
        except Exception:
            return

        if self._hiding and self._alpha <= 0.0:
            if self._parent:
                self._parent.after(0, self._destroy)
            return

        self._phase += 0.11
        self._draw()

        try:
            self._after_id = self._win.after(35, self._tick)
        except Exception:
            pass

    # ── Drawing ───────────────────────────────────────────────────

    def _draw(self):
        c = self._canvas
        W, H = self.W, self.H
        c.delete("all")

        # ── Background panel with purple border ───────────────────
        # Outer glow (multiple rects, darker to lighter)
        for i, col in enumerate(["#2a1060", "#3d1a8a", "#5b21b6", "#7c3aed"]):
            pad = 3 - i if i < 3 else 0
            c.create_rectangle(pad, pad, W - pad, H - pad,
                                fill="", outline=col, width=1)

        # Filled dark panel
        c.create_rectangle(3, 3, W - 3, H - 3, fill="#100e28", outline="")

        # Top inner shine
        c.create_rectangle(4, 4, W - 4, 18, fill="#ffffff09", outline="")

        # ── Pulsing mic dot (left) ────────────────────────────────
        pulse = (math.sin(self._phase * 3.0) + 1) / 2
        cx, cy = 38, H // 2

        # Glow rings
        for ri, col in ((22, "#ef444415"), (16, "#ef444435"), (11, "#ef444465")):
            r = ri + pulse * 4
            c.create_oval(cx - r, cy - r, cx + r, cy + r,
                          fill=col, outline="")

        # Core dot
        dr = int(9 + pulse * 2)
        c.create_oval(cx - dr, cy - dr, cx + dr, cy + dr,
                      fill="#ef4444", outline="#fca5a5", width=1)

        # Mic icon inside
        c.create_oval(cx - 3, cy - 7, cx + 3, cy - 1, fill="white", outline="")
        c.create_line(cx, cy - 1, cx, cy + 5, fill="white", width=2)
        c.create_arc(cx - 6, cy - 3, cx + 6, cy + 7,
                     start=0, extent=-180, style="arc", outline="white", width=2)

        # ── Text ──────────────────────────────────────────────────
        c.create_text(62, cy - 10,
                      text="Nagrywam...",
                      fill="#fca5a5", font=("Segoe UI", 11, "bold"),
                      anchor="w")
        c.create_text(62, cy + 8,
                      text="VoxFlow  \u2022  zwolnij klawisz aby zakonczyc",
                      fill="#6b5e9b", font=("Segoe UI", 8),
                      anchor="w")

        # Thin vertical divider
        c.create_line(228, 14, 228, H - 14, fill="#3d2d6d", width=1)

        # ── Waveform bars ─────────────────────────────────────────
        n = 32
        bw, gap = 4, 2
        x0 = 236
        max_h = 22

        for i in range(n):
            x = x0 + i * (bw + gap)
            if x + bw > W - 6:
                break

            t = self._phase * 2.5 + i * 0.40
            wave = abs(math.sin(t)) * 0.6 + abs(math.sin(t * 0.73 + 1.1)) * 0.4
            amp = max(3, min(max_h, (wave * 0.45 + self._level * 0.70) * max_h))

            ratio = amp / max_h
            col = ("#f43f5e" if ratio > 0.78
                   else "#a78bfa" if ratio > 0.50
                   else "#7c3aed" if ratio > 0.28
                   else "#4c1d95")

            c.create_rectangle(x, cy - amp, x + bw, cy + amp,
                                fill=col, outline="")
            # Round top cap
            c.create_oval(x, cy - amp - 2, x + bw, cy - amp + 2,
                          fill=col, outline="")
