<div align="center">

# 🎤 VoxFlow

### Dyktowanie głosem • 100% Offline • Open Source

[![License: MIT](https://img.shields.io/badge/License-MIT-7c3aed.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-lightgrey)](https://github.com/aievolutionpl/VoxFlow)
[![AI Evolution Polska](https://img.shields.io/badge/by-AI_Evolution_Polska-7c3aed)](https://github.com/aievolutionpl)

**VoxFlow** to bezpłatne, open-source narzędzie do dyktowania głosem na komputer.  
Zamień głos w tekst jednym przytrzymaniem klawisza — bez chmury, bez subskrypcji.

[🪟 Instalacja Windows](#-instalacja--windows) • [🍎 Instalacja macOS](#-instalacja--macos) • [✨ Funkcje](#-funkcje) • [📖 Użytkowanie](#-użytkowanie)

---

> **Free & Open Source speech-to-text dictation for Windows and macOS.**  
> Hold your hotkey → speak → text appears. 100% local, no cloud, no subscription.

</div>

---

## ✨ Funkcje / Features

| 🇵🇱 | 🇬🇧 |
|-----|-----|
| 🎤 Dyktowanie trzymając klawisz | Hold-to-record with configurable hotkey |
| 🌍 Polski + Angielski (auto-detekcja) | Polish + English (auto-detection) |
| ⚡ 100% lokalne — zero chmury | 100% local — zero cloud |
| 🧠 OpenAI Whisper (faster-whisper) | OpenAI Whisper (faster-whisper) |
| ✍️ Auto-wpisywanie w aktywne okno | Auto-type into active window |
| 🎙 Wybór urządzenia mikrofonowego | Microphone device selection |
| ⌨️ Dowolny klawisz (naciśnij aby ustawić) | Any hotkey (press to set) |
| 📋 Auto-kopiowanie do schowka | Auto-copy to clipboard |
| 🔲 Ikona w zasobniku systemowym | System tray icon |
| 📚 Historia nagrań | Recording history |
| ✨ Autokorekta tekstu | Text auto-correction |

---

## 🪟 Instalacja — Windows

### Wymagania
- Windows 10 / 11 (64-bit)
- **Python 3.9+** z opcją [Add Python to PATH](https://www.python.org/downloads/)
- Mikrofon

### Instalacja w 2 krokach

```
1. Pobierz Python 3.10+ ze strony python.org (zaznacz "Add Python to PATH")
2. Kliknij dwukrotnie install.bat
```

Szczegółowa instrukcja: [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)

---

## 🍎 Instalacja — macOS

### Wymagania
- macOS 11+ (Intel lub Apple Silicon M1/M2/M3)
- Python 3.9+ (instalowany automatycznie)
- Mikrofon

### Instalacja w 2 krokach

```bash
chmod +x install_mac.sh
./install_mac.sh
```

> ⚠️ Globalny hotkey wymaga uprawnień **Accessibility** w System Settings.  
> Szczegóły: [INSTALL_MAC.md](INSTALL_MAC.md)

---

## 📖 Użytkowanie / Usage

1. **Uruchom VoxFlow** — pojawi się okno aplikacji i ikona w zasobniku
2. **Przytrzymaj klawisz** (domyślnie `F2`) i mów
3. **Zwolnij klawisz** — tekst pojawi się automatycznie w aktywnym oknie
4. **Zmień klawisz** — kliknij przycisk klawisza i naciśnij dowolny klawisz
5. **Zmień mikrofon** — użyj dropdown'u z listą urządzeń

### Obsługiwane klawisze
`F2` `F3` `F4` `F5` `F6` `F7` `F8` `F9` `F10` `Ctrl+Space` `CapsLock` `Insert` i inne

---

## 🧠 Wybór modelu Whisper

| Model | Rozmiar | Szybkość | Jakość | Rekomendacja |
|-------|---------|----------|--------|--------------|
| `tiny` | ~75 MB | ⚡⚡⚡⚡ | ⭐⭐ | Testy |
| `base` | ~150 MB | ⚡⚡⚡ | ⭐⭐⭐ | Słaby PC |
| `small` | ~500 MB | ⚡⚡ | ⭐⭐⭐⭐ | **Zalecany** |
| `medium` | ~1.5 GB | ⚡ | ⭐⭐⭐⭐⭐ | Dobry PC |
| `large-v3` | ~3 GB | 🐢 | ⭐⭐⭐⭐⭐ | GPU |

> Pierwsza zmiana modelu wymaga pobrania jego pliku (jednorazowo).

---

## 🛠️ Budowanie .exe (Windows)

```bash
BUILD_EXE.bat
```

Wymaga [Inno Setup 6](https://jrsoftware.org/isinfo.php) do stworzenia instalatora.

---

## 📜 Licencja / License

MIT License — bezpłatny, open source.  
Możesz używać, modyfikować i dystrybuować bez ograniczeń.

---

## 🤝 Twórca / Author

<div align="center">

**AI Evolution Polska**  
Bezpłatne narzędzia AI dla polskich użytkowników

[![GitHub](https://img.shields.io/badge/GitHub-aievolutionpl-181717?logo=github)](https://github.com/aievolutionpl)

</div>
