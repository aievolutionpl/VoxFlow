# 🎤 VoxFlow — Instalacja na Windows

**VoxFlow** — bezpłatne, lokalne narzędzie do dyktowania głosem. 100% offline. Brak chmury.  
by [AI Evolution Polska](https://github.com/aievolutionpl)

---

## ⚡ Instalacja jednym kliknięciem

### Krok 1 — Pobierz Python 3.10+

> [!IMPORTANT]
> Python **musi** być zainstalowany przed uruchomieniem instalatora VoxFlow.
> **Zaznacz opcję "Add Python to PATH"** podczas instalacji!

👉 [Pobierz Python ze python.org](https://www.python.org/downloads/)

Sprawdź instalację (otwórz `cmd`):
```
python --version
```
Powinno wyświetlić: `Python 3.10.x` lub nowszy.

---

### Krok 2 — Pobierz VoxFlow

Pobierz i rozpakuj archiwum lub sklonuj repozytorium:

```bash
git clone https://github.com/aievolutionpl/VoxFlow.git
cd VoxFlow
```

---

### Krok 3 — Uruchom instalator

Kliknij dwukrotnie plik:

```
install.bat
```

Skrypt automatycznie:
- ✅ Sprawdzi wersję Python
- ✅ Stworzy wirtualne środowisko (`venv`)
- ✅ Zainstaluje wszystkie biblioteki
- ✅ Zweryfikuje instalację
- ✅ Zaproponuje natychmiastowe uruchomienie

---

### Krok 4 — Uruchomienie

Po instalacji kliknij:
```
START_VOXFLOW.bat
```

Lub uruchom ręcznie:
```bash
venv\Scripts\activate
python -m voxflow.main
```

---

## 🔨 Budowanie instalatora .exe (opcjonalne)

Jeśli chcesz stworzyć samodzielny plik `.exe` do dystrybucji:

```bash
BUILD_EXE.bat
```

Wymagany [Inno Setup 6](https://jrsoftware.org/isinfo.php) do stworzenia instalatora `.exe`.

---

## ❓ Częste problemy

| Problem | Rozwiązanie |
|---------|-------------|
| `python` nie znany | Zainstaluj Python i dodaj do PATH |
| Błąd importu sounddevice | `pip install sounddevice` z C++ Redistributable |
| Hotkey nie działa | Uruchom jako Administrator |
| Błąd modelu Whisper | Sprawdź połączenie internetowe (tylko pierwsze pobieranie) |

---

## 📋 Wymagania systemowe

- Windows 10 / 11 (64-bit)
- Python 3.9–3.12
- 4 GB RAM (8 GB zalecane dla modelu `medium`)
- Mikrofon
- Połączenie internetowe (tylko do pierwszego pobrania modelu ~500 MB)
