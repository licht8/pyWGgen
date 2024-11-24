#!/bin/bash
# run_project.sh
## Установочный и стартовый скрипт проекта wg_qr_generator

# Название репозитория и директории
GITHUB_REPO="https://github.com/licht8/wg_qr_generator.git"
PROJECT_DIR="wg_qr_generator"
VENV_DIR="venv" # Убедимся, что путь относительный, для создания в $PROJECT_DIR
WIREGUARD_INSTALL_SCRIPT="wireguard-install.sh"
WIREGUARD_BINARY="/usr/bin/wg"

# Проверяем, включён ли режим debug
DEBUG=false
if [[ $1 == "--debug" ]]; then
    DEBUG=true
fi

# Цвета для вывода
RESET='\033[0m'
RED='\033[1;31m'
GREEN='\033[1;32m'
BOLD='\033[1m'
UNDERLINE='\033[4m'

echo -e "\n=== Установка проекта wg_qr_generator ==="

# Проверяем запуск с правами суперпользователя
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Пожалуйста, запустите скрипт с правами суперпользователя (sudo).${RESET}"
    echo "Например: sudo $0"
    exit 1
fi

# Проверяем наличие Git
if ! command -v git &>/dev/null; then
  echo -e "${RED}❌ Git не установлен. Установите его и повторите попытку.${RESET}"
  exit 1
fi

# Проверяем и при необходимости устанавливаем Node.js
if ! command -v node &>/dev/null; then
  echo "🔄 Node.js не установлен. Устанавливаю..."
  curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash - &>/dev/null || { echo -e "${RED}❌ Ошибка при добавлении репозитория Node.js.${RESET}"; exit 1; }
  sudo dnf install -y nodejs &>/dev/null || { echo -e "${RED}❌ Ошибка при установке Node.js.${RESET}"; exit 1; }
  echo "✅ Node.js успешно установлен."
else
  echo "✅ Node.js уже установлен. Версия: $(node --version)"
fi

# Проверяем и восстанавливаем приоритет Python 3.11, если он сбит
PYTHON_PATH="/usr/bin/python3.11"
if [ -f "$PYTHON_PATH" ]; then
  sudo alternatives --set python3 $PYTHON_PATH || { echo -e "${RED}❌ Ошибка при настройке Python 3.11.${RESET}"; exit 1; }
  echo "✅ Python 3.11 настроен как основная версия."
else
  echo -e "${RED}❌ Python 3.11 не найден. Установите его вручную.${RESET}"
  exit 1
fi

# Проверяем наличие утилиты bc
install_bc_if_not_found() {
    if ! command -v bc &>/dev/null; then
        echo "🔄 Утилита 'bc' не найдена. Устанавливаю..."
        sudo dnf install -y bc &>/dev/null || { echo -e "${RED}❌ Ошибка при установке утилиты 'bc'.${RESET}"; exit 1; }
        echo "✅ Утилита 'bc' успешно установлена."
    else
        echo "✅ Утилита 'bc' уже установлена."
    fi
}

install_bc_if_not_found

# Проверяем версию Python
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if (( PYTHON_MAJOR < 3 || (PYTHON_MAJOR == 3 && PYTHON_MINOR < 8) )); then
  echo -e "${RED}❌ Требуется Python версии 3.8 или выше. Установите соответствующую версию.${RESET}"
  exit 1
else
  echo "✅ Python версии $PYTHON_MAJOR.$PYTHON_MINOR обнаружен."
fi

# Клонируем или обновляем репозиторий
if [ ! -d "$PROJECT_DIR" ]; then
  echo "🔄 Клонирование репозитория..."
  git clone "$GITHUB_REPO" || { echo -e "${RED}❌ Ошибка при клонировании репозитория.${RESET}"; exit 1; }
  FIRST_INSTALL=true
else
  echo "🔄 Репозиторий уже существует. Обновляем..."
  git -C "$PROJECT_DIR" pull || { echo -e "${RED}❌ Ошибка при обновлении репозитория.${RESET}"; exit 1; }
  FIRST_INSTALL=false
fi

# Переходим в папку проекта
cd "$PROJECT_DIR" || exit

# Создаем и активируем виртуальное окружение
if [ ! -d "$VENV_DIR" ]; then
  echo "🔧 Создание виртуального окружения..."
  python3 -m venv "$VENV_DIR" || { echo -e "${RED}❌ Ошибка при создании виртуального окружения.${RESET}"; exit 1; }
fi

# Активируем виртуальное окружение
echo "🔄 Активация виртуального окружения..."
source "$VENV_DIR/bin/activate" || { echo -e "${RED}❌ Не удалось активировать виртуальное окружение.${RESET}"; exit 1; }

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
if [ "$FIRST_INSTALL" = true ] || [ "$DEBUG" = true ]; then
  pip install --upgrade pip
  pip install -r "requirements.txt" || { echo -e "${RED}❌ Ошибка при установке зависимостей.${RESET}"; exit 1; }
else
  pip install --upgrade pip &>/dev/null
  pip install -r "requirements.txt" &>/dev/null
  echo "✅ Все зависимости уже установлены."
fi

# Проверяем наличие menu.py
if [ ! -f "menu.py" ]; then
  echo -e "${RED}❌ Файл menu.py не найден. Убедитесь, что он находится в папке $PROJECT_DIR.${RESET}"
  exit 1
fi

# Полезная информация перед запуском меню
echo -e "\n=== Полезная информация о системе ==="
echo -e "🖥️ ОС: $(cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"')"
echo -e "🧰 Ядро: $(uname -r)"
EXTERNAL_IP=$(curl -s ifconfig.me)
echo -e "🌍 Внешний IP-адрес: ${EXTERNAL_IP}"
FIREWALL_PORTS=$(sudo firewall-cmd --list-ports)
if [ -z "$FIREWALL_PORTS" ]; then
  echo -e "🔓 Открытые порты в firewalld: Нет открытых портов. Проверьте настройки."
else
  echo -e "🔓 Открытые порты в firewalld: ${FIREWALL_PORTS}"
fi

if ! systemctl is-active --quiet wg-quick@wg0; then
  echo -e "🛡️ WireGuard статус: не активен. Установите и настройте WireGuard для корректной работы."
else
  echo -e "🛡️ WireGuard статус: активен"
fi

echo -e "⚙️ Файл конфигурации WireGuard: /etc/wireguard/wg0.conf"
echo -e "🌐 Gradio админка: http://${EXTERNAL_IP}:7860"
echo -e "📂 Репозиторий: https://github.com/licht8/wg_qr_generator"
echo "======================================"

# Выводим сообщение об успешной установке
echo "✅ Установка завершена. Проект готов к работе."

# Запускаем меню
echo -e "🔄 Запуск меню...\n"
python3 menu.py || { echo -e "${RED}❌ Ошибка при запуске меню.${RESET}"; exit 1; }
