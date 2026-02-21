<div align="center">

# 🎤 VoxFlow

### Dyktowanie głosem • 100% Offline • Open Source

[![License: MIT](https://img.shields.io/badge/License-MIT-7c3aed.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-lightgrey)](https://github.com/aievolutionpl/VoxFlow)
[![by AI Evolution Polska](https://img.shields.io/badge/by-AI_Evolution_Polska-7c3aed)](https://github.com/aievolutionpl)

**VoxFlow** to bezpłatne narzędzie do dyktowania głosem.  
Przytrzymaj klawisz → mów → tekst pojawia się w aktywnym oknie. Zero chmury, zero subskrypcji.

</div>

---

## ⚡ Szybki start (Windows) — 3 kroki

> **Wymagania:** Windows 10/11 (64-bit), mikrofon, połączenie z internetem (tylko przy pierwszym uruchomieniu do pobrania modelu AI ~500 MB)

### Krok 1 — Zainstaluj Python

Pobierz Python 3.10+ ze strony **[python.org/downloads](https://www.python.org/downloads/)**.

> ⚠️ **Ważne:** podczas instalacji zaznacz opcję **"Add Python to PATH"**!

### Krok 2 — Zainstaluj VoxFlow

Kliknij dwukrotnie plik **`install.bat`** i poczekaj aż zakończy instalację (~2–5 minut).

### Krok 3 — Uruchom

Kliknij dwukrotnie **`START_VOXFLOW.bat`** (tworzony automatycznie przez install.bat).

---

## 🖥️ Jak działa VoxFlow?

| Akcja | Efekt |
|-------|-------|
| Przytrzymaj `F2` i mów | 🔴 Nagrywa — animacja fal pojawia się na dole ekranu |
| Zwolnij `F2` | ⏳ AI przetwarza mowę → tekst wklejony w aktywnym oknie |
| Kliknij przycisk klawisza w UI | Ustaw własny klawisz dyktowania |
| Kliknij dropdown mikrofonu | Wybierz urządzenie audio |
| Kliknij `⚙` | Otwórz zaawansowane ustawienia |

Po uruchomieniu VoxFlow minimalizuje się do **ikony w zasobniku systemowym** (prawy dolny róg).  
Podwójne kliknięcie na ikonę → przywraca okno.

---

## 📦 Wersja EXE (bez Pythona)

Jeśli chcesz wersję gotową `.exe` — **nie wymaga Pythona**:

**Opcja A — Instalator (zalecana):**

```
BUILD_EXE.bat → tworzy VoxFlow_Setup.exe
```

Wymaga [Inno Setup 6](https://jrsoftware.org/isinfo.php).

**Opcja B — Portable:**

```
CREATE_PORTABLE.bat → tworzy folder dist\VoxFlow_Portable_v1.1.0\
```

Uruchom `START_VOXFLOW.bat` z folderu portable — gotowe, bez instalacji.

---

## ✨ Funkcje

| 🇵🇱 | 🇬🇧 |
|-----|-----|
| 🎤 Dyktowanie przytrzymując klawisz | Hold-to-record hotkey |
| 🌍 Polski + Angielski (auto-detekcja) | Polish + English (auto-detect) |
| ⚡ 100% lokalne — zero chmury | 100% local — no cloud |
| 🧠 OpenAI Whisper (faster-whisper) | OpenAI Whisper (faster-whisper) |
| ✍️ Auto-wpisywanie w aktywne okno | Auto-type into active window |
| 🎙 Wybór mikrofonu | Microphone device selection |
| ⌨️ Dowolny klawisz dyktowania | Configurable hotkey |
| 📋 Auto-kopiowanie do schowka | Auto-copy to clipboard |
| 🌊 Animacja fal audio podczas nagrywania | Audio waveform animation |
| 🔲 Ikona w zasobniku | System tray icon |
| 📚 Historia nagrań | Recording history |

---

## 🧠 Modele Whisper

| Model | Rozmiar | Szybkość | Jakość | Dla kogo |
|-------|---------|----------|--------|----------|
| `tiny` | ~75 MB | ⚡⚡⚡⚡ | ⭐⭐ | Testy |
| `base` | ~150 MB | ⚡⚡⚡ | ⭐⭐⭐ | Słaby PC |
| `small` | ~500 MB | ⚡⚡ | ⭐⭐⭐⭐ | **Zalecany** |
| `medium` | ~1.5 GB | ⚡ | ⭐⭐⭐⭐⭐ | Dobry PC |
| `large-v3` | ~3 GB | 🐢 | ⭐⭐⭐⭐⭐ | GPU |

> Model pobiera się automatycznie przy pierwszej zmianie (jednorazowo).

---

## 🍎 Instalacja macOS

```bash
chmod +x install_mac.sh
./install_mac.sh
```

> ⚠️ Globalny hotkey wymaga uprawnień **Accessibility** w System Settings.  
> Szczegóły: [INSTALL_MAC.md](INSTALL_MAC.md)

---

## 📜 Licencja

MIT License — bezpłatny, open source. Użyj, modyfikuj, dystrybuuj bez ograniczeń.

---

<div align="center">

**AI Evolution Polska** — Bezpłatne narzędzia AI dla polskich użytkowników

[![GitHub](https://img.shields.io/badge/GitHub-aievolutionpl-181717?logo=github)](https://github.com/aievolutionpl)

</div>
