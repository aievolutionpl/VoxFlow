"""VoxFlow Main Application - Beautiful Desktop UI with Hold-to-Record.

Built by AI Evolution Polska
https://github.com/AI-Evolution-Polska/VoxFlow
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
from voxflow.tray import TrayManager
from voxflow.auto_typer import AutoTyper
from voxflow import sounds
from voxflow.overlay import RecordingOverlay
from voxflow.autostart import set_autostart, is_autostart_enabled
from voxflow import __version__, __author__


# ─── Color Palette ────────────────────────────────────────────────────────────
C = {
    "bg":           "#0c0c18",
    "bg_card":      "#161630",
    "bg_hover":     "#1e1e42",
    "bg_input":     "#12122a",
    "accent":       "#8b5cf6",
    "accent2":      "#a78bfa",
    "accent_dim":   "#6d28d9",
    "rec_red":      "#ef4444",
    "rec_glow":     "#dc2626",
    "ok":           "#22c55e",
    "warn":         "#f59e0b",
    "txt":          "#f1f5f9",
    "txt2":         "#94a3b8",
    "txt3":         "#64748b",
    "border":       "#2a2a50",
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
        self.minsize(440, 620)
        self.configure(fg_color=C["bg"])

        # ─── State ────────────────────────────────────────────────
        self._recording = False
        self._processing = False
        self._level = 0.0
        self._phase = 0.0
        self._history: list[dict] = []
        self._alive = True
        self._settings_visible = False

        # ─── Engine ───────────────────────────────────────────────
        self.recorder = AudioRecorder(
            sample_rate=self.config.sample_rate,
            channels=self.config.channels,
            silence_threshold=self.config.silence_threshold,
            silence_duration=self.config.silence_duration,
            max_duration=self.config.max_recording_duration,
            on_level_change=self._on_level,
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

        self.tray = TrayManager(
            on_show=self._show,
            on_toggle_recording=lambda: self.after(0, self._toggle_recording),
            on_quit=self._quit,
        )

        self.auto_typer = AutoTyper()
        self.overlay = RecordingOverlay()

        # ─── Build ────────────────────────────────────────────────
        self._build_ui()
        self._start_services()

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._animate()

    # ═══════════════════════════════════════════════════════════════
    # UI
    # ═══════════════════════════════════════════════════════════════

    def _build_ui(self):
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.pack(fill="both", expand=True, padx=20, pady=10)

        self._build_header()
        self._build_record_btn()
        self._build_level_bar()
        self._build_status()
        self._build_transcript()
        self._build_quick_controls()
        self._build_history()
        self._build_settings_panel()
        self._build_footer()

    def _build_header(self):
        f = ctk.CTkFrame(self.main, fg_color="transparent")
        f.pack(fill="x", pady=(8, 2))

        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x")

        ctk.CTkLabel(row, text="🎤 VoxFlow",
                     font=ctk.CTkFont(family="Segoe UI", size=30, weight="bold"),
                     text_color=C["txt"]).pack(side="left")

        # Version badge
        ctk.CTkLabel(row, text=f"v{__version__}",
                     font=ctk.CTkFont(size=10),
                     text_color=C["accent2"],
                     fg_color=C["bg_card"],
                     corner_radius=6,
                     padx=6, pady=1).pack(side="left", padx=(8, 0))

        # Settings gear button
        self.settings_btn = ctk.CTkButton(
            row, text="⚙️", width=36, height=36,
            font=ctk.CTkFont(size=16),
            fg_color=C["bg_card"], hover_color=C["accent"],
            corner_radius=10, command=self._toggle_settings,
        )
        self.settings_btn.pack(side="right")

        ctk.CTkLabel(f, text="Przytrzymaj F2 aby dyktować • 100% offline",
                     font=ctk.CTkFont(size=12), text_color=C["txt2"]).pack(anchor="w", pady=(2, 0))

    def _build_record_btn(self):
        f = ctk.CTkFrame(self.main, fg_color="transparent")
        f.pack(fill="x", pady=12)

        sz = 150
        self.canvas = ctk.CTkCanvas(f, width=sz, height=sz, bg=C["bg"], highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<ButtonPress-1>", lambda e: self._start_rec())
        self.canvas.bind("<ButtonRelease-1>", lambda e: self._stop_rec())
        self._csz = sz
        self._draw_btn()

    def _draw_btn(self):
        self.canvas.delete("all")
        cx = cy = self._csz // 2
        r = 52

        if self._recording:
            # Glow rings
            for i in range(3):
                p = self._phase + i * 0.8
                er = r + 10 + i * 11 + ((math.sin(p) + 1) / 2) * 8
                self.canvas.create_oval(cx-er, cy-er, cx+er, cy+er,
                                        fill="", outline=C["rec_red"], width=max(1, 3-i))
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                                    fill=C["rec_red"], outline=C["rec_glow"], width=3)
            # Waveform bars
            for i in range(7):
                bx = cx - 24 + i * 8
                amp = abs(math.sin(self._phase * 2 + i * 0.7)) * 18 + 4
                self.canvas.create_rectangle(bx-2, cy-amp, bx+2, cy+amp,
                                             fill="white", outline="")
        elif self._processing:
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                                    fill=C["warn"], outline="#d97706", width=3)
            for i in range(8):
                a = self._phase * 3 + i * (math.pi / 4)
                dx, dy = cx + math.cos(a) * 25, cy + math.sin(a) * 25
                self.canvas.create_oval(dx-4, dy-4, dx+4, dy+4, fill="white", outline="")
        else:
            gf = (math.sin(self._phase * 0.4) + 1) / 2
            gr = r + 4 + gf * 5
            self.canvas.create_oval(cx-gr, cy-gr, cx+gr, cy+gr,
                                    fill="", outline=C["accent"], width=2)
            self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                                    fill=C["accent"], outline=C["accent2"], width=3)
            # Mic icon
            self.canvas.create_oval(cx-10, cy-24, cx+10, cy+0, fill="white", outline="")
            self.canvas.create_line(cx, cy, cx, cy+14, fill="white", width=3)
            self.canvas.create_line(cx-10, cy+14, cx+10, cy+14, fill="white", width=3)
            self.canvas.create_arc(cx-16, cy-12, cx+16, cy+8,
                                   start=200, extent=140, style="arc", outline="white", width=2)

    def _build_level_bar(self):
        f = ctk.CTkFrame(self.main, fg_color="transparent")
        f.pack(fill="x", pady=(0, 4))
        self.level_bar = ctk.CTkProgressBar(f, height=5, corner_radius=3,
                                             fg_color=C["bg_card"], progress_color=C["accent"], border_width=0)
        self.level_bar.pack(fill="x", padx=25)
        self.level_bar.set(0)

    def _build_status(self):
        f = ctk.CTkFrame(self.main, fg_color="transparent")
        f.pack(fill="x", pady=(0, 8))
        hk = self.config.hotkey.upper()
        self.status = ctk.CTkLabel(f, text=f"✨ Gotowy — Przytrzymaj {hk} lub kliknij przycisk",
                                   font=ctk.CTkFont(size=12), text_color=C["txt2"])
        self.status.pack()

    def _build_transcript(self):
        card = ctk.CTkFrame(self.main, fg_color=C["bg_card"], corner_radius=12,
                            border_width=1, border_color=C["border"])
        card.pack(fill="both", expand=True, pady=(0, 8))

        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=14, pady=(10, 0))

        ctk.CTkLabel(head, text="📝 Transkrypcja",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C["txt2"]).pack(side="left")

        self.copy_btn = ctk.CTkButton(head, text="📋 Kopiuj", width=75, height=26,
                                      font=ctk.CTkFont(size=11),
                                      fg_color=C["bg_hover"], hover_color=C["accent"],
                                      corner_radius=8, command=self._copy_text)
        self.copy_btn.pack(side="right")

        self.textbox = ctk.CTkTextbox(card, font=ctk.CTkFont(family="Segoe UI", size=15),
                                       fg_color="transparent", text_color=C["txt"],
                                       wrap="word", height=100, border_width=0)
        self.textbox.pack(fill="both", expand=True, padx=14, pady=(4, 10))
        self.textbox.insert("1.0", "Twój tekst pojawi się tutaj...")
        self.textbox.configure(state="disabled")

    def _build_quick_controls(self):
        card = ctk.CTkFrame(self.main, fg_color=C["bg_card"], corner_radius=12,
                            border_width=1, border_color=C["border"])
        card.pack(fill="x", pady=(0, 8))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=10)

        # Language
        lf = ctk.CTkFrame(inner, fg_color="transparent")
        lf.pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkLabel(lf, text="🌍 Język", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=C["txt2"]).pack(anchor="w")
        self.lang_var = ctk.StringVar(value=self.config.language)
        ctk.CTkOptionMenu(lf, values=["auto", "pl", "en"], variable=self.lang_var,
                          font=ctk.CTkFont(size=12), fg_color=C["bg_input"],
                          button_color=C["accent"], button_hover_color=C["accent2"],
                          dropdown_fg_color=C["bg_card"], corner_radius=8,
                          command=self._on_lang).pack(fill="x", pady=(3, 0))

        # Model
        mf = ctk.CTkFrame(inner, fg_color="transparent")
        mf.pack(side="left", expand=True, fill="x", padx=(6, 6))
        ctk.CTkLabel(mf, text="🧠 Model", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=C["txt2"]).pack(anchor="w")
        self.model_var = ctk.StringVar(value=self.config.model_size)
        ctk.CTkOptionMenu(mf, values=self.config.available_models, variable=self.model_var,
                          font=ctk.CTkFont(size=12), fg_color=C["bg_input"],
                          button_color=C["accent"], button_hover_color=C["accent2"],
                          dropdown_fg_color=C["bg_card"], corner_radius=8,
                          command=self._on_model).pack(fill="x", pady=(3, 0))

        # Hotkey
        hf = ctk.CTkFrame(inner, fg_color="transparent")
        hf.pack(side="left", expand=True, fill="x", padx=(6, 0))
        ctk.CTkLabel(hf, text="⌨️ Klawisz", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=C["txt2"]).pack(anchor="w")
        self.hotkey_var = ctk.StringVar(value=self.config.hotkey)
        ctk.CTkOptionMenu(hf, values=self.config.available_hotkeys, variable=self.hotkey_var,
                          font=ctk.CTkFont(size=12), fg_color=C["bg_input"],
                          button_color=C["accent"], button_hover_color=C["accent2"],
                          dropdown_fg_color=C["bg_card"], corner_radius=8,
                          command=self._on_hotkey_change).pack(fill="x", pady=(3, 0))

    def _build_history(self):
        card = ctk.CTkFrame(self.main, fg_color=C["bg_card"], corner_radius=12,
                            border_width=1, border_color=C["border"])
        card.pack(fill="x", pady=(0, 8))

        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkLabel(head, text="📚 Historia",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C["txt2"]).pack(side="left")

        ctk.CTkButton(head, text="🗑️", width=30, height=26,
                      font=ctk.CTkFont(size=10), fg_color=C["bg_hover"],
                      hover_color=C["rec_red"], corner_radius=6,
                      command=self._clear_history).pack(side="right")

        self.hist_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.hist_frame.pack(fill="x", padx=14, pady=(0, 10))

        self.hist_empty = ctk.CTkLabel(self.hist_frame, text="Brak nagrań",
                                        font=ctk.CTkFont(size=11), text_color=C["txt3"])
        self.hist_empty.pack(pady=4)

    def _build_settings_panel(self):
        """Build the collapsible advanced settings panel."""
        self.settings_frame = ctk.CTkFrame(self.main, fg_color=C["bg_card"], corner_radius=12,
                                            border_width=1, border_color=C["accent_dim"])
        # Hidden by default
        self._settings_visible = False

        inner = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=12)

        ctk.CTkLabel(inner, text="⚙️ Ustawienia zaawansowane",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=C["txt"]).pack(anchor="w", pady=(0, 10))

        # --- Auto-type toggle ---
        row1 = ctk.CTkFrame(inner, fg_color="transparent")
        row1.pack(fill="x", pady=3)
        ctk.CTkLabel(row1, text="✍️ Auto-wpisywanie tekstu",
                     font=ctk.CTkFont(size=12), text_color=C["txt2"]).pack(side="left")
        self.autotype_var = ctk.BooleanVar(value=self.config.auto_type_enabled)
        ctk.CTkSwitch(row1, text="", variable=self.autotype_var,
                      fg_color=C["bg_hover"], progress_color=C["accent"],
                      button_color=C["txt"], button_hover_color=C["accent2"],
                      command=self._on_autotype_toggle).pack(side="right")

        # --- Typing method ---
        row2 = ctk.CTkFrame(inner, fg_color="transparent")
        row2.pack(fill="x", pady=3)
        ctk.CTkLabel(row2, text="📋 Metoda wpisywania",
                     font=ctk.CTkFont(size=12), text_color=C["txt2"]).pack(side="left")
        self.typemethod_var = ctk.StringVar(value=self.config.typing_method)
        ctk.CTkOptionMenu(row2, values=["clipboard", "keyboard"], variable=self.typemethod_var,
                          width=130, font=ctk.CTkFont(size=11),
                          fg_color=C["bg_input"], button_color=C["accent"],
                          button_hover_color=C["accent2"], dropdown_fg_color=C["bg_card"],
                          corner_radius=8, command=self._on_typemethod).pack(side="right")

        # --- Auto-copy ---
        row3 = ctk.CTkFrame(inner, fg_color="transparent")
        row3.pack(fill="x", pady=3)
        ctk.CTkLabel(row3, text="📎 Auto-kopiowanie do schowka",
                     font=ctk.CTkFont(size=12), text_color=C["txt2"]).pack(side="left")
        self.autocopy_var = ctk.BooleanVar(value=self.config.auto_copy_to_clipboard)
        ctk.CTkSwitch(row3, text="", variable=self.autocopy_var,
                      fg_color=C["bg_hover"], progress_color=C["accent"],
                      button_color=C["txt"], button_hover_color=C["accent2"],
                      command=self._on_autocopy_toggle).pack(side="right")

        # --- Minimize to tray ---
        row4 = ctk.CTkFrame(inner, fg_color="transparent")
        row4.pack(fill="x", pady=3)
        ctk.CTkLabel(row4, text="🔲 Minimalizuj do zasobnika",
                     font=ctk.CTkFont(size=12), text_color=C["txt2"]).pack(side="left")
        self.tray_var = ctk.BooleanVar(value=self.config.minimize_to_tray)
        ctk.CTkSwitch(row4, text="", variable=self.tray_var,
                      fg_color=C["bg_hover"], progress_color=C["accent"],
                      button_color=C["txt"], button_hover_color=C["accent2"],
                      command=self._on_tray_toggle).pack(side="right")

        # --- Notifications ---
        row5 = ctk.CTkFrame(inner, fg_color="transparent")
        row5.pack(fill="x", pady=3)
        ctk.CTkLabel(row5, text="🔔 Powiadomienia",
                     font=ctk.CTkFont(size=12), text_color=C["txt2"]).pack(side="left")
        self.notify_var = ctk.BooleanVar(value=self.config.show_notifications)
        ctk.CTkSwitch(row5, text="", variable=self.notify_var,
                      fg_color=C["bg_hover"], progress_color=C["accent"],
                      button_color=C["txt"], button_hover_color=C["accent2"],
                      command=self._on_notify_toggle).pack(side="right")

        # --- VAD ---
        row6 = ctk.CTkFrame(inner, fg_color="transparent")
        row6.pack(fill="x", pady=3)
        ctk.CTkLabel(row6, text="🎯 Detekcja mowy (VAD)",
                     font=ctk.CTkFont(size=12), text_color=C["txt2"]).pack(side="left")
        self.vad_var = ctk.BooleanVar(value=self.config.vad_enabled)
        ctk.CTkSwitch(row6, text="", variable=self.vad_var,
                      fg_color=C["bg_hover"], progress_color=C["accent"],
                      button_color=C["txt"], button_hover_color=C["accent2"],
                      command=self._on_vad_toggle).pack(side="right")

        # --- Beam Size ---
        row7 = ctk.CTkFrame(inner, fg_color="transparent")
        row7.pack(fill="x", pady=3)
        ctk.CTkLabel(row7, text="🔬 Beam size (dokładność)",
                     font=ctk.CTkFont(size=12), text_color=C["txt2"]).pack(side="left")
        self.beam_var = ctk.StringVar(value=str(self.config.beam_size))
        ctk.CTkOptionMenu(row7, values=["1", "3", "5", "8", "10"], variable=self.beam_var,
                          width=80, font=ctk.CTkFont(size=11),
                          fg_color=C["bg_input"], button_color=C["accent"],
                          button_hover_color=C["accent2"], dropdown_fg_color=C["bg_card"],
                          corner_radius=8, command=self._on_beam_change).pack(side="right")

        # --- Auto-correct ---
        row8 = ctk.CTkFrame(inner, fg_color="transparent")
        row8.pack(fill="x", pady=3)
        ctk.CTkLabel(row8, text="✨ Autokorekta tekstu",
                     font=ctk.CTkFont(size=12), text_color=C["txt2"]).pack(side="left")
        self.autocorrect_var = ctk.BooleanVar(value=self.config.auto_correct)
        ctk.CTkSwitch(row8, text="", variable=self.autocorrect_var,
                      fg_color=C["bg_hover"], progress_color=C["accent"],
                      button_color=C["txt"], button_hover_color=C["accent2"],
                      command=self._on_autocorrect_toggle).pack(side="right")

        # --- Sounds toggle ---
        row9 = ctk.CTkFrame(inner, fg_color="transparent")
        row9.pack(fill="x", pady=3)
        ctk.CTkLabel(row9, text="🔊 Dźwięki nagrywania",
                     font=ctk.CTkFont(size=12), text_color=C["txt2"]).pack(side="left")
        self.sounds_var = ctk.BooleanVar(value=self.config.play_sounds)
        ctk.CTkSwitch(row9, text="", variable=self.sounds_var,
                      fg_color=C["bg_hover"], progress_color=C["accent"],
                      button_color=C["txt"], button_hover_color=C["accent2"],
                      command=self._on_sounds_toggle).pack(side="right")

        # --- Auto-start with Windows ---
        row10 = ctk.CTkFrame(inner, fg_color="transparent")
        row10.pack(fill="x", pady=3)
        ctk.CTkLabel(row10, text="🚀 Uruchamiaj z Windows",
                     font=ctk.CTkFont(size=12), text_color=C["txt2"]).pack(side="left")
        self.autostart_var = ctk.BooleanVar(value=is_autostart_enabled())
        ctk.CTkSwitch(row10, text="", variable=self.autostart_var,
                      fg_color=C["bg_hover"], progress_color=C["accent"],
                      button_color=C["txt"], button_hover_color=C["accent2"],
                      command=self._on_autostart_toggle).pack(side="right")

        # --- Separator ---
        ctk.CTkFrame(inner, fg_color=C["border"], height=1).pack(fill="x", pady=8)

        # Info label
        ctk.CTkLabel(inner,
                     text="💡 Dźwięki informują o starcie/stopie nagrywania.\n"
                          "     Animacja REC pojawia się w prawym górnym rogu ekranu.",
                     font=ctk.CTkFont(size=11), text_color=C["txt3"],
                     justify="left").pack(anchor="w")

    def _build_footer(self):
        f = ctk.CTkFrame(self.main, fg_color="transparent")
        f.pack(fill="x", pady=(0, 6))

        # Main footer with branding
        ctk.CTkLabel(f, text=f"VoxFlow v{__version__} • faster-whisper • 100% Lokalne",
                     font=ctk.CTkFont(size=10), text_color=C["txt3"]).pack()

        # AI Evolution Polska credit
        ctk.CTkLabel(f, text=f"Built by {__author__}",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=C["accent_dim"]).pack(pady=(1, 0))

    # ═══════════════════════════════════════════════════════════════
    # SETTINGS TOGGLE
    # ═══════════════════════════════════════════════════════════════

    def _toggle_settings(self):
        if self._settings_visible:
            self.settings_frame.pack_forget()
            self._settings_visible = False
            self.settings_btn.configure(fg_color=C["bg_card"])
        else:
            # Pack before footer
            self.settings_frame.pack(fill="x", pady=(0, 8), before=self.main.winfo_children()[-1])
            self._settings_visible = True
            self.settings_btn.configure(fg_color=C["accent_dim"])

    # ═══════════════════════════════════════════════════════════════
    # ANIMATION
    # ═══════════════════════════════════════════════════════════════

    def _animate(self):
        if not self._alive:
            return
        self._phase += 0.12
        self._draw_btn()

        target = self._level if self._recording else 0
        cur = self.level_bar.get()
        self.level_bar.set(min(1.0, cur + (target - cur) * 0.3) * 5 if self._recording else max(0, cur * 0.85))
        self.level_bar.configure(progress_color=C["rec_red"] if self._recording else C["accent"])

        self.after(50, self._animate)

    # ═══════════════════════════════════════════════════════════════
    # RECORDING (Hold-to-Record)
    # ═══════════════════════════════════════════════════════════════

    def _on_hotkey_press(self):
        """Called when hotkey is pressed down — start recording."""
        self.after(0, self._start_rec)

    def _on_hotkey_release(self):
        """Called when hotkey is released — stop recording + transcribe."""
        self.after(0, self._stop_rec)

    def _toggle_recording(self):
        if self._processing:
            return
        if self._recording:
            self._stop_rec()
        else:
            self._start_rec()

    def _start_rec(self):
        if self._recording or self._processing:
            return
        self._recording = True
        self.status.configure(text="🔴 Nagrywam... Mów teraz!", text_color=C["rec_red"])
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
                on_progress=lambda m: self.after(0, lambda msg=m: self.status.configure(text=msg)),
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

        # Update transcript box
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", text)
        self.textbox.configure(state="disabled")

        # Auto-copy
        if self.config.auto_copy_to_clipboard:
            try:
                pyperclip.copy(text)
            except Exception:
                pass

        # Auto-type into active window
        if self.config.auto_type_enabled:
            # Small delay to let the user's target window regain focus
            threading.Thread(
                target=self._delayed_auto_type,
                args=(text,),
                daemon=True,
            ).start()

        lang = result.get("language", "?")
        flag = "🇵🇱" if lang == "pl" else "🇬🇧" if lang == "en" else "🌍"
        dur = result.get("duration", 0)
        extra = " • ✍️ Wpisano!" if self.config.auto_type_enabled else ""
        extra += " • 📋" if self.config.auto_copy_to_clipboard else ""
        self.status.configure(text=f"✅ {flag} {lang.upper()} • {dur:.1f}s{extra}", text_color=C["ok"])
        if self.config.play_sounds:
            sounds.play("done")

        self._add_history(text, lang, dur)

    def _delayed_auto_type(self, text: str):
        """Wait briefly for target window to get focus, then type."""
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
        self._history.insert(0, {"text": text, "language": lang, "duration": dur,
                                  "time": datetime.now().strftime("%H:%M:%S")})
        if len(self._history) > 10:
            self._history = self._history[:10]
        self._refresh_history()

    def _refresh_history(self):
        for w in self.hist_frame.winfo_children():
            w.destroy()
        if not self._history:
            ctk.CTkLabel(self.hist_frame, text="Brak nagrań",
                         font=ctk.CTkFont(size=11), text_color=C["txt3"]).pack(pady=4)
            return
        for e in self._history[:5]:
            row = ctk.CTkFrame(self.hist_frame, fg_color=C["bg_hover"], corner_radius=8, height=34)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)
            flag = "🇵🇱" if e["language"] == "pl" else "🇬🇧" if e["language"] == "en" else "🌍"
            preview = e["text"][:45] + ("..." if len(e["text"]) > 45 else "")
            ctk.CTkLabel(row, text=f"{flag} {e['time']} • {preview}",
                         font=ctk.CTkFont(size=11), text_color=C["txt2"],
                         anchor="w").pack(side="left", padx=8, fill="x", expand=True)
            t = e["text"]
            ctk.CTkButton(row, text="📋", width=28, height=22, font=ctk.CTkFont(size=10),
                          fg_color="transparent", hover_color=C["accent"], corner_radius=6,
                          command=lambda txt=t: pyperclip.copy(txt)).pack(side="right", padx=4)

    def _clear_history(self):
        self._history = []
        self._refresh_history()

    # ═══════════════════════════════════════════════════════════════
    # SETTINGS CALLBACKS
    # ═══════════════════════════════════════════════════════════════

    def _on_lang(self, v):
        self.config.language = v; self.config.save()

    def _on_model(self, v):
        if v != self.config.model_size:
            self.config.model_size = v; self.config.save()
            self.status.configure(text=f"⏳ Ładuję model '{v}'...", text_color=C["warn"])
            threading.Thread(target=self._reload_model, args=(v,), daemon=True).start()

    def _on_hotkey_change(self, v):
        self.config.hotkey = v; self.config.save()
        self.hotkey_manager.update_hotkey(v)
        self.status.configure(text=f"⌨️ Hotkey: {v.upper()}", text_color=C["ok"])

    def _on_autotype_toggle(self):
        self.config.auto_type_enabled = self.autotype_var.get(); self.config.save()

    def _on_typemethod(self, v):
        self.config.typing_method = v; self.config.save()

    def _on_autocopy_toggle(self):
        self.config.auto_copy_to_clipboard = self.autocopy_var.get(); self.config.save()

    def _on_tray_toggle(self):
        self.config.minimize_to_tray = self.tray_var.get(); self.config.save()

    def _on_notify_toggle(self):
        self.config.show_notifications = self.notify_var.get(); self.config.save()

    def _on_vad_toggle(self):
        self.config.vad_enabled = self.vad_var.get(); self.config.save()

    def _on_beam_change(self, v):
        self.config.beam_size = int(v); self.config.save()

    def _on_autocorrect_toggle(self):
        self.config.auto_correct = self.autocorrect_var.get(); self.config.save()

    def _on_sounds_toggle(self):
        self.config.play_sounds = self.sounds_var.get(); self.config.save()

    def _on_autostart_toggle(self):
        enabled = self.autostart_var.get()
        set_autostart(enabled)
        self.config.start_with_windows = enabled
        self.config.save()
        msg = "🚀 Auto-start włączony" if enabled else "🚀 Auto-start wyłączony"
        self.status.configure(text=msg, text_color=C["ok"])

    def _reload_model(self, sz):
        try:
            self.transcriber.load_model(sz, on_progress=lambda m: self.after(
                0, lambda msg=m: self.status.configure(text=msg)))
        except Exception as e:
            self.after(0, lambda: self.status.configure(
                text=f"❌ Model: {str(e)[:50]}", text_color=C["rec_red"]))

    def _copy_text(self):
        self.textbox.configure(state="normal")
        t = self.textbox.get("1.0", "end").strip()
        self.textbox.configure(state="disabled")
        if t and t != "Twój tekst pojawi się tutaj...":
            pyperclip.copy(t)
            self.status.configure(text="📋 Skopiowano!", text_color=C["ok"])

    def _on_level(self, lv):
        self._level = lv
        self.overlay.set_level(lv)

    # ═══════════════════════════════════════════════════════════════
    # SERVICES
    # ═══════════════════════════════════════════════════════════════

    def _start_services(self):
        self.status.configure(text="⏳ Ładowanie modelu Whisper...", text_color=C["warn"])
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
            self.transcriber.load_model(on_progress=lambda m: self.after(
                0, lambda msg=m: self.status.configure(text=msg, text_color=C["txt2"])))
            hk = self.config.hotkey.upper()
            self.after(0, lambda: self.status.configure(
                text=f"✨ Gotowy — Przytrzymaj {hk} i mów", text_color=C["ok"]))
        except Exception as e:
            self.after(0, lambda: self.status.configure(
                text=f"❌ {str(e)[:70]}", text_color=C["rec_red"]))

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
