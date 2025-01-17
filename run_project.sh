#!/bin/bash
# run_project.sh
## Installation and startup script for the pyWGgen project

# Repository and directory names
GITHUB_REPO="https://github.com/licht8/pyWGgen.git"
PROJECT_DIR="pyWGgen"
VENV_DIR="venv" # Ensure the path is relative to create it within $PROJECT_DIR
WIREGUARD_INSTALL_SCRIPT="wireguard-install.sh"
WIREGUARD_BINARY="/usr/bin/wg"

# Check if debug mode is enabled
DEBUG=false
if [[ $1 == "--debug" ]]; then
    DEBUG=true
fi

# Output colors
RESET='\033[0m'
RED='\033[1;31m'
GREEN='\033[1;32m'
BOLD='\033[1m'
UNDERLINE='\033[4m'

echo -e "\n=== Installing the pyWGgen Project ===\n"

# Function to parse the Gradio port from settings.py
get_gradio_port() {
    local file_path="pyWGgen/settings.py"
    local port

    # Extract GRADIO_PORT value
    port=$(grep -oP 'GRADIO_PORT\s*=\s*\K\d+' "$file_path")

    # Check if the port was found
    if [[ -n "$port" ]]; then
        echo "$port"
    else
        echo "Port not found."
    fi
}

# Call the function
GRADIO_PORT=$(get_gradio_port)

# Ensure the script is run with superuser privileges
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED} ❌ Please run the script with superuser privileges (sudo).${RESET}"
    echo "For example: sudo $0"
    exit 1
fi

# Check if Git is installed
if ! command -v git &>/dev/null; then
  echo -e "${RED} ❌ Git is not installed. Please install it and try again.${RESET}"
  exit 1
fi

# Check and install Node.js if necessary
if ! command -v node &>/dev/null; then
  echo " 🔄 Node.js is not installed. Installing..."
  curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash - &>/dev/null || { echo -e "${RED} ❌ Error adding the Node.js repository.${RESET}"; exit 1; }
  sudo dnf install -y nodejs &>/dev/null || { echo -e "${RED} ❌ Error installing Node.js.${RESET}"; exit 1; }
  echo -e "\n ✅ Node.js successfully installed."
else
  echo " ✅ Node.js is already installed. Version: $(node --version)"
fi

# Restore Python 3.11 priority if it was altered
PYTHON_PATH="/usr/bin/python3.11"
if [ -f "$PYTHON_PATH" ]; then
  sudo alternatives --set python3 $PYTHON_PATH || { echo -e "${RED} ❌ Error setting Python 3.11.${RESET}"; exit 1; }
  echo " ✅ Python 3.11 set as the default version."
else
  echo -e "${RED} ❌ Python 3.11 not found. Please install it manually.${RESET}"
  exit 1
fi

# Check for the bc utility and install it if not found
install_bc_if_not_found() {
    if ! command -v bc &>/dev/null; then
        echo " 🔄 'bc' utility not found. Installing..."
        sudo dnf install -y bc &>/dev/null || { echo -e "${RED} ❌ Error installing 'bc'.${RESET}"; exit 1; }
        echo " ✅ 'bc' utility successfully installed."
    else
        echo " ✅ 'bc' utility is already installed."
    fi
}

install_bc_if_not_found

# Check Python version
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if (( PYTHON_MAJOR < 3 || (PYTHON_MAJOR == 3 && PYTHON_MINOR < 8) )); then
  echo -e "${RED} ❌ Python 3.8 or higher is required. Please install the appropriate version.${RESET}"
  exit 1
else
  echo " ✅ Python version $PYTHON_MAJOR.$PYTHON_MINOR detected."
fi

# Clone or update the repository
if [ ! -d "$PROJECT_DIR" ]; then
  echo " 🔄 Cloning the repository..."
  git clone "$GITHUB_REPO" || { echo -e "${RED} ❌ Error cloning the repository.${RESET}"; exit 1; }
  FIRST_INSTALL=true
else
  echo " 🔄 Repository already exists. Updating..."
  echo "=========================================="
  git -C "$PROJECT_DIR" pull || { echo -e "${RED} ❌ Error updating the repository.${RESET}"; exit 1; }
  FIRST_INSTALL=false
fi

# Navigate to the project directory
cd "$PROJECT_DIR" || exit

# Create and activate a virtual environment
if [ ! -d "$VENV_DIR" ]; then
  echo " 🔧 Creating a virtual environment..."
  python3 -m venv "$VENV_DIR" || { echo -e "${RED} ❌ Error creating the virtual environment.${RESET}"; exit 1; }
fi

# Activate the virtual environment
echo "=========================================="
echo -e " 🔄 Activating the virtual environment..."
source "$VENV_DIR/bin/activate" || { echo -e "${RED} ❌ Failed to activate the virtual environment.${RESET}"; exit 1; }

# Install dependencies
echo " 📦 Installing dependencies..."
if [ "$FIRST_INSTALL" = true ] || [ "$DEBUG" = true ]; then
  pip install --upgrade pip
  pip install -r "requirements.txt" || { echo -e "${RED} ❌ Error installing dependencies.${RESET}"; exit 1; }
else
  pip install --upgrade pip &>/dev/null
  pip install -r "requirements.txt" &>/dev/null
  echo " ✅ All dependencies are already installed."
fi

# Check if menu.py exists
if [ ! -f "menu.py" ]; then
  echo -e "${RED} ❌ menu.py file not found. Ensure it is located in the $PROJECT_DIR folder.${RESET}"
  exit 1
fi

# System information before launching the menu
echo -e "\n=== System Information ==="
echo -e "\n 🖥️  OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '"')"
echo -e " 🧰 Kernel: $(uname -r)"
EXTERNAL_IP=$(curl -s ifconfig.me)
echo -e " 🌍 External IP Address: ${EXTERNAL_IP}"
FIREWALL_PORTS=$(sudo firewall-cmd --list-ports)
if [ -z "$FIREWALL_PORTS" ]; then
  echo -e " 🔓 Open ports in firewalld: None. Check the settings."
else
  echo -e " 🔓 Open ports in firewalld: ${FIREWALL_PORTS}"
fi

if ! systemctl is-active --quiet wg-quick@wg0; then
  echo -e " 🛡️  WireGuard status: inactive. Install and configure WireGuard for proper functionality."
else
  echo -e " 🛡️  WireGuard status: active"
fi

echo -e " ⚙️  WireGuard configuration file: /etc/wireguard/wg0.conf"
echo -e " 🌐 Gradio admin panel: http://${EXTERNAL_IP}:${GRADIO_PORT}"
echo -e " 📂 Repository: https://github.com/licht8/pyWGgen"
echo -e "\n=========================================="

# Display a success message
echo -e "\n ✅ Installation complete. The project is ready to use."

# Launch the menu
echo -e " 🔄 Launching the menu...\n"
sleep 1 && clear
python3 menu.py || { echo -e "${RED} ❌ Error launching the menu.${RESET}"; exit 1; }
