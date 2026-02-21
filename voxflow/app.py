"""VoxFlow Main Application - Premium Desktop UI with Hold-to-Record.

Built by AI Evolution Polska
https://github.com/aievolutionpl/VoxFlow
"""
import threading
import time
import math
from datetime import datetime
from typing import Optional
import customtkinter as ctk
import pyperclip
import numpy as np

from voxflow.config import VoxFlowConfig
from voxflow.recorder import AudioRecorder
from voxflow.transcriber import VoxTranscriber
from voxflow.hotkey_manager import HotkeyManager
from voxflow.auto_typer import AutoTyper
from voxflow import sounds
from voxflow.overlay import RecordingOverlay
from voxflow import __version__, __author__

# Optional modules — gracefully degrade if unavailable
try:
    from voxflow.tray import TrayManager
    _TRAY_AVAILABLE = True
except Exception:
    _TRAY_AVAILABLE = False

try:
    from voxflow.autostart import set_autostart, is_autostart_enabled
    _AUTOSTART_AVAILABLE = True
except Exception:
    _AUTOSTART_AVAILABLE = False
    def set_autostart(_enabled: bool) -> None: pass
    def is_autostart_enabled() -> bool: return False


# ─── Color Palette ────────────────────────────────────────────────────────────
C = {
    "bg":           "#09091a",
    "bg_card":      "#12122b",
    "bg_hover":     "#1a1a3a",
    "bg_input":     "#0e0e22",
    "accent":       "#7c3aed",
    "accent2":      "#a78bfa",
    "accent3":      "#c4b5fd",
    "accent_dim":   "#5b21b6",
    "accent_glow":  "#4c1d95",
    "rec_red":      "#ef4444",
    "rec_glow":     "#dc2626",
    "ok":           "#22c55e",
    "warn":         "#f59e0b",
    "txt":          "#f1f5f9",
    "txt2":         "#94a3b8",
    "txt3":         "#475569",
    "border":       "#1e1e42",
    "border2":      "#2d2d5e",
}


