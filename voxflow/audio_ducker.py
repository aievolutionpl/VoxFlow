"""VoxFlow Audio Ducker — ścisza inne aplikacje podczas nagrywania.

Gdy zaczynasz dyktować, grająca w tle muzyka (Spotify, YouTube itp.)
jest automatycznie przyciszana, a po zakończeniu nagrania głośność
wraca do poprzedniego poziomu. Mniej echa w mikrofonie = lepsza
jakość transkrypcji.

Implementacje per system:
- Windows: per-aplikacja przez pycaw (Core Audio) — ścisza tylko inne
  procesy, dźwięki VoxFlow (beep start/stop) pozostają słyszalne.
- macOS: głośność systemowa przez osascript.
- Linux: głośność domyślnego sinka przez pactl (PulseAudio/PipeWire).
"""
import os
import re
import subprocess
import sys
import threading
from typing import Optional


class AudioDucker:
    """Przycisza inne źródła dźwięku na czas nagrywania i je przywraca."""

    def __init__(self, duck_level: float = 0.2):
        # Docelowy ułamek oryginalnej głośności (0.0 = wycisz, 1.0 = bez zmian)
        self.duck_level = max(0.0, min(1.0, duck_level))
        self._lock = threading.Lock()
        self._ducked = False
        # Windows: pid -> oryginalna głośność sesji
        self._saved_sessions: dict[int, float] = {}
        # macOS/Linux: zapamiętana głośność systemowa (0–100)
        self._saved_master: Optional[int] = None

    # ── Public API (nieblokujące — wołane z wątku UI) ────────────────

    def duck(self):
        """Przycisz inne aplikacje. Bezpieczne przy wielokrotnym wywołaniu."""
        threading.Thread(target=self._duck_impl, daemon=True).start()

    def restore(self):
        """Przywróć zapamiętane głośności. No-op jeśli nic nie ściszono."""
        threading.Thread(target=self._restore_impl, daemon=True).start()

    # ── Dispatch ─────────────────────────────────────────────────────

    def _duck_impl(self):
        with self._lock:
            if self._ducked:
                return
            try:
                if sys.platform == "win32":
                    self._duck_windows()
                elif sys.platform == "darwin":
                    self._duck_macos()
                else:
                    self._duck_linux()
                self._ducked = True
            except Exception as e:
                print(f"[AudioDucker] duck failed: {e}")

    def _restore_impl(self):
        with self._lock:
            if not self._ducked:
                return
            try:
                if sys.platform == "win32":
                    self._restore_windows()
                elif sys.platform == "darwin":
                    self._restore_macos()
                else:
                    self._restore_linux()
            except Exception as e:
                print(f"[AudioDucker] restore failed: {e}")
            finally:
                # Nie próbuj przywracać drugi raz nawet po błędzie —
                # stan i tak jest już nieznany.
                self._ducked = False
                self._saved_sessions = {}
                self._saved_master = None

    # ── Windows (pycaw — per aplikacja) ──────────────────────────────

    def _duck_windows(self):
        import comtypes
        comtypes.CoInitialize()
        try:
            from pycaw.pycaw import AudioUtilities
            my_pid = os.getpid()
            for session in AudioUtilities.GetAllSessions():
                proc = session.Process
                # Pomiń sesje systemowe i własny proces (beepy VoxFlow)
                if proc is None or proc.pid == my_pid:
                    continue
                try:
                    volume = session.SimpleAudioVolume
                    current = volume.GetMasterVolume()
                    if current > 0.01:
                        self._saved_sessions[proc.pid] = current
                        volume.SetMasterVolume(current * self.duck_level, None)
                except Exception:
                    continue
        finally:
            try:
                comtypes.CoUninitialize()
            except Exception:
                pass

    def _restore_windows(self):
        if not self._saved_sessions:
            return
        import comtypes
        comtypes.CoInitialize()
        try:
            from pycaw.pycaw import AudioUtilities
            # Sesje enumerujemy na nowo — wskaźników COM nie wolno
            # przenosić między wątkami, więc dopasowujemy po PID.
            for session in AudioUtilities.GetAllSessions():
                proc = session.Process
                if proc is None or proc.pid not in self._saved_sessions:
                    continue
                try:
                    session.SimpleAudioVolume.SetMasterVolume(
                        self._saved_sessions[proc.pid], None
                    )
                except Exception:
                    continue
        finally:
            try:
                comtypes.CoUninitialize()
            except Exception:
                pass

    # ── macOS (osascript — głośność systemowa) ───────────────────────

    def _duck_macos(self):
        out = subprocess.run(
            ["osascript", "-e", "output volume of (get volume settings)"],
            capture_output=True, text=True, timeout=3,
        )
        current = int(out.stdout.strip())
        if current > 0:
            self._saved_master = current
            subprocess.run(
                ["osascript", "-e",
                 f"set volume output volume {int(current * self.duck_level)}"],
                capture_output=True, timeout=3,
            )

    def _restore_macos(self):
        if self._saved_master is None:
            return
        subprocess.run(
            ["osascript", "-e",
             f"set volume output volume {self._saved_master}"],
            capture_output=True, timeout=3,
        )

    # ── Linux (pactl — domyślny sink) ────────────────────────────────

    def _duck_linux(self):
        out = subprocess.run(
            ["pactl", "get-sink-volume", "@DEFAULT_SINK@"],
            capture_output=True, text=True, timeout=3,
        )
        match = re.search(r"(\d+)%", out.stdout)
        if not match:
            return
        current = int(match.group(1))
        if current > 0:
            self._saved_master = current
            subprocess.run(
                ["pactl", "set-sink-volume", "@DEFAULT_SINK@",
                 f"{int(current * self.duck_level)}%"],
                capture_output=True, timeout=3,
            )

    def _restore_linux(self):
        if self._saved_master is None:
            return
        subprocess.run(
            ["pactl", "set-sink-volume", "@DEFAULT_SINK@",
             f"{self._saved_master}%"],
            capture_output=True, timeout=3,
        )
