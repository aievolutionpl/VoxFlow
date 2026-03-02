#!/bin/bash
# VoxFlow — Instalacja macOS (Intel & Apple Silicon)
# by AI Evolution Polska | Open Source
# ─────────────────────────────────────────────────────────────────

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${CYAN}${BOLD}"
echo "  ╔══════════════════════════════════════════════════════╗"
echo "  ║        VoxFlow — Instalacja macOS                    ║"
echo "  ║           by AI Evolution Polska | Open Source       ║"
echo "  ╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# ─── Check macOS ────────────────────────────────────────────────
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}❌ Ten skrypt jest przeznaczony dla macOS.${NC}"
    echo "   Dla Windows użyj install.bat"
    exit 1
fi

ARCH=$(uname -m)
echo -e "  ${CYAN}Architektura:${NC} $ARCH"
if [[ "$ARCH" == "arm64" ]]; then
    echo -e "  ${GREEN}✅ Apple Silicon (M1/M2/M3) wykryty${NC}"
else
    echo -e "  ${GREEN}✅ Intel Mac wykryty${NC}"
fi

# ─── Check Homebrew ─────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════"
echo "  KROK 1: Sprawdzanie Homebrew..."
echo "══════════════════════════════════════════════════════"
echo ""

if ! command -v brew &>/dev/null; then
    echo -e "${YELLOW}  ℹ️  Homebrew nie znaleziony. Instaluję...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Add brew to PATH for Apple Silicon
    if [[ "$ARCH" == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> "$HOME/.zprofile"
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
    echo -e "${GREEN}  ✅ Homebrew zainstalowany${NC}"
else
    echo -e "${GREEN}  ✅ Homebrew już zainstalowany${NC}"
fi

# ─── Install PortAudio (needed by sounddevice) ──────────────────
echo ""
echo "══════════════════════════════════════════════════════"
echo "  KROK 2: Instalacja bibliotek audio (portaudio)..."
echo "══════════════════════════════════════════════════════"
echo ""

# Detect Homebrew prefix for portaudio lib path
BREW_PREFIX=$(brew --prefix 2>/dev/null || echo "/usr/local")

if brew list portaudio &>/dev/null; then
    echo -e "${GREEN}  ✅ portaudio już zainstalowany${NC}"
else
    brew install portaudio
    echo -e "${GREEN}  ✅ portaudio zainstalowany${NC}"
fi

# Export portaudio path so sounddevice can find the dylib
export DYLD_LIBRARY_PATH="${BREW_PREFIX}/lib:${DYLD_LIBRARY_PATH:-}"

# ─── Check Python 3.9+ ─────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════"
echo "  KROK 3: Sprawdzanie Python 3.9+..."
echo "══════════════════════════════════════════════════════"
echo ""

PYTHON_CMD=""
for cmd in python3.12 python3.11 python3.10 python3.9 python3; do
    if command -v $cmd &>/dev/null; then
        VERSION=$($cmd --version 2>&1 | awk '{print $2}')
        MAJOR=$(echo $VERSION | cut -d. -f1)
        MINOR=$(echo $VERSION | cut -d. -f2)
        if [[ $MAJOR -eq 3 && $MINOR -ge 9 ]]; then
            PYTHON_CMD=$cmd
            echo -e "${GREEN}  ✅ Python $VERSION — używam $cmd${NC}"
            break
        fi
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    echo -e "${YELLOW}  ℹ️  Python 3.9+ nie znaleziony. Instaluję przez Homebrew...${NC}"
    brew install python@3.11
    PYTHON_CMD="python3.11"
    echo -e "${GREEN}  ✅ Python 3.11 zainstalowany${NC}"
fi

# ─── Create venv ────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════"
echo "  KROK 4: Tworzenie środowiska wirtualnego..."
echo "══════════════════════════════════════════════════════"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ -d venv ]]; then
    echo -e "  ${CYAN}ℹ️  Środowisko venv już istnieje${NC}"
else
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}  ✅ Środowisko venv stworzone${NC}"
fi

source venv/bin/activate

# ─── Install requirements ────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════"
echo "  KROK 5: Instalacja wymaganych pakietów..."
echo "  (pierwsze uruchomienie może potrwać kilka minut)"
echo "══════════════════════════════════════════════════════"
echo ""

pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# Install pynput as macOS hotkey fallback (keyboard lib needs root on macOS)
pip install pynput --quiet 2>/dev/null || true

echo -e "${GREEN}  ✅ Pakiety zainstalowane${NC}"

# Ensure Tkinter is available — install python-tk via Homebrew if missing
python -c "import tkinter" 2>/dev/null || {
    echo -e "${YELLOW}  ℹ️  Tkinter nie znaleziony. Instaluję python-tk@3.11...${NC}"
    brew install python-tk@3.11 2>/dev/null || brew install python-tk 2>/dev/null || true
    echo -e "  ⚠️  Jeśli Tkinter nadal nie działa, uruchom: brew install python-tk@3.11"
}

# ─── Verify ─────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════"
echo "  KROK 6: Weryfikacja instalacji..."
echo "══════════════════════════════════════════════════════"
echo ""

if python -m voxflow.main --test; then
    echo -e "${GREEN}  ✅ Weryfikacja zakończona pomyślnie${NC}"
else
    echo -e "${YELLOW}  ⚠️  Weryfikacja z ostrzeżeniami — sprawdź błędy powyżej.${NC}"
    echo "  Typowe problemy:"
    echo "    • tkinter: brew install python-tk@3.11"
    echo "    • portaudio: brew install portaudio"
    echo "    • HotKey: dodaj Terminal do Accessibility w Ustawieniach"
fi

# ─── Create launcher ─────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════"
echo "  KROK 7: Tworzenie skrótu uruchamiania..."
echo "══════════════════════════════════════════════════════"
echo ""

LAUNCHER="$SCRIPT_DIR/VoxFlow.command"
cat > "$LAUNCHER" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
source venv/bin/activate
python -m voxflow.main
EOF
chmod +x "$LAUNCHER"
echo -e "${GREEN}  ✅ Launcher VoxFlow.command stworzony${NC}"

# ─── Accessibility warning (macOS keyboard hook) ─────────────────
echo ""
echo -e "${YELLOW}  ⚠️  WAŻNA INFORMACJA — Uprawnienia Accessibility:${NC}"
echo ""
echo "  Aby globalny hotkey (np. F2) działał we WSZYSTKICH aplikacjach,"
echo "  musisz nadać VoxFlow uprawnienia Accessibility:"
echo ""
echo "  1. Otwórz: Apple Menu → System Settings → Privacy & Security"
echo "  2. Kliknij: Accessibility"
echo "  3. Dodaj Terminal lub VoxFlow.command do listy"
echo ""
echo "  Bez tych uprawnień: hotkey działa tylko gdy VoxFlow jest na pierwszym planie."
echo ""

# ─── Done ────────────────────────────────────────────────────────
echo "══════════════════════════════════════════════════════"
echo -e "${GREEN}${BOLD}  ✅ VoxFlow zainstalowany pomyślnie!${NC}"
echo ""
echo "  Uruchom aplikację:"
echo "    • Kliknij dwukrotnie: VoxFlow.command"
echo "    • lub w terminalu: ./VoxFlow.command"
echo "══════════════════════════════════════════════════════"
echo ""

read -p "  Uruchomić VoxFlow teraz? [T/n]: " LAUNCH
if [[ "$LAUNCH" != "n" && "$LAUNCH" != "N" ]]; then
    echo ""
    echo -e "  ${CYAN}🚀 Uruchamianie VoxFlow...${NC}"
    python -m voxflow.main &
fi
