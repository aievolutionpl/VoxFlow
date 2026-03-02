# 🎤 VoxFlow — Instalacja na macOS

**VoxFlow** — bezpłatne, lokalne narzędzie do dyktowania głosem. 100% offline.  
by [AI Evolution Polska](https://github.com/aievolutionpl)

---

## ⚡ Instalacja jednym kliknięciem

### Krok 1 — Pobierz VoxFlow

```bash
git clone https://github.com/aievolutionpl/VoxFlow.git
cd VoxFlow
```

---

### Krok 2 — Uruchom instalator

```bash
chmod +x install_mac.sh
./install_mac.sh
```

Skrypt automatycznie:
- ✅ Sprawdzi i zainstaluje [Homebrew](https://brew.sh) (jeśli brakuje)
- ✅ Zainstaluje `portaudio` (wymagane przez sounddevice)
- ✅ Sprawdzi Python 3.9+ (zainstaluje jeśli brakuje)
- ✅ Stworzy wirtualne środowisko (`venv`)
- ✅ Zainstaluje wszystkie biblioteki
- ✅ Stworzy launcher `VoxFlow.command`

---

### Krok 3 — Uruchomienie

Kliknij dwukrotnie plik `VoxFlow.command` lub uruchom:

```bash
./VoxFlow.command
```

---

## ⚠️ Uprawnienia Accessibility (globalny hotkey)

> [!IMPORTANT]
> Aby skrót klawiszowy (np. F2) działał we **wszystkich** aplikacjach, macOS wymaga przyznania uprawnień Accessibility.

1. Otwórz **System Settings** → **Privacy & Security** → **Accessibility**
2. Kliknij `+` i dodaj:
   - Terminal (jeśli uruchamiasz przez terminal)
   - lub `VoxFlow.command`
3. Uruchom VoxFlow ponownie

> [!NOTE]
> Bez tych uprawnień hotkey działa tylko gdy VoxFlow jest aktywną aplikacją na pierwszym planie.

---

## 🍎 Apple Silicon (M1/M2/M3)

Skrypt automatycznie wykrywa architekturę. Na Apple Silicon:
- Homebrew instaluje się do `/opt/homebrew/`
- `faster-whisper` obsługuje ARM64 natywnie
- Wydajność jest doskonała bez GPU

---

## ❓ Częste problemy

| Problem | Rozwiązanie |
|---------|-------------|
| `command not found: brew` | Zainstaluj [Homebrew](https://brew.sh) ręcznie |
| `portaudio` błąd | `brew install portaudio` |
| `tkinter` nie znaleziony | `brew install python-tk@3.11` |
| Python za stary | `brew install python@3.11` |
| Hotkey nie działa globalnie | Dodaj do Accessibility (patrz sekcja poniżej) |
| `pynput` błąd | `pip install pynput` (instalowany automatycznie) |
| Błąd pobierania modelu | Sprawdź połączenie internetowe |

---

## 📋 Wymagania systemowe

- macOS 11 Big Sur lub nowszy
- Intel lub Apple Silicon (M1/M2/M3)
- Python 3.9–3.12
- Homebrew (instalowany automatycznie)
- 4 GB RAM (8 GB zalecane)
- Mikrofon
- Połączenie internetowe (pierwsze pobranie modelu ~500 MB)

---

## 🌐 Funkcja tłumaczenia (nowość)

VoxFlow posiada wbudowane tłumaczenie głosowe **100% offline**:  
Mów po polsku, niemiecku, francusku → tekst pojawia się po **angielsku**.

Aktywacja: **⚙ Ustawienia → 🌐 Tłumacz głos → angielski** (toggle)

> Działa bez internetu — Whisper tłumaczy lokalnie.