class VoxFlowApp(ctk.CTk):
    """Main VoxFlow application window."""

    def __init__(self):
        super().__init__()

        self.config = VoxFlowConfig.load()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("VoxFlow")
        self.geometry(f"{self.config.window_width}x{self.config.window_height}")
        self.minsize(460, 700)
        self.configure(fg_color=C["bg"])

        # ─── State ────────────────────────────────────────────────
        self._recording = False
        self._processing = False
        self._level = 0.0
        self._phase = 0.0
        self._history: list[dict] = []
        self._alive = True
        self._settings_visible = False
        self._capturing_hotkey = False
        self._audio_devices: list[dict] = []

        # ─── Engine ───────────────────────────────────────────────
        self.recorder = AudioRecorder(
            sample_rate=self.config.sample_rate,
            channels=self.config.channels,
            silence_threshold=self.config.silence_threshold,
            silence_duration=self.config.silence_duration,
            max_duration=self.config.max_recording_duration,
            device_index=self.config.audio_device_index,
            on_level_change=self._on_level,
            on_device_fallback=self._on_device_fallback,
        )

        self.transcriber = VoxTranscriber(
            model_size=self.config.model_size,
            device=self.config.device,
            compute_type=self.config.compute_type,
        )

        self.hotkey_manager = HotkeyManager(
            hotkey=self.config.hotkey,
            on_press=self._on_hotkey_press,
            on_release=self._on_hotkey_release,
        )

        if _TRAY_AVAILABLE:
            self.tray = TrayManager(
                on_show=self._show,
                on_toggle_recording=lambda: self.after(0, self._toggle_recording),
                on_quit=self._quit,
            )
        else:
            self.tray = None

        self.auto_typer = AutoTyper()
        self.overlay = RecordingOverlay()

        # ─── Build ────────────────────────────────────────────────
        self._load_audio_devices()
        self._build_ui()
        self._start_services()

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Configure>", self._on_window_configure)
        self._animate()

    # ═══════════════════════════════════════════════════════════════
    # DEVICE ENUMERATION
    # ═══════════════════════════════════════════════════════════════

    def _load_audio_devices(self):
        """Load list of available audio input devices."""
        try:
            self._audio_devices = AudioRecorder.list_devices()
        except Exception:
            self._audio_devices = []

    def _get_device_names(self) -> list[str]:
        """Return device display names for UI dropdown."""
        names = ["🎤 Domyślny mikrofon"]
        for d in self._audio_devices:
            name = d["name"]
            if len(name) > 38:
                name = name[:35] + "..."
            names.append(f"[{d['index']}] {name}")
        return names

    def _get_current_device_label(self) -> str:
        """Get label for the currently selected device."""
        idx = self.config.audio_device_index
        if idx < 0:
            return "🎤 Domyślny mikrofon"
        for d in self._audio_devices:
            if d["index"] == idx:
                name = d["name"]
                if len(name) > 38:
                    name = name[:35] + "..."
                return f"[{idx}] {name}"
        return "🎤 Domyślny mikrofon"

    # ═══════════════════════════════════════════════════════════════
    # UI BUILDER
    # ═══════════════════════════════════════════════════════════════

    def _build_ui(self):
        # Outer scrollable container
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.pack(fill="both", expand=True, padx=18, pady=(8, 6))

        self._build_header()
        self._build_record_btn()
        self._build_level_bar()
        self._build_mic_selector()
        self._build_status()
        self._build_transcript()
        self._build_quick_controls()
        self._build_history()
        self._build_settings_panel()
        self._build_footer()

    # ── Header ───────────────────────────────────────────────────

    def _build_header(self):
        f = ctk.CTkFrame(self.main, fg_color="transparent")
        f.pack(fill="x", pady=(6, 4))

        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x")

        # Logo + title
        logo_frame = ctk.CTkFrame(row, fg_color="transparent")
        logo_frame.pack(side="left")

        ctk.CTkLabel(
            logo_frame, text="🎤",
            font=ctk.CTkFont(size=28),
        ).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            logo_frame, text="VoxFlow",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=C["txt"],
        ).pack(side="left")

        ctk.CTkLabel(
            logo_frame, text=f"v{__version__}",
            font=ctk.CTkFont(size=10),
            text_color=C["accent3"],
            fg_color=C["bg_card"],
            corner_radius=6,
            padx=6, pady=1,
        ).pack(side="left", padx=(8, 0), pady=(4, 0))

        # Right buttons
        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(side="right")

        self.settings_btn = ctk.CTkButton(
            btn_frame, text="⚙", width=34, height=34,
            font=ctk.CTkFont(size=15),
            fg_color=C["bg_card"], hover_color=C["accent_dim"],
            border_width=1, border_color=C["border2"],
            corner_radius=10, command=self._toggle_settings,
        )
        self.settings_btn.pack(side="right")

        # Subtitle
        hk_display = self.config.hotkey.upper().replace("+", " + ")
        self.subtitle_label = ctk.CTkLabel(
            f,
            text=f"Przytrzymaj {hk_display} aby dyktować  •  100% offline",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=C["txt3"],
        )
        self.subtitle_label.pack(anchor="w", pady=(2, 0))

        # Thin separator line
        ctk.CTkFrame(self.main, fg_color=C["border"], height=1).pack(fill="x", pady=(4, 0))

    # ── Record Button (canvas) ────────────────────────────────────

    def _build_record_btn(self):
        f = ctk.CTkFrame(self.main, fg_color="transparent")
        f.pack(fill="x", pady=(14, 4))

        sz = 160
        self.canvas = ctk.CTkCanvas(
            f, width=sz, height=sz,
            bg=C["bg"], highlightthickness=0,
        )
        self.canvas.pack()
        self.canvas.bind("<ButtonPress-1>", lambda e: self._start_rec())
        self.canvas.bind("<ButtonRelease-1>", lambda e: self._stop_rec())
        self._csz = sz
        self._draw_btn()

    def _draw_btn(self):
        self.canvas.delete("all")
        cx = cy = self._csz // 2
        r = 55

        if self._recording:
            # Outer glow rings
            for i in range(3):
                p = self._phase + i * 0.9
                er = r + 12 + i * 12 + ((math.sin(p) + 1) / 2) * 8
                alpha_hex = ["40", "28", "18"][i]
                self.canvas.create_oval(
                    cx - er, cy - er, cx + er, cy + er,
                    fill="", outline=C["rec_red"], width=max(1, 3 - i)
                )
            # Main circle
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=C["rec_red"], outline="#b91c1c", width=3,
            )
            # Waveform bars
            for i in range(9):
                bx = cx - 28 + i * 7
                amp = abs(math.sin(self._phase * 2 + i * 0.65)) * 20 + 5
                lvl_boost = self._level * 15
                amp = min(amp + lvl_boost, 26)
                self.canvas.create_rectangle(
                    bx - 2, cy - amp, bx + 2, cy + amp,
                    fill="white", outline="",
                )

        elif self._processing:
            # Processing spinner
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=C["warn"], outline="#b45309", width=3,
            )
            for i in range(8):
                a = self._phase * 3 + i * (math.pi / 4)
                dx = cx + math.cos(a) * 28
                dy = cy + math.sin(a) * 28
                size = 5 - i * 0.3
                self.canvas.create_oval(
                    dx - size, dy - size, dx + size, dy + size,
                    fill="white", outline="",
                )
            self.canvas.create_text(
                cx, cy, text="AI",
                fill="white",
                font=("Segoe UI", 13, "bold"),
            )

        else:
            # Idle — gentle pulse
            gf = (math.sin(self._phase * 0.35) + 1) / 2
            # Outer glow
            gr = r + 6 + gf * 6
            self.canvas.create_oval(
                cx - gr, cy - gr, cx + gr, cy + gr,
                fill="", outline=C["accent"], width=2,
            )
            # Second glow ring
            gr2 = r + 2 + gf * 3
            self.canvas.create_oval(
                cx - gr2, cy - gr2, cx + gr2, cy + gr2,
                fill="", outline=C["accent2"], width=1,
            )
            # Main circle
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=C["accent"], outline=C["accent2"], width=3,
            )
            # Mic body
            self.canvas.create_oval(cx - 11, cy - 26, cx + 11, cy + 2, fill="white", outline="")
            # Mic stand
            self.canvas.create_line(cx, cy + 2, cx, cy + 16, fill="white", width=3)
            self.canvas.create_line(cx - 11, cy + 16, cx + 11, cy + 16, fill="white", width=3)
            # Mic arc
            self.canvas.create_arc(
                cx - 18, cy - 14, cx + 18, cy + 10,
                start=200, extent=140, style="arc", outline="white", width=2,
            )

    # ── Level Bar ─────────────────────────────────────────────────

    def _build_level_bar(self):
        f = ctk.CTkFrame(self.main, fg_color="transparent")
        f.pack(fill="x", pady=(0, 2))
        self.level_bar = ctk.CTkProgressBar(
            f, height=4, corner_radius=2,
            fg_color=C["bg_card"],
            progress_color=C["accent"],
            border_width=0,
        )
        self.level_bar.pack(fill="x", padx=30)
        self.level_bar.set(0)

    # ── Microphone Selector ───────────────────────────────────────

    def _build_mic_selector(self):
        card = ctk.CTkFrame(
            self.main, fg_color=C["bg_card"],
            corner_radius=10,
            border_width=1, border_color=C["border"],
        )
        card.pack(fill="x", pady=(6, 4))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=8)

        ctk.CTkLabel(
            inner, text="🎙 Mikrofon",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=C["txt2"],
        ).pack(side="left", padx=(0, 8))

        device_names = self._get_device_names()
        current = self._get_current_device_label()
        if current not in device_names:
            current = device_names[0]

        self.mic_var = ctk.StringVar(value=current)
        self.mic_menu = ctk.CTkOptionMenu(
            inner,
            values=device_names,
            variable=self.mic_var,
            font=ctk.CTkFont(size=11),
            fg_color=C["bg_input"],
            button_color=C["accent_dim"],
            button_hover_color=C["accent"],
            dropdown_fg_color=C["bg_card"],
            corner_radius=8,
            command=self._on_mic_change,
            dynamic_resizing=False,
            width=280,
        )
        self.mic_menu.pack(side="right", expand=True, fill="x", padx=(0, 0))

    # ── Status Label ──────────────────────────────────────────────

    def _build_status(self):
        f = ctk.CTkFrame(self.main, fg_color="transparent")
        f.pack(fill="x", pady=(4, 6))
        hk = self.config.hotkey.upper().replace("+", " + ")
        self.status = ctk.CTkLabel(
            f,
            text=f"✨ Gotowy — Przytrzymaj {hk} lub kliknij przycisk",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=C["txt2"],
        )
        self.status.pack()

    # ── Transcript Box ────────────────────────────────────────────

    def _build_transcript(self):
        card = ctk.CTkFrame(
            self.main, fg_color=C["bg_card"],
            corner_radius=12,
            border_width=1, border_color=C["border"],
        )
        card.pack(fill="both", expand=True, pady=(0, 6))

        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=14, pady=(10, 0))

        ctk.CTkLabel(
            head, text="📝 Transkrypcja",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=C["txt2"],
        ).pack(side="left")

        btn_row = ctk.CTkFrame(head, fg_color="transparent")
        btn_row.pack(side="right")

        ctk.CTkButton(
            btn_row, text="🗑", width=30, height=26,
            font=ctk.CTkFont(size=11),
            fg_color=C["bg_hover"], hover_color=C["rec_red"],
            corner_radius=8, command=self._clear_transcript,
        ).pack(side="right", padx=(4, 0))

        ctk.CTkButton(
            btn_row, text="📋 Kopiuj", width=80, height=26,
            font=ctk.CTkFont(size=11),
            fg_color=C["bg_hover"], hover_color=C["accent"],
            corner_radius=8, command=self._copy_text,
        ).pack(side="right")

        self.textbox = ctk.CTkTextbox(
        card,
        font=ctk.CTkFont(family="Segoe UI", size=14),
        fg_color="transparent",
        text_color=C["txt"],
        wrap="word", height=90, border_width=0,
    )
    self.textbox.pack(fill="both", expand=True, padx=14, pady=(6, 10))
    self.textbox.insert("1.0", "Twój tekst pojawi się tutaj — możesz go edytować przed skopiowaniem...")

    # ── Quick Controls (language / model / hotkey) ─────────────────

    def _build_quick_controls(self):
        card = ctk.CTkFrame(
            self.main, fg_color=C["bg_card"],
            corner_radius=12,
            border_width=1, border_color=C["border"],
        )
        card.pack(fill="x", pady=(0, 6))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)

        # Language
        lf = ctk.CTkFrame(inner, fg_color="transparent")
        lf.pack(side="left", expand=True, fill="x", padx=(0, 5))
        ctk.CTkLabel(lf, text="🌍 Język", font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=C["txt3"]).pack(anchor="w")
        self.lang_var = ctk.StringVar(value=self.config.language)
        ctk.CTkOptionMenu(
            lf, values=["auto", "pl", "en"],
            variable=self.lang_var,
            font=ctk.CTkFont(size=11),
            fg_color=C["bg_input"],
            button_color=C["accent_dim"],
            button_hover_color=C["accent"],
            dropdown_fg_color=C["bg_card"],
            corner_radius=8,
            command=self._on_lang,
        ).pack(fill="x", pady=(3, 0))

        # Model
        mf = ctk.CTkFrame(inner, fg_color="transparent")
        mf.pack(side="left", expand=True, fill="x", padx=(5, 5))
        ctk.CTkLabel(mf, text="🧠 Model", font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=C["txt3"]).pack(anchor="w")
        self.model_var = ctk.StringVar(value=self.config.model_size)
        ctk.CTkOptionMenu(
            mf, values=self.config.available_models,
            variable=self.model_var,
            font=ctk.CTkFont(size=11),
            fg_color=C["bg_input"],
            button_color=C["accent_dim"],
            button_hover_color=C["accent"],
            dropdown_fg_color=C["bg_card"],
            corner_radius=8,
            command=self._on_model,
        ).pack(fill="x", pady=(3, 0))

        # Hotkey picker
        hf = ctk.CTkFrame(inner, fg_color="transparent")
        hf.pack(side="left", expand=True, fill="x", padx=(5, 0))
        ctk.CTkLabel(hf, text="⌨️ Klawisz", font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=C["txt3"]).pack(anchor="w")
        self.hotkey_btn = ctk.CTkButton(
            hf,
            text=self.config.hotkey.upper().replace("+", "+"),
            height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=C["bg_input"],
            hover_color=C["accent_dim"],
            border_width=1,
            border_color=C["border2"],
            corner_radius=8,
            command=self._start_hotkey_capture,
        )
        self.hotkey_btn.pack(fill="x", pady=(3, 0))

    # ── History ───────────────────────────────────────────────────

    def _build_history(self):
        card = ctk.CTkFrame(
            self.main, fg_color=C["bg_card"],
            corner_radius=12,
            border_width=1, border_color=C["border"],
        )
        card.pack(fill="x", pady=(0, 6))

        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            head, text="📚 Historia",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=C["txt2"],
        ).pack(side="left")

        ctk.CTkButton(
            head, text="🗑", width=30, height=26,
            font=ctk.CTkFont(size=10),
            fg_color=C["bg_hover"],
            hover_color=C["rec_red"],
            corner_radius=6,
            command=self._clear_history,
        ).pack(side="right")

        self.hist_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.hist_frame.pack(fill="x", padx=12, pady=(0, 10))

        ctk.CTkLabel(
            self.hist_frame, text="Brak nagrań",
            font=ctk.CTkFont(size=11), text_color=C["txt3"],
        ).pack(pady=4)

    # ── Settings Panel ────────────────────────────────────────────

    def _build_settings_panel(self):
        """Build the collapsible advanced settings panel."""
        self.settings_frame = ctk.CTkFrame(
            self.main, fg_color=C["bg_card"],
            corner_radius=12,
            border_width=1, border_color=C["accent_dim"],
        )
        self._settings_visible = False

        inner = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=12)

        ctk.CTkLabel(
            inner, text="⚙️ Ustawienia zaawansowane",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=C["txt"],
        ).pack(anchor="w", pady=(0, 10))

        def sw_row(parent, label, var, cmd):
            r = ctk.CTkFrame(parent, fg_color="transparent")
            r.pack(fill="x", pady=3)
            ctk.CTkLabel(r, text=label, font=ctk.CTkFont(size=12),
                         text_color=C["txt2"]).pack(side="left")
            ctk.CTkSwitch(r, text="", variable=var,
                          fg_color=C["bg_hover"], progress_color=C["accent"],
                          button_color=C["txt"], button_hover_color=C["accent3"],
                          command=cmd).pack(side="right")

        def opt_row(parent, label, values, var, cmd, width=130):
            r = ctk.CTkFrame(parent, fg_color="transparent")
            r.pack(fill="x", pady=3)
            ctk.CTkLabel(r, text=label, font=ctk.CTkFont(size=12),
                         text_color=C["txt2"]).pack(side="left")
            ctk.CTkOptionMenu(r, values=values, variable=var, width=width,
                              font=ctk.CTkFont(size=11),
                              fg_color=C["bg_input"], button_color=C["accent_dim"],
                              button_hover_color=C["accent"],
                              dropdown_fg_color=C["bg_card"],
                              corner_radius=8, command=cmd).pack(side="right")

        self.autotype_var = ctk.BooleanVar(value=self.config.auto_type_enabled)
        sw_row(inner, "✍️ Auto-wpisywanie tekstu", self.autotype_var, self._on_autotype_toggle)

        self.typemethod_var = ctk.StringVar(value=self.config.typing_method)
        opt_row(inner, "📋 Metoda wpisywania", ["clipboard", "keyboard"],
                self.typemethod_var, self._on_typemethod)

        self.autocopy_var = ctk.BooleanVar(value=self.config.auto_copy_to_clipboard)
        sw_row(inner, "📎 Auto-kopiowanie do schowka", self.autocopy_var, self._on_autocopy_toggle)

        self.tray_var = ctk.BooleanVar(value=self.config.minimize_to_tray)
        sw_row(inner, "🔲 Minimalizuj do zasobnika", self.tray_var, self._on_tray_toggle)

        self.notify_var = ctk.BooleanVar(value=self.config.show_notifications)
        sw_row(inner, "🔔 Powiadomienia", self.notify_var, self._on_notify_toggle)

        self.vad_var = ctk.BooleanVar(value=self.config.vad_enabled)
        sw_row(inner, "🎯 Detekcja mowy (VAD)", self.vad_var, self._on_vad_toggle)

        self.beam_var = ctk.StringVar(value=str(self.config.beam_size))
        opt_row(inner, "🔬 Beam size (dokładność)", ["1", "3", "5", "8", "10"],
                self.beam_var, self._on_beam_change, width=80)

        self.autocorrect_var = ctk.BooleanVar(value=self.config.auto_correct)
        sw_row(inner, "✨ Autokorekta tekstu", self.autocorrect_var, self._on_autocorrect_toggle)

        self.sounds_var = ctk.BooleanVar(value=self.config.play_sounds)
        sw_row(inner, "🔊 Dźwięki nagrywania", self.sounds_var, self._on_sounds_toggle)

        self.autostart_var = ctk.BooleanVar(value=is_autostart_enabled())
        sw_row(inner, "🚀 Uruchamiaj z Windows", self.autostart_var, self._on_autostart_toggle)

        # ── Color theme selector ───────────────────────
        ctk.CTkFrame(inner, fg_color=C["border"], height=1).pack(fill="x", pady=(10, 8))

        ctk.CTkLabel(
            inner, text="🎨 Motyw kolorów",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=C["txt2"],
        ).pack(anchor="w", pady=(0, 6))

        theme_row = ctk.CTkFrame(inner, fg_color="transparent")
        theme_row.pack(fill="x")

        THEMES = [
            ("Fioletowy", "#7c3aed", "#09091a"),
            ("Niebieski",  "#1d4ed8", "#080e1a"),
            ("Zielony",   "#059669", "#08130f"),
        ]

        def _apply_theme(accent, bg):
            C["accent"] = accent
            C["accent2"] = accent
            C["accent_dim"] = accent
            C["bg"] = bg
            self.configure(fg_color=bg)
            self.config.save()

        for label, accent, bg in THEMES:
            ctk.CTkButton(
                theme_row, text=label, width=100, height=30,
                font=ctk.CTkFont(size=11),
                fg_color=accent, hover_color=accent,
                corner_radius=8,
                command=lambda a=accent, b=bg: _apply_theme(a, b),
            ).pack(side="left", padx=(0, 6))

        ctk.CTkFrame(inner, fg_color=C["border"], height=1).pack(fill="x", pady=(10, 6))

        ctk.CTkLabel(
            inner,
            text="💡 Wskazówka: Użyj Ctrl+Space lub F2–F10 jako klawisz dyktowania.\n"
                 "     Model 'small' = dobry balans jakości i szybkości.",
            font=ctk.CTkFont(size=10),
            text_color=C["txt3"],
            justify="left",
        ).pack(anchor="w")


    # ── Footer ────────────────────────────────────────────────────

    def _build_footer(self):
        self.footer_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        self.footer_frame.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            self.footer_frame,
            text=f"VoxFlow v{__version__}  •  faster-whisper  •  100% lokalne",
            font=ctk.CTkFont(size=9),
            text_color=C["txt3"],
        ).pack()

        ctk.CTkLabel(
            self.footer_frame,
            text=f"Open Source  •  {__author__}",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=C["accent_dim"],
        ).pack(pady=(1, 0))

    # ═══════════════════════════════════════════════════════════════
    # SETTINGS TOGGLE
    # ═══════════════════════════════════════════════════════════════

    def _toggle_settings(self):
        if self._settings_visible:
            self.settings_frame.pack_forget()
            self._settings_visible = False
            self.settings_btn.configure(fg_color=C["bg_card"])
        else:
            self.settings_frame.pack(
                fill="x", pady=(0, 6),
                before=self.footer_frame,  # Always insert just before footer
            )
            self._settings_visible = True
            self.settings_btn.configure(fg_color=C["accent_dim"])

    # ═══════════════════════════════════════════════════════════════
    # ANIMATION
    # ═══════════════════════════════════════════════════════════════

    def _animate(self):
        if not self._alive:
            return
        self._phase += 0.10
        self._draw_btn()

        target = self._level if self._recording else 0
        cur = self.level_bar.get()
        if self._recording:
            self.level_bar.set(min(1.0, cur + (target - cur) * 0.3) * 5)
        else:
            self.level_bar.set(max(0.0, cur * 0.8))
        self.level_bar.configure(
            progress_color=C["rec_red"] if self._recording else C["accent"]
        )

        self.after(50, self._animate)

    # ═══════════════════════════════════════════════════════════════
    # HOTKEY CAPTURE (interactive)
    # ═══════════════════════════════════════════════════════════════

    def _start_hotkey_capture(self):
        """Start interactive hotkey capture — next key press becomes the hotkey."""
        if self._capturing_hotkey or self._recording:
            return
        self._capturing_hotkey = True
        self.hotkey_btn.configure(
            text="⌨️ Naciśnij klawisz...",
            fg_color=C["accent_dim"],
            border_color=C["accent"],
        )
        self.hotkey_manager.stop()
        threading.Thread(target=self._capture_hotkey_thread, daemon=True).start()

    def _capture_hotkey_thread(self):
        """Wait for key press in background thread."""
        key = self.hotkey_manager.capture_next_key(timeout=10.0)
        self.after(0, lambda: self._finish_hotkey_capture(key))

    def _finish_hotkey_capture(self, key: Optional[str]):
        """Apply captured key as new hotkey."""
        self._capturing_hotkey = False
        if key:
            self.config.hotkey = key
            self.config.save()
            # BUGFIX: update_hotkey checks was_active which is False after stop(),
            # so we update the key manually and always call start().
            self.hotkey_manager.hotkey = key.lower()
            self.hotkey_manager._is_combo = "+" in key
            self.hotkey_manager.start()
            display = key.upper().replace("+", " + ")
            self.hotkey_btn.configure(
                text=display,
                fg_color=C["bg_input"],
                border_color=C["ok"],
            )
            self.subtitle_label.configure(
                text=f"Przytrzymaj {display} aby dyktować  •  100% offline"
            )
            hk_disp = key.upper().replace("+", " + ")
            self.status.configure(
                text=f"⌨️ Hotkey ustawiony: {hk_disp}", text_color=C["ok"]
            )
            # Reset border after 2s
            self.after(2000, lambda: self.hotkey_btn.configure(border_color=C["border2"]))
        else:
            # Cancelled / timeout — restart with old hotkey
            self.hotkey_btn.configure(
                text=self.config.hotkey.upper().replace("+", " + "),
                fg_color=C["bg_input"],
                border_color=C["border2"],
            )
            self.hotkey_manager.start()

    # ═══════════════════════════════════════════════════════════════
    # MICROPHONE SELECTION
    # ═══════════════════════════════════════════════════════════════

    def _on_mic_change(self, label: str):
        """Handle microphone device selection change."""
        if label.startswith("🎤 Domyślny"):
            idx = -1
        else:
            try:
                idx = int(label.split("]")[0].replace("[", "").strip())
            except (ValueError, IndexError):
                idx = -1

        self.config.audio_device_index = idx
        self.config.save()
        self.recorder.set_device(idx)

        dev_name = label if idx < 0 else label[label.index("]") + 2:]
        self.status.configure(
            text=f"🎙 Mikrofon: {dev_name[:40]}", text_color=C["ok"]
        )

    def _on_device_fallback(self, fallback_index: int):
        """Called by AudioRecorder when it falls back to the default device."""
        self.config.audio_device_index = fallback_index
        self.config.save()
        # Update mic dropdown to show "Domyślny mikrofon"
        self.after(0, lambda: (
            self.mic_var.set("🎤 Domyślny mikrofon")
            if hasattr(self, "mic_var") else None
        ))
        self.after(
            0,
            lambda: self.status.configure(
                text="⚠️ Mikrofon niedostępny, przełączono na domyślny",
                text_color=C["warn"],
            ),
        )

    def _on_window_configure(self, event=None):
        """Save window dimensions whenever the window is resized.

        Debounced: cancels any pending save and schedules a new one
        400 ms after the last resize event.
        """
        if hasattr(self, "_resize_job") and self._resize_job:
            try:
                self.after_cancel(self._resize_job)
            except Exception:
                pass
        self._resize_job = self.after(400, self._save_window_size)

    def _save_window_size(self):
        """Persist the current window dimensions to config."""
        try:
            w = self.winfo_width()
            h = self.winfo_height()
            if w > 100 and h > 100:  # sanity check
                self.config.window_width = w
                self.config.window_height = h
                self.config.save()
        except Exception:
            pass
        self._resize_job = None

    # ═══════════════════════════════════════════════════════════════
    # RECORDING (Hold-to-Record)
    # ═══════════════════════════════════════════════════════════════

    def _on_hotkey_press(self):
        self.after(0, self._start_rec)

    def _on_hotkey_release(self):
        self.after(0, self._stop_rec)

    def _toggle_recording(self):
        if self._processing:
            return
        if self._recording:
            self._stop_rec()
        else:
            self._start_rec()

    def _start_rec(self):
        if self._recording or self._processing or self._capturing_hotkey:
            return
        self._recording = True
        self.status.configure(text="🔴 Nagrywam... Mów teraz!", text_color=C["rec_red"])
        if self.tray:
            self.tray.set_recording(True)
        if self.config.play_sounds:
            sounds.play("start")
        self.overlay.show(self)
        self.recorder.start()

    def _stop_rec(self):
        if not self._recording:
            return
        self._recording = False
        self._processing = True
        if self.tray:
            self.tray.set_recording(False)
        self.overlay.hide()
        if self.config.play_sounds:
            sounds.play("stop")
        self.status.configure(text="⏳ Transkrybuję...", text_color=C["warn"])

        audio = self.recorder.stop()
        if audio is None or len(audio) < self.config.sample_rate * 0.3:
            self._processing = False
            self.status.configure(text="⚠️ Za krótkie nagranie", text_color=C["warn"])
            return

        threading.Thread(target=self._transcribe, args=(audio,), daemon=True).start()

    def _transcribe(self, audio: np.ndarray):
        try:
            result = self.transcriber.transcribe(
                audio,
                language=self.lang_var.get(),
                beam_size=self.config.beam_size,
                vad_enabled=self.config.vad_enabled,
                auto_correct=self.config.auto_correct,
                on_progress=lambda m: self.after(
                    0, lambda msg=m: self.status.configure(text=msg)
                ),
            )
            self.after(0, lambda: self._on_done(result))
        except Exception as e:
            self.after(0, lambda: self._on_error(str(e)))

    def _on_done(self, result: dict):
        self._processing = False
        text = result.get("text", "").strip()
        if not text:
            self.status.configure(text="🤔 Nie rozpoznano mowy", text_color=C["warn"])
            return

        # Update transcript box (always editable — user can fix before copying)
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text)

        # Auto-copy
        if self.config.auto_copy_to_clipboard:
            try:
                pyperclip.copy(text)
            except Exception:
                pass

        # Auto-type into active window
        if self.config.auto_type_enabled:
            threading.Thread(
                target=self._delayed_auto_type,
                args=(text,),
                daemon=True,
            ).start()

        lang = result.get("language", "?")
        flag = "🇵🇱" if lang == "pl" else "🇬🇧" if lang == "en" else "🌍"
        dur = result.get("duration", 0)
        extras = []
        if self.config.auto_type_enabled:
            extras.append("✍️")
        if self.config.auto_copy_to_clipboard:
            extras.append("📋")
        extra_str = " • " + " ".join(extras) if extras else ""
        self.status.configure(
            text=f"✅ {flag} {lang.upper()} • {dur:.1f}s{extra_str}",
            text_color=C["ok"],
        )
        if self.config.play_sounds:
            sounds.play("done")

        self._add_history(text, lang, dur)

    def _delayed_auto_type(self, text: str):
        time.sleep(0.15)
        self.auto_typer.type_text(text, method=self.config.typing_method)

    def _on_error(self, err: str):
        self._processing = False
        self.status.configure(text=f"❌ {err[:70]}", text_color=C["rec_red"])
        if self.config.play_sounds:
            sounds.play("error")

    # ═══════════════════════════════════════════════════════════════
    # HISTORY
    # ═══════════════════════════════════════════════════════════════

    def _add_history(self, text: str, lang: str, dur: float):
        self._history.insert(0, {
            "text": text, "language": lang,
            "duration": dur,
            "time": datetime.now().strftime("%H:%M"),
        })
        if len(self._history) > 20:
            self._history = self._history[:20]
        self._refresh_history()

    def _refresh_history(self):
        for w in self.hist_frame.winfo_children():
            w.destroy()
        if not self._history:
            ctk.CTkLabel(
                self.hist_frame, text="Brak nagrań",
                font=ctk.CTkFont(size=11), text_color=C["txt3"],
            ).pack(pady=4)
            return
        for e in self._history[:6]:
            row = ctk.CTkFrame(
                self.hist_frame, fg_color=C["bg_hover"],
                corner_radius=8, height=32,
            )
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)
            flag = "🇵🇱" if e["language"] == "pl" else "🇬🇧" if e["language"] == "en" else "🌍"
            preview = e["text"][:44] + ("…" if len(e["text"]) > 44 else "")
            ctk.CTkLabel(
                row,
                text=f"{flag} {e['time']} • {preview}",
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=C["txt2"],
                anchor="w",
            ).pack(side="left", padx=8, fill="x", expand=True)
            t = e["text"]
            ctk.CTkButton(
                row, text="📋", width=26, height=22,
                font=ctk.CTkFont(size=10),
                fg_color="transparent", hover_color=C["accent"],
                corner_radius=6,
                command=lambda txt=t: pyperclip.copy(txt),
            ).pack(side="right", padx=4)

    def _clear_history(self):
        self._history = []
        self._refresh_history()

    # ═══════════════════════════════════════════════════════════════
    # SETTINGS CALLBACKS
    # ═══════════════════════════════════════════════════════════════

    def _on_lang(self, v):
        self.config.language = v
        self.config.save()

    def _on_model(self, v):
        if v != self.config.model_size:
            self.config.model_size = v
            self.config.save()
            self.status.configure(text=f"⏳ Ładuję model '{v}'...", text_color=C["warn"])
            threading.Thread(target=self._reload_model, args=(v,), daemon=True).start()

    def _on_autotype_toggle(self):
        self.config.auto_type_enabled = self.autotype_var.get()
        self.config.save()

    def _on_typemethod(self, v):
        self.config.typing_method = v
        self.config.save()

    def _on_autocopy_toggle(self):
        self.config.auto_copy_to_clipboard = self.autocopy_var.get()
        self.config.save()

    def _on_tray_toggle(self):
        self.config.minimize_to_tray = self.tray_var.get()
        self.config.save()

    def _on_notify_toggle(self):
        self.config.show_notifications = self.notify_var.get()
        self.config.save()

    def _on_vad_toggle(self):
        self.config.vad_enabled = self.vad_var.get()
        self.config.save()

    def _on_beam_change(self, v):
        self.config.beam_size = int(v)
        self.config.save()

    def _on_autocorrect_toggle(self):
        self.config.auto_correct = self.autocorrect_var.get()
        self.config.save()

    def _on_sounds_toggle(self):
        self.config.play_sounds = self.sounds_var.get()
        self.config.save()

    def _on_autostart_toggle(self):
        enabled = self.autostart_var.get()
        set_autostart(enabled)
        self.config.start_with_windows = enabled
        self.config.save()
        msg = "🚀 Auto-start włączony" if enabled else "🔕 Auto-start wyłączony"
        self.status.configure(text=msg, text_color=C["ok"])

    def _reload_model(self, sz):
        try:
            self.transcriber.load_model(
                sz,
                on_progress=lambda m: self.after(
                    0, lambda msg=m: self.status.configure(text=msg)
                ),
            )
        except Exception as e:
            self.after(
                0,
                lambda: self.status.configure(
                    text=f"❌ Model: {str(e)[:50]}", text_color=C["rec_red"]
                ),
            )

    def _copy_text(self):
        t = self.textbox.get("1.0", "end").strip()
        placeholder = "Twój tekst pojawi się tutaj"
        if t and not t.startswith(placeholder):
            pyperclip.copy(t)
            self.status.configure(text="📋 Skopiowano!", text_color=C["ok"])

    def _clear_transcript(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", "Twój tekst pojawi się tutaj...")
        self.textbox.configure(state="disabled")

    def _on_level(self, lv):
        self._level = lv
        self.overlay.set_level(lv)

    # ═══════════════════════════════════════════════════════════════
    # SERVICES
    # ═══════════════════════════════════════════════════════════════

    def _start_services(self):
        self.status.configure(
            text="⏳ Ładowanie modelu Whisper...", text_color=C["warn"]
        )
        threading.Thread(target=self._init_model, daemon=True).start()
        try:
            self.hotkey_manager.start()
        except Exception:
            pass
        try:
            self.tray.start()
        except Exception:
            pass

    def _init_model(self):
        try:
            self.transcriber.load_model(
                on_progress=lambda m: self.after(
                    0, lambda msg=m: self.status.configure(
                        text=msg, text_color=C["txt2"]
                    )
                )
            )
            hk = self.config.hotkey.upper().replace("+", " + ")
            self.after(
                0,
                lambda: self.status.configure(
                    text=f"✨ Gotowy — Przytrzymaj {hk} i mów",
                    text_color=C["ok"],
                ),
            )
        except Exception as e:
            self.after(
                0,
                lambda: self.status.configure(
                    text=f"❌ {str(e)[:70]}", text_color=C["rec_red"]
                ),
            )

    def _show(self):
        self.after(0, lambda: (self.deiconify(), self.lift(), self.focus_force()))

    def _on_close(self):
        if self.config.minimize_to_tray:
            self.withdraw()
        else:
            self._quit()

    def _quit(self):
        self._alive = False
        if self._recording:
            self.recorder.stop()
        self.hotkey_manager.stop()
        self.tray.stop()
        self.config.save()
        self.destroy()
