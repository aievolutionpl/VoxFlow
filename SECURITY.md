# 🔒 Polityka Bezpieczeństwa — Security Policy

## Wspierane wersje

| Wersja | Status |
|--------|--------|
| 1.0.x  | ✅ Wspierana |

## Zgłaszanie podatności

Jeśli odkryjesz lukę bezpieczeństwa w VoxFlow:

1. **NIE** twórz publicznego Issue
2. Wyślij opis na: **kontakt@aievolutionpolska.pl** (lub otwórz prywatny Security Advisory na GitHubie)
3. W zgłoszeniu podaj:
   - Opis podatności
   - Kroki do reprodukcji
   - Potencjalny wpływ
   - Propozycję naprawy (jeśli możliwe)

### Czas reakcji

- **Potwierdzenie**: do 48 godzin
- **Wstępna ocena**: do 7 dni
- **Poprawka**: w zależności od poziomu krytyczności

## Zakres bezpieczeństwa

### Co obejmuje ten projekt

- Bezpieczne przechowywanie konfiguracji (`%APPDATA%/VoxFlow/`)
- Bezpieczna obsługa rejestru Windows (autostart)
- Walidacja danych wejściowych z plików konfiguracyjnych
- Bezpieczeństwo przetwarzania audio (wyłącznie lokalne)

### Co NIE jest podatnością

- **Brak szyfrowania konfiguracji** — plik `config.json` zawiera wyłącznie preferencje UI, brak danych wrażliwych
- **Dostęp do mikrofonu** — wymagany do działania aplikacji, użytkownik wyraża zgodę przy uruchomieniu
- **Dostęp do klawiatury** — wymagany do hotkeya i auto-wpisywania
- **Dostęp do schowka** — wymagany do kopiowania transkrypcji

## Prywatność

VoxFlow jest **w 100% lokalne**:
- ❌ Żadne dane audio nie są wysyłane do internetu
- ❌ Żadna telemetria nie jest zbierana
- ❌ Żadne dane użytkownika nie opuszczają komputera
- ✅ Modele Whisper są pobierane jednorazowo z Hugging Face i cachowane lokalnie

---

*Zbudowane przez [AI Evolution Polska](https://github.com/aievolutionpl)*
