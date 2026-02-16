# 🤝 Współpraca — Contributing

Dziękujemy za zainteresowanie projektem VoxFlow! Każda pomoc jest mile widziana.

## 🐛 Zgłaszanie błędów

1. Sprawdź [istniejące Issues](../../issues), czy Twój problem nie został już zgłoszony
2. Utwórz nowy Issue z opisem:
   - **System**: Windows 10/11, wersja Python
   - **Model Whisper**: jaki model używasz (tiny/base/small/medium/large-v3)
   - **Opis błędu**: co się dzieje, czego oczekujesz
   - **Kroki do reprodukcji**: jak odtworzyć problem
   - **Logi**: jeśli są dostępne

## 💡 Propozycje funkcji

Otwórz Issue z etykietą `enhancement` i opisz:
- Co chcesz osiągnąć
- Dlaczego to ważne
- Jak to powinno działać

## 🔧 Pull Requests

### Jak przygotować zmianę

```bash
# 1. Sforkuj repozytorium na GitHubie

# 2. Sklonuj swój fork
git clone https://github.com/TWOJ-USER/VoxFlow.git
cd VoxFlow

# 3. Stwórz brancha
git checkout -b feature/moja-zmiana

# 4. Zainstaluj zależności
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 5. Wprowadź zmiany i przetestuj
python -m voxflow.main --test

# 6. Commituj i wypchnij
git add .
git commit -m "feat: opis zmiany"
git push origin feature/moja-zmiana

# 7. Otwórz Pull Request na GitHubie
```

### Konwencje commitów

Używamy [Conventional Commits](https://www.conventionalcommits.org/):

| Prefiks | Opis |
|---------|------|
| `feat:` | Nowa funkcja |
| `fix:` | Poprawka błędu |
| `docs:` | Zmiany w dokumentacji |
| `style:` | Formatowanie kodu |
| `refactor:` | Refaktoryzacja |
| `perf:` | Poprawa wydajności |
| `test:` | Dodanie testów |
| `chore:` | Utrzymanie projektu |

### Styl kodu

- **Python 3.9+** — używaj type hints
- **Docstringi** — dla każdej klasy i publicznej metody
- **Komentarze** — po polsku lub angielsku
- **Max 120 znaków** na linię

## 📋 Checklist przed PR

- [ ] Kod się kompiluje (`python -m py_compile voxflow/app.py`)
- [ ] Test importów przechodzi (`python -m voxflow.main --test`)
- [ ] Dodano docstringi do nowych funkcji
- [ ] README zaktualizowany (jeśli dotyczy)

## 🌍 Tłumaczenia

VoxFlow jest głównie po polsku, ale chętnie przyjmiemy tłumaczenia UI na inne języki!

---

**Dziękujemy za wkład! 🎉**
