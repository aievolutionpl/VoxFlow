# 📋 Changelog

Wszystkie istotne zmiany w projekcie są dokumentowane w tym pliku.

Format oparty na [Keep a Changelog](https://keepachangelog.com/pl/1.0.0/),
wersjonowanie zgodne z [Semantic Versioning](https://semver.org/lang/pl/).

---

## [1.1.0] — 2026-02-20

### ✨ Dodane
- 🎤 Wybór mikrofonu — dropdown z listą urządzeń audio
- ⌨️ Interaktywny hotkey picker — naciśnij dowolny klawisz aby ustawić
- 🔑 Wsparcie kombinacji klawiszy (Ctrl+Space, Ctrl+Shift+Space itp.)
- 🖥️ Zapamiętywanie rozmiaru okna między sesjami
- ⚠️ Automatyczny fallback mikrofonu gdy wybrany jest niedostępny

### 🐛 Naprawiono
- **[Krytyczny]** Hotkey resetował się do F2 po każdym restarcie — walidacja
  konfiguracji blokowała własne klawisze użytkownika
- **[Krytyczny]** Fallback mikrofonu nie aktualizował konfiguracji trwale —
  problem powtarzał się przy każdym uruchomieniu
- **[Krytyczny]** `keyboard.read_event()` bez timeout mogło zawiesić wątek UI
  podczas hotkey capture — naprawiono przez threading.Event z limitem czasu
- **[Ważny]** Settings panel wstawiał się w losowe miejsce — naprawiono przez
  przechowywanie referencji do `footer_frame`
- Graceful degradation gdy `pystray` lub `autostart` są niedostępne (brak crashu)

### 🔧 Poprawki jakości
- Escape anuluje teraz hotkey capture
- Debounced zapis rozmiaru okna (400ms po ostatnim zdarzeniu resize)
- Tray guard — aplikacja działa poprawnie bez system tray

---

## [1.0.0] — 2026-02-16

### ✨ Dodane
- 🎤 Lokalne rozpoznawanie mowy (speech-to-text) — 100% offline
- 🇵🇱🇬🇧 Wsparcie dla języka polskiego i angielskiego
- ⌨️ Hold-to-record — przytrzymaj F2 i mów
- ✍️ Auto-wpisywanie tekstu do aktywnego okna (clipboard/keyboard)
- 📋 Automatyczne kopiowanie transkrypcji do schowka
- 🧠 Wybór modelu Whisper: tiny / base / small / medium / large-v3
- 🎯 Voice Activity Detection (VAD) — inteligentna detekcja mowy
- ✨ Auto-korekta tekstu — poprawa polskich znaków diakrytycznych
- 🔊 Dźwięki nagrywania (generowane programistycznie)
- 🖥️ System tray — minimalizacja do zasobnika systemowego
- 🎨 Ciemny motyw UI z animacjami Canvas
- 📚 Historia transkrypcji (ostatnie 10 nagrań)
- 🚀 Autostart z Windows (opcjonalnie)
- 🔴 Overlay nagrywania — animowana nakładka na ekranie
- 📦 Wersja .exe (PyInstaller) + instalator (Inno Setup)

### 🔒 Bezpieczeństwo
- Walidacja konfiguracji ładowanej z pliku JSON
- Ograniczenie długości tekstu auto-wpisywania
- Bezpieczna obsługa kluczy rejestru Windows

### 🏗️ Technologie
- Python 3.9+
- faster-whisper (CTranslate2)
- CustomTkinter
- sounddevice + numpy
- pystray + keyboard

---

*Zbudowane przez [AI Evolution Polska](https://github.com/aievolutionpl)*
