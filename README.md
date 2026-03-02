<div align="center">

# 🎤 VoxFlow

### Dyktowanie głosem • 100% Offline • Open Source

[![License: MIT](https://img.shields.io/badge/License-MIT-7c3aed.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-lightgrey)](https://github.com/aievolutionpl/VoxFlow)
[![by AI Evolution Polska](https://img.shields.io/badge/by-AI_Evolution_Polska-7c3aed)](https://github.com/aievolutionpl)

VoxFlow to bezpłatne narzędzie do dyktowania głosem.  
Przytrzymaj klawisz → mów → tekst pojawia się w aktywnym oknie. Zero chmury, zero subskrypcji.

</div>

---

## ⚡ Instalacja Windows — krok po kroku

> Wymagania: Windows 10/11 (64-bit), mikrofon, internet (tylko przy pierwszym uruchomieniu — pobranie modelu AI ~500 MB)

### Krok 1 — Zainstaluj Python

1. Wejdź na stronę [python.org/downloads](https://www.python.org/downloads/)
2. Pobierz Python 3.10 lub nowszy
3. Uruchom instalator
4. WAŻNE: zaznacz opcję "Add Python to PATH" przed kliknięciem Install

### Krok 2 — Zainstaluj VoxFlow

1. Pobierz lub rozpakuj folder VoxFlow na dysk
2. Kliknij dwukrotnie plik `install.bat`
3. Poczekaj aż zakończy instalację (2–5 minut) — instaluje wymagane biblioteki AI

### Krok 3 — Uruchom

Kliknij dwukrotnie `START_VOXFLOW.bat` (tworzony automatycznie przez install.bat).

Gotowe — VoxFlow jest teraz uruchomiony i widoczny w zasobniku systemowym (prawy dolny róg ekranu).

---

## 🖥️ Jak używać

| Akcja | Efekt |
|-------|-------|
| Przytrzymaj `F2` i mów | Nagrywa — na dole ekranu pojawia się animacja fal |
| Zwolnij `F2` | AI przetwarza mowę i wkleja tekst w aktywnym oknie |
| Kliknij przycisk klawisza w UI | Zmień skrót klawiszowy na dowolny inny |
| Kliknij dropdown mikrofonu | Wybierz urządzenie audio |
| Kliknij ikonę w zasobniku prawym przyciskiem | Menu: pokaż okno, nagraj, zamknij |

---

## 📦 Wersja EXE (bez Pythona)

Jeśli chcesz wersję, która nie wymaga instalacji Pythona:

Opcja A — Instalator (zalecana):

```
BUILD_EXE.bat  →  tworzy VoxFlow_Setup.exe
```

Wymaga [Inno Setup 6](https://jrsoftware.org/isinfo.php).

Opcja B — Portable (nie wymaga instalacji):

```
CREATE_PORTABLE.bat  →  tworzy dist\VoxFlow_Portable_v1.1.0\
```

Uruchom `START_VOXFLOW.bat` z folderu portable.

---

## ✨ Funkcje

| 🇵🇱 | 🇬🇧 |
|-----|-----|
| � Dyktowanie przytrzymując klawisz | Hold-to-record hotkey |
| 🌍 Polski + Angielski + Niemiecki + więcej (auto-detekcja) | Polish + English + German + more (auto-detect) |
| 🌐 Tłumaczenie głos → Angielski (100% offline) | Voice → English translation (100% offline) |
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
| `small` | ~500 MB | ⚡⚡ | ⭐⭐⭐⭐ | Zalecany |
| `medium` | ~1.5 GB | ⚡ | ⭐⭐⭐⭐⭐ | Dobry PC |
| `large-v3` | ~3 GB | 🐢 | ⭐⭐⭐⭐⭐ | GPU |

> Model pobiera się automatycznie przy pierwszej zmianie (jednorazowo).

---

## 🍎 Instalacja macOS

```bash
chmod +x install_mac.sh
./install_mac.sh
```

> Skrypt automatycznie instaluje `portaudio`, `pynput` (globalny hotkey) i sprawdza Tkinter.  
> Globalny hotkey wymaga uprawnień Accessibility w System Settings.  
> Szczegóły i rozwiązywanie problemów: [INSTALL\_MAC.md](INSTALL_MAC.md)

---

## 📜 Licencja

MIT License — bezpłatny, open source. Używaj, modyfikuj i dystrybuuj bez ograniczeń.

---

<div align="center">

AI Evolution Polska — Bezpłatne narzędzia AI dla polskich użytkowników

[![GitHub](https://img.shields.io/badge/GitHub-aievolutionpl-181717?logo=github)](https://github.com/aievolutionpl)

</div>
