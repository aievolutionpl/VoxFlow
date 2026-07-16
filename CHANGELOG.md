# 📋 Changelog

Wszystkie istotne zmiany w projekcie są dokumentowane w tym pliku.

Format oparty na [Keep a Changelog](https://keepachangelog.com/pl/1.0.0/),
wersjonowanie zgodne z [Semantic Versioning](https://semver.org/lang/pl/).

---

## [1.3.0] — 2026-07-16

### ✨ Dodane
- 🎵 **Auto-ściszanie muzyki podczas nagrywania** — gdy przytrzymasz klawisz
  dyktowania, grająca w tle muzyka (Spotify, YouTube itp.) jest automatycznie
  przyciszana, a po zakończeniu wraca do poprzedniego poziomu. Na Windows
  ściszane są tylko inne aplikacje (per-aplikacja przez pycaw), na macOS/Linux
  głośność systemowa. Konfigurowalny poziom (0/20/40/60%) w ustawieniach
- 💾 **Trwała historia nagrań** — historia jest zapisywana na dysku
  (do 50 wpisów) i przywracana po ponownym uruchomieniu; starsze wpisy
  pokazują datę obok godziny
- ⏱️ **Licznik czasu nagrywania** — status pokazuje upływający czas (M:SS),
  a w ostatnich 30 sekundach ostrzega przed limitem
- 💾 Przycisk zapisu transkrypcji do pliku (.txt / .md)
- 🎨 Trzy nowe motywy kolorów: Różowy, Bursztyn, Grafitowy

### 🔧 Poprawki jakości
- ⚙️ Panel ustawień jest teraz **przewijalny** i otwiera się w miejscu karty
  historii — wcześniej dolne opcje wystawały poza okno i były nieosiągalne
- 🎨 Motyw kolorów stosowany jest teraz **natychmiast** w całym interfejsie —
  bez ponownego uruchamiania aplikacji (tekst i historia są zachowywane)
- Kliknięcie w pole transkrypcji usuwa tekst zastępczy, żeby można było
  od razu pisać
- Ujednolicono tekst zastępczy pola transkrypcji (jedna stała w kodzie)

---

## [1.2.0] — 2026-07-01

### ✨ Dodane
- 🎨 Trwały motyw kolorów — wybór (Fioletowy/Niebieski/Zielony) jest zapisywany
  i przywracany przy starcie, cały interfejs używa spójnej palety
- 🔄 Przycisk odświeżania listy mikrofonów — wykrywa urządzenia podłączone
  po uruchomieniu aplikacji (restart PortAudio)
- 🔢 Licznik słów i znaków nad polem transkrypcji (aktualizowany też
  podczas ręcznej edycji)
- 🌍 Flagi języków w szybkim wyborze języka (🇵🇱 pl, 🇬🇧 en, ...)
- ⏱️ Automatyczne zakończenie nagrania po osiągnięciu limitu czasu —
  wcześniej UI wisiał w stanie „Nagrywam" do zwolnienia klawisza

### 🐛 Naprawiono
- **[Krytyczny]** `install.bat` / `CREATE_PORTABLE.bat`: tworzenie skrótu na
  pulpicie zawsze kończyło się błędem składni Pythona — backslashe w ścieżce
  (np. `C:\Users\...`) psuły literal (`'\U'`); ścieżka przekazywana jest teraz
  przez zmienną środowiskową
- **[Ważny]** Wersja portable: launcher używał `activate.bat` z zapisaną na
  sztywno starą ścieżką venv — po przeniesieniu folderu uruchamiał złe
  środowisko; teraz woła bezpośrednio `venv\Scripts\pythonw.exe`
- **[Ważny]** macOS: auto-wklejanie używało Ctrl+V zamiast Cmd+V
- Transkrypcja czytała zmienną Tk z wątku roboczego (niebezpieczne wątkowo) —
  język jest teraz brany z konfiguracji
- Nagrywanie przy niezaładowanym modelu kończyło się błędem — teraz czytelny
  komunikat „Model AI jeszcze się ładuje"
- Ujednolicono wersję projektu (pyproject 1.0.0 / installer 1.1.0 /
  portable 1.2.0 → wszędzie 1.2.0)
- Polskie znaki w nakładce nagrywania („zakończyć")
- Uszkodzony znak w tabeli funkcji w README

### 🔧 Poprawki jakości
- `install.bat`: weryfikacja instalacji jawnie przez `venv\Scripts\python.exe`
- `START_VOXFLOW.bat` odporny na brak Pythona w PATH (używa venv bezpośrednio)
- Usunięto zduplikowane słowniki flag językowych w kodzie

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
