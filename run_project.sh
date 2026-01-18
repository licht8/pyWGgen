#!/bin/bash
# run_project.sh
## Skrypt instalacyjny i uruchomieniowy projektu pyWGgen

# Nazwy repozytorium i katalogów
GITHUB_REPO="https://github.com/licht8/pyWGgen.git"
PROJECT_DIR="pyWGgen"
VENV_DIR="venv" # Upewnij się, że ścieżka jest względna aby utworzyć ją w $PROJECT_DIR
# WIREGUARD_INSTALL_SCRIPT="wireguard-install.sh"
WIREGUARD_BINARY="/usr/bin/wg"

# Sprawdź czy włączony jest tryb debugowania
DEBUG=false
if [[ $1 == "--debug" ]]; then
    DEBUG=true
fi

# Kolory wyjścia
RESET='\033[0m'
RED='\033[1;31m'
GREEN='\033[1;32m'
BOLD='\033[1m'
UNDERLINE='\033[4m'

echo -e "\n=== Instalacja projektu pyWGgen ===\n"

# Funkcja do parsowania portu Gradio z settings.py
get_gradio_port() {
    local file_path="pyWGgen/settings.py"
    local port

    # Wyodrębnij wartość GRADIO_PORT
    port=$(grep -oP 'GRADIO_PORT\s*=\s*\K\d+' "$file_path")

    # Sprawdź czy port został znaleziony
    if [[ -n "$port" ]]; then
        echo "$port"
    else
        echo "Port nie został znaleziony."
    fi
}

# Wywołaj funkcję
GRADIO_PORT=$(get_gradio_port)

# Upewnij się że skrypt jest uruchamiany z uprawnieniami superużytkownika
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED} ❌ Uruchom skrypt z uprawnieniami superużytkownika (sudo).${RESET}"
    echo "Na przykład: sudo $0"
    exit 1
fi

# Sprawdź czy Git jest zainstalowany
if ! command -v git &>/dev/null; then
  echo -e "${RED} ❌ Git nie jest zainstalowany. Zainstaluj go i spróbuj ponownie.${RESET}"
  exit 1
fi

# Sprawdź i zainstaluj Node.js jeśli potrzeba
if ! command -v node &>/dev/null; then
  echo " 🔄 Node.js nie jest zainstalowany. Instalowanie..."
  curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash - &>/dev/null || { echo -e "${RED} ❌ Błąd dodawania repozytorium Node.js.${RESET}"; exit 1; }
  sudo dnf install -y nodejs &>/dev/null || { echo -e "${RED} ❌ Błąd instalowania Node.js.${RESET}"; exit 1; }
  echo -e "\n ✅ Node.js pomyślnie zainstalowany."
else
  echo " ✅ Node.js jest już zainstalowany. Wersja: $(node --version)"
fi

# Przywróć priorytet Python 3.11 jeśli był zmieniony
PYTHON_PATH="/usr/bin/python3.11"
if [ -f "$PYTHON_PATH" ]; then
  sudo alternatives --set python3 $PYTHON_PATH || { echo -e "${RED} ❌ Błąd ustawiania Python 3.11.${RESET}"; exit 1; }
  echo " ✅ Python 3.11 ustawiony jako domyślna wersja."
else
  echo -e "${RED} ❌ Python 3.11 nie znaleziony. Zainstaluj ręcznie.${RESET}"
  exit 1
fi

# Sprawdź narzędzie bc i zainstaluj jeśli brak
install_bc_if_not_found() {
    if ! command -v bc &>/dev/null; then
        echo " 🔄 Narzędzie 'bc' nie znalezione. Instalowanie..."
        sudo dnf install -y bc &>/dev/null || { echo -e "${RED} ❌ Błąd instalowania 'bc'.${RESET}"; exit 1; }
        echo " ✅ Narzędzie 'bc' pomyślnie zainstalowane."
    else
        echo " ✅ Narzędzie 'bc' jest już zainstalowane."
    fi
}

install_bc_if_not_found

# Sprawdź wersję Pythona
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if (( PYTHON_MAJOR < 3 || (PYTHON_MAJOR == 3 && PYTHON_MINOR < 8) )); then
  echo -e "${RED} ❌ Wymagany jest Python 3.8 lub wyższy. Zainstaluj odpowiednią wersję.${RESET}"
  exit 1
