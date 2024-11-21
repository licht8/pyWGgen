#!/bin/bash
# run_project.sh
## Установочный и стартовый скрипт проекта wg_qr_generator

# Название репозитория и директории
GITHUB_REPO="https://github.com/licht8/wg_qr_generator.git"
PROJECT_DIR="wg_qr_generator"
VENV_DIR="venv" # Убедимся, что путь относительный, для создания в $PROJECT_DIR
WIREGUARD_INSTALL_SCRIPT="wireguard-install.sh"
WIREGUARD_BINARY="/usr/bin/wg"

echo -e "\n=== Установка проекта wg_qr_generator ==="

# Проверяем наличие Git
if ! command -v git &>/dev/null; then
  echo "❌ Git не установлен. Установите его и повторите попытку."
  exit 1
fi

# Проверяем и при необходимости устанавливаем Node.js
if ! command -v node &>/dev/null; then
  echo "🔄 Node.js не установлен. Устанавливаю..."
  curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash - &>/dev/null
  sudo dnf install -y nodejs &>/dev/null
  if command -v node &>/dev/null; then
    echo "✅ Node.js успешно установлен."
  else
    echo "❌ Ошибка при установке Node.js."
    exit 1
  fi
else
  echo "✅ Node.js уже установлен. Версия: $(node --version)"
fi

# Проверяем и восстанавливаем приоритет Python 3.11, если он сбит
PYTHON_PATH="/usr/bin/python3.11"
if [ -f "$PYTHON_PATH" ]; then
  # Устанавливаем Python 3.11 как основную версию
  sudo alternatives --set python3 $PYTHON_PATH
  echo "✅ Python 3.11 настроен как основная версия."
else
  echo "❌ Python 3.11 не найден. Установите его вручную."
  exit 1
fi

# Проверяем наличие утилиты bc
install_bc_if_not_found() {
    if ! command -v bc &>/dev/null; then
        echo "Утилита 'bc' не найдена. Устанавливаю..."
        sudo dnf install bc -y
    else
        echo "✅ Утилита 'bc' уже установлена."
    fi
}

install_bc_if_not_found

# Проверяем версию Python
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if (( PYTHON_MAJOR < 3 || (PYTHON_MAJOR == 3 && PYTHON_MINOR < 8) )); then
  echo "❌ Требуется Python версии 3.8 или выше. Установите соответствующую версию."
  exit 1
else
  echo "✅ Python версии $PYTHON_MAJOR.$PYTHON_MINOR обнаружен."
fi

# Клонируем или обновляем репозиторий
if [ ! -d "$PROJECT_DIR" ]; then
  echo "🔄 Клонирование репозитория..."
  git clone "$GITHUB_REPO"
else
  echo "🔄 Репозиторий уже существует. Обновляем..."
  git -C "$PROJECT_DIR" pull
fi

# Переходим в папку проекта
cd "$PROJECT_DIR" || exit

# Создаем и активируем виртуальное окружение
if [ ! -d "$VENV_DIR" ]; then
  echo "🔧 Создание виртуального окружения..."
  python3 -m venv "$VENV_DIR"
fi

# Активируем виртуальное окружение
echo "🔄 Активация виртуального окружения..."
source "$VENV_DIR/bin/activate" || { echo "❌ Не удалось активировать виртуальное окружение."; exit 1; }

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip install --upgrade pip &>/dev/null
if [ -f "requirements.txt" ]; then
  MISSING_DEPENDENCIES=$(pip install -r "requirements.txt" 2>&1 | grep -v "Requirement already satisfied")
  if [ -z "$MISSING_DEPENDENCIES" ]; then
    echo "✅ Все зависимости уже установлены."
  else
    echo "$MISSING_DEPENDENCIES"
  fi
else
  echo "⚠️ Файл requirements.txt не найден. Проверьте проект."
fi

# Проверяем наличие menu.py
if [ ! -f "menu.py" ]; then
  echo "❌ Файл menu.py не найден. Убедитесь, что он находится в папке $PROJECT_DIR."
  exit 1
fi

# Выводим сообщение об успешной установке
echo "✅ Установка завершена. Проект готов к работе."

# Запускаем меню
echo -e "🔄 Запуск меню...\n"
python3 menu.py || { echo "❌ Ошибка при запуске меню."; exit 1; }
