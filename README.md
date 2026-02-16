<p align="center">
  <img src="assets/voxflow_256.png" alt="VoxFlow Logo" width="128" height="128">
</p>

<h1 align="center">🎤 VoxFlow</h1>

<p align="center">
  <strong>Lokalne rozpoznawanie mowy — 100% offline, 100% prywatne</strong><br>
  <em>Local Speech-to-Text for Windows • Polish & English</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/VoxFlow-v1.0.0-8b5cf6?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.9+-3776ab?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/AI_Evolution-Polska-ef4444?style=for-the-badge" alt="AI Evolution Polska">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/100%25-Offline-success?style=flat-square" alt="Offline">
  <img src="https://img.shields.io/badge/🇵🇱_Polski-Wspierany-blue?style=flat-square" alt="Polish">
  <img src="https://img.shields.io/badge/🇬🇧_English-Supported-blue?style=flat-square" alt="English">
  <img src="https://img.shields.io/badge/Built_by-AI_Evolution_Polska-red?style=flat-square" alt="Built by">
</p>

---

## ✨ Co to jest VoxFlow?

**VoxFlow** to darmowa, w pełni lokalna aplikacja do zamiany mowy na tekst dla systemu Windows. Przytrzymaj klawisz **F2**, mów — a VoxFlow automatycznie wpisze tekst w aktywne okno. Żadne dane nie opuszczają Twojego komputera.

### 🎯 Kluczowe funkcje

| Funkcja | Opis |
|---------|------|
| 🎤 **Hold-to-Record** | Przytrzymaj F2 (lub inny klawisz) i mów |
| 🇵🇱🇬🇧 **Polski i Angielski** | Automatyczne wykrywanie języka |
| 🔒 **100% Lokalne** | Zero internetu, zero chmury, zero śledzenia |
| ✍️ **Auto-wpisywanie** | Tekst trafia od razu do aktywnego okna |
| 📋 **Auto-kopiowanie** | Transkrypcja ląduje w schowku |
| 🧠 **5 modeli AI** | Od tiny (75 MB) po large-v3 (3 GB) |
| ✨ **Autokorekta** | Poprawia polskie znaki diakrytyczne |
| 🎯 **VAD** | Inteligentna detekcja mowy — ignoruje ciszę |
| 🔊 **Dźwięki** | Sygnał start/stop nagrywania |
| 🖥️ **System Tray** | Minimalizuj do zasobnika systemowego |
| 🔴 **Overlay REC** | Animowana nakładka "nagrywam" na ekranie |
| 📚 **Historia** | Ostatnie 10 transkrypcji z kopiowaniem |
| 🎨 **Ciemny motyw** | Piękny UI z animacjami |

---

## 🚀 Instalacja

### Sposób 1: Pobierz gotowy .exe (zalecane)

1. Przejdź do [Releases](../../releases)
2. Pobierz `VoxFlow_Setup_v1.0.0.exe` (instalator) lub `VoxFlow-Portable.zip` (wersja portable)
3. Uruchom i gotowe!

### Sposób 2: Uruchomienie jednym kliknięciem (ze źródeł)

```
Kliknij dwukrotnie: START_VOXFLOW.bat
```

Skrypt automatycznie:
- ✅ Sprawdzi Python
- ✅ Stworzy środowisko wirtualne
- ✅ Zainstaluje pakiety
- ✅ Uruchomi VoxFlow

### Sposób 3: Ręczne uruchomienie

```bash
# Sklonuj repozytorium
git clone https://github.com/aievolutionpl/VoxFlow.git
cd VoxFlow

# Stwórz środowisko wirtualne
python -m venv venv
venv\Scripts\activate

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom
python -m voxflow.main
```

### Sposób 4: pip install

```bash
pip install .
voxflow
```

---

## ⌨️ Jak używać

1. **Uruchom VoxFlow** — okno aplikacji pojawi się na ekranie
2. **Przytrzymaj F2** (lub kliknij przycisk mikrofonu)
3. **Mów** — zobaczysz animację nagrywania
4. **Puść F2** — tekst zostanie automatycznie:
   - 📝 Wyświetlony w oknie VoxFlow
   - ✍️ Wpisany do aktywnego okna (jeśli włączone)
   - 📋 Skopiowany do schowka (jeśli włączone)

> 💡 **Tip**: VoxFlow działa w tle — możesz go zminimalizować do zasobnika systemowego.

---

## 🧠 Modele Whisper

Przy pierwszym użyciu VoxFlow automatycznie pobierze wybrany model (~1 min dla `small`).

| Model | Rozmiar | Jakość 🇵🇱 | Szybkość | Rekomendacja |
|-------|---------|-----------|----------|--------------|
| `tiny` | ~75 MB | ⭐⭐ | ⚡⚡⚡⚡⚡ | Szybkie testy |
| `base` | ~150 MB | ⭐⭐⭐ | ⚡⚡⚡⚡ | Podstawowe użycie |
| `small` | ~500 MB | ⭐⭐⭐⭐ | ⚡⚡⚡ | **Zalecany** ⬅️ |
| `medium` | ~1.5 GB | ⭐⭐⭐⭐⭐ | ⚡⚡ | Wysoka jakość |
| `large-v3` | ~3 GB | ⭐⭐⭐⭐⭐ | ⚡ | Maksymalna dokładność |

