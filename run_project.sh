#!/bin/bash
# run_project.sh
## Установочный и стартовый скрипт проекта wg_qr_generator

# Название репозитория и директории
GITHUB_REPO="https://github.com/licht8/wg_qr_generator.git"
PROJECT_DIR="wg_qr_generator"
VENV_DIR="venv"
WIREGUARD_INSTALL_SCRIPT="wireguard-install.sh"
WIREGUARD_BINARY="/usr/bin/wg"

echo "=== Установка проекта wg_qr_generator ==="

# Проверяем наличие Git
if ! command -v git &>/dev/null; then
  echo "❌ Git не установлен. Установите его и повторите попытку."
  exit 1
fi

# Установка Node.js
echo "🔄 Установка Node.js..."
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo dnf install -y nodejs
if command -v node &>/dev/null; then
  echo "✅ Node.js установлен. Версия: $(node --version)"
else
  echo "❌ Ошибка при установке Node.js."
  exit 1
fi

# Проверяем и восстанавливаем приоритет Python 3.11, если он сбит
PYTHON_PATH="/usr/bin/python3.11"
if [ -f "$PYTHON_PATH" ]; then
  sudo alternatives --install /usr/bin/python3 python3 $PYTHON_PATH 2
  sudo alternatives --set python3 $PYTHON_PATH
  echo "✅ Python 3.11 настроен как основная версия."
else
  echo "❌ Python 3.11 не найден. Установите его вручную."
  exit 1
fi

# Проверяем версию Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
  echo "❌ Требуется Python версии 3.8 или выше. Установите соответствующую версию."
  exit 1
else
  echo "✅ Python версии $PYTHON_VERSION обнаружен."
fi

# Клонируем или обновляем репозиторий
if [ ! -d "$PROJECT_DIR" ]; then
  echo "🔄 Клонирование репозитория..."
  git clone "$GITHUB_REPO"
else
  echo "🔄 Репозиторий уже существует. Обновляем..."
  git -C "$PROJECT_DIR" pull
fi

# Создаем и активируем виртуальное окружение
if [ ! -d "$VENV_DIR" ]; then
  echo "🔧 Создание виртуального окружения..."
  python3 -m venv "$VENV_DIR"
fi

# Активируем виртуальное окружение
source "$VENV_DIR/bin/activate"

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip install --upgrade pip
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
  pip install -r "$PROJECT_DIR/requirements.txt"
else
  echo "⚠️ Файл requirements.txt не найден. Проверьте проект."
fi

echo "✅ Установка завершена. Проект готов к работе."