else
  echo " ✅ Wykryto Python wersja $PYTHON_MAJOR.$PYTHON_MINOR."
fi

# Sklonuj lub zaktualizuj repozytorium
if [ ! -d "$PROJECT_DIR" ]; then
  echo " 🔄 Klonowanie repozytorium..."
  git clone "$GITHUB_REPO" || { echo -e "${RED} ❌ Błąd klonowania repozytorium.${RESET}"; exit 1; }
  FIRST_INSTALL=true
else
  echo " 🔄 Repo już istnieje. Aktualizacja..."
  echo "=========================================="
  git -C "$PROJECT_DIR" pull || { echo -e "${RED} ❌ Błąd aktualizacji repozytorium.${RESET}"; exit 1; }
  FIRST_INSTALL=false
fi

# Przejdź do katalogu projektu
cd "$PROJECT_DIR" || exit

# Utwórz i aktywuj środowisko wirtualne
if [ ! -d "$VENV_DIR" ]; then
  echo " 🔧 Tworzenie środowiska wirtualnego..."
  python3 -m venv "$VENV_DIR" || { echo -e "${RED} ❌ Błąd tworzenia środowiska wirtualnego.${RESET}"; exit 1; }
fi

# Aktywuj środowisko wirtualne
echo "=========================================="
echo -e " 🔄 Aktywowanie środowiska wirtualnego..."
source "$VENV_DIR/bin/activate" || { echo -e "${RED} ❌ Nie udało się aktywować środowiska wirtualnego.${RESET}"; exit 1; }

# Zainstaluj zależności
echo " 📦 Instalowanie zależności..."
if [ "$FIRST_INSTALL" = true ] || [ "$DEBUG" = true ]; then
  pip install --upgrade pip
  pip install -r "requirements.txt" || { echo -e "${RED} ❌ Błąd instalowania zależności.${RESET}"; exit 1; }
else
  pip install --upgrade pip &>/dev/null
  pip install -r "requirements.txt" &>/dev/null
  echo " ✅ Wszystkie zależności są już zainstalowane."
fi

# Sprawdź czy istnieje menu.py
if [ ! -f "menu.py" ]; then
  echo -e "${RED} ❌ Plik menu.py nie znaleziony. Upewnij się że znajduje się w folderze $PROJECT_DIR.${RESET}"
  exit 1
fi

# Informacje systemowe przed uruchomieniem menu
echo -e "\n=== Informacje systemowe ==="
echo -e "\n 🖥️  System: $(cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '"')"
echo -e " 🧰 Jądro: $(uname -r)"
EXTERNAL_IP=$(curl -s ifconfig.me)
echo -e " 🌍 Zewnętrzny adres IP: ${EXTERNAL_IP}"
FIREWALL_PORTS=$(sudo firewall-cmd --list-ports)
if [ -z "$FIREWALL_PORTS" ]; then
  echo -e " 🔓 Otwarte porty w firewalld: Brak. Sprawdź ustawienia."
else
  echo -e " 🔓 Otwarte porty w firewalld: ${FIREWALL_PORTS}"
fi

if ! systemctl is-active --quiet wg-quick@wg0; then
  echo -e " 🛡️  Status WireGuard: nieaktywny. Zainstaluj i skonfiguruj WireGuard dla pełnej funkcjonalności."
else
  echo -e " 🛡️  Status WireGuard: aktywny"
fi

echo -e " ⚙️  Plik konfiguracyjny WireGuard: /etc/wireguard/wg0.conf"
echo -e " 🌐 Panel administracyjny Gradio: http://${EXTERNAL_IP}:${GRADIO_PORT}"
echo -e " 📂 Repozytorium: https://github.com/licht8/pyWGgen"
echo -e "\n=========================================="

# Wyświetl komunikat o powodzeniu
echo -e "\n ✅ Instalacja zakończona. Projekt gotowy do użycia."

# Uruchom menu
echo -e " 🔄 Uruchamianie menu...\n"
sleep 1 && clear
python3 menu.py || { echo -e "${RED} ❌ Błąd uruchamiania menu.${RESET}"; exit 1; }