> 🎯 **Domyślnie**: `small` — najlepszy balans jakości i szybkości dla polskiego.

---

## ⚙️ Ustawienia

Kliknij ⚙️ w oknie VoxFlow, aby otworzyć zaawansowane ustawienia:

| Ustawienie | Opis | Domyślnie |
|------------|------|-----------|
| **Model** | Rozmiar modelu Whisper | `small` |
| **Język** | Auto / PL / EN | `auto` |
| **Hotkey** | Klawisz hold-to-record | `F2` |
| **Auto-wpisywanie** | Wpisuj tekst do aktywnego okna | ✅ Włączone |
| **Auto-kopiowanie** | Kopiuj do schowka | ✅ Włączone |
| **Metoda wpisywania** | Clipboard (Ctrl+V) / Klawiatura | `clipboard` |
| **VAD** | Detekcja mowy | ✅ Włączona |
| **Autokorekta** | Poprawa tekstu | ✅ Włączona |
| **Dźwięki** | Sygnały start/stop | ✅ Włączone |
| **Beam size** | Dokładność transkrypcji (1-10) | `5` |
| **Autostart** | Uruchamiaj z Windows | ❌ Wyłączone |

---

## 📁 Struktura projektu

```
VoxFlow/
├── voxflow/
│   ├── __init__.py          # Metadata pakietu
│   ├── __main__.py          # python -m voxflow
│   ├── main.py              # Entry point + test mode
│   ├── app.py               # Główne okno UI (CustomTkinter)
│   ├── config.py            # Zarządzanie konfiguracją
│   ├── recorder.py          # Nagrywanie audio (sounddevice)
│   ├── transcriber.py       # Silnik Whisper (faster-whisper)
│   ├── post_processor.py    # Autokorekta tekstu
│   ├── hotkey_manager.py    # Global hotkey (hold-to-record)
│   ├── auto_typer.py        # Auto-wpisywanie tekstu
│   ├── overlay.py           # Overlay REC na ekranie
│   ├── tray.py              # System tray
│   ├── sounds.py            # Generowanie dźwięków
│   ├── autostart.py         # Autostart Windows (rejestr)
│   ├── create_shortcut.py   # Tworzenie skrótu na pulpicie
│   └── icon_gen.py          # Generowanie ikony .ico
├── assets/
│   ├── voxflow.ico          # Ikona aplikacji
│   └── voxflow_256.png      # Logo PNG
├── .github/workflows/
│   └── ci.yml               # GitHub Actions CI
├── requirements.txt         # Zależności Python
├── pyproject.toml           # Konfiguracja pakietu (PEP 621)
├── START_VOXFLOW.bat        # Uruchom jednym kliknięciem
├── BUILD_EXE.bat            # Zbuduj .exe
├── installer.iss            # Instalator Inno Setup
├── LICENSE                  # Licencja MIT
├── CONTRIBUTING.md          # Jak kontrybuować
├── CHANGELOG.md             # Historia zmian
├── SECURITY.md              # Polityka bezpieczeństwa
├── CODE_OF_CONDUCT.md       # Kodeks postępowania
└── README.md                # Ten plik
```

---

## 🔧 Wymagania systemowe

- **System**: Windows 10/11 (x64)
- **Python**: 3.9 lub nowszy
- **RAM**: 2 GB+ (zależy od modelu)
- **Dysk**: ~500 MB (model `small`) — ~3 GB (model `large-v3`)
- **Mikrofon**: dowolny mikrofon USB/wbudowany
- **Internet**: tylko do pierwszego pobrania modelu; potem **100% offline**

---

## 🏗️ Budowanie .exe

```bash
# Zbuduj standalone .exe za pomocą PyInstaller
BUILD_EXE.bat

# Gotowy plik: dist/VoxFlow/VoxFlow.exe
```

Opcjonalnie, jeśli masz zainstalowane [Inno Setup 6](https://jrsoftware.org/isinfo.php), skrypt automatycznie zbuduje też instalator `.exe`.

---

## 🔒 Prywatność i bezpieczeństwo

VoxFlow jest **w 100% lokalne**:

- ❌ Żadne dane audio nie są wysyłane do internetu
- ❌ Żadna telemetria nie jest zbierana
- ❌ Żadne dane użytkownika nie opuszczają komputera
- ✅ Model AI działa w pełni lokalnie na Twoim CPU
- ✅ Konfiguracja przechowywana bezpiecznie w `%APPDATA%/VoxFlow/`

Więcej informacji: [SECURITY.md](SECURITY.md)

---

## 🤝 Współpraca

Chcesz pomóc? Świetnie! Przeczytaj [CONTRIBUTING.md](CONTRIBUTING.md) i otwórz Pull Request.

---

## 📄 Licencja

Ten projekt jest udostępniony na licencji [MIT](LICENSE).

---

<p align="center">
  <strong>Zbudowane z ❤️ przez <a href="https://github.com/aievolutionpl">AI Evolution Polska</a></strong><br>
  <em>Open-source tools for the Polish AI community</em>
</p>
