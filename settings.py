#!/usr/bin/env python3
# wg_qr_generator/settings.py
# ===========================================
# Настройки проекта wg_qr_generator
# ===========================================
# Этот файл содержит основные настройки проекта, включая пути к файлам,
# директориям, конфигурациям, а также глобальные параметры.
# Он централизует все важные переменные для упрощения поддержки проекта.
#
# Пример использования:
# ---------------------
# from settings import BASE_DIR, WG_CONFIG_DIR, GRADIO_PORT
# 
# print(f"Корневая директория проекта: {BASE_DIR}")
# print(f"Директория конфигураций WireGuard: {WG_CONFIG_DIR}")
# print(f"Порт для запуска Gradio: {GRADIO_PORT}")
#
# ВАЖНО: Все пути и параметры следует указывать относительно BASE_DIR.
# ===========================================
# Логирование:
# Для управления логированием в проекте используется модуль logging.
# Вы можете изменить уровень логирования через переменную LOG_LEVEL:
# - DEBUG: Вывод всех сообщений, включая отладочные.
# - INFO: Основные действия без отладочных сообщений.
# - WARNING: Только предупреждения и ошибки.
# - ERROR: Только ошибки.
# Логи записываются как в консоль, так и в файл, путь к которому указан в LOG_FILE_PATH.
#
# Версия: 1.5 (2024-12-02) 18:30

from pathlib import Path

# Определяем базовый путь к корню проекта
BASE_DIR = Path(__file__).resolve().parent  # Путь к корневой директории wg_qr_generator
PROJECT_DIR = BASE_DIR  # Для совместимости, PROJECT_DIR равен BASE_DIR

# Пути к файлам и директориям
WG_CONFIG_DIR = BASE_DIR / "user/data/wg_configs"  # Путь к конфигурациям WireGuard пользователей
QR_CODE_DIR = BASE_DIR / "user/data/qrcodes"      # Путь к сохраненным QR-кодам
STALE_CONFIG_DIR = BASE_DIR / "user/data/usr_stale_config"  # Путь к устаревшим конфигурациям пользователей
USER_DB_PATH = BASE_DIR / "user/data/user_records.json"  # База данных пользователей
IP_DB_PATH = BASE_DIR / "user/data/ip_records.json"      # База данных IP-адресов
SERVER_CONFIG_FILE = Path("/etc/wireguard/wg0.conf")     # Путь к конфигурационному файлу сервера WireGuard
PARAMS_FILE = Path("/etc/wireguard/params")             # Путь к файлу параметров WireGuard

# Параметры WireGuard
DEFAULT_TRIAL_DAYS = 30  # Базовый срок действия аккаунта в днях
WIREGUARD_PORT = 51820   # Порт для сервера WireGuard (по умолчанию)

# Настройки для логирования
LOG_DIR = BASE_DIR / "user/data/logs"  # Директория для хранения логов
DIAGNOSTICS_LOG = LOG_DIR / "diagnostics.log"  # Файл логов диагностики
SUMMARY_REPORT_PATH = LOG_DIR / "summary_report.txt"  # Файл для хранения обобщенного отчета
LOG_FILE_PATH = LOG_DIR / "app.log"  # Файл для записи логов приложения
LOG_LEVEL = "WARNING"  # Уровень логирования: DEBUG, INFO, WARNING, ERROR

# Пути к отчетам и базе сообщений
DEBUG_REPORT_PATH = BASE_DIR / "ai_diagnostics/debug_report.txt"  # Путь к отчету диагностики
TEST_REPORT_PATH = BASE_DIR / "ai_diagnostics/test_report.txt"    # Путь к отчету тестирования
MESSAGES_DB_PATH = BASE_DIR / "ai_diagnostics/messages_db.json"   # Путь к базе сообщений диагностики

# Пути к справке
HELP_JSON_PATH = BASE_DIR / "ai_diagnostics/ai_help/ai_help.json"  # Новый путь для справочной системы

# Дополнительные пути для модулей и утилит
MODULES_DIR = BASE_DIR / "modules"            # Директория с модулями
AI_DIAGNOSTICS_DIR = BASE_DIR / "ai_diagnostics"  # Директория с файлами диагностики

# Порт для Gradio
GRADIO_PORT = 7860  # Порт для запуска Gradio интерфейса

# Настройки скорости для анимации и имитации печати
ANIMATION_SPEED = 0.2  # Задержка между итерациями анимации (в секундах)
# Пример использования:
# - 0.2 (по умолчанию): Плавная анимация, комфортная для восприятия.
# - 0.1: Быстрая анимация, подходит для коротких сообщений.
# - 0.5: Медленная анимация, создаёт акцент на процессе.

PRINT_SPEED = 0.02  # Скорость вывода символов (в секундах)
# Пример использования:
# - 0.02 (по умолчанию): Стандартная скорость, напоминающая ручной ввод текста.
# - 0.01: Быстрая печать, практически мгновенная.
# - 0.05: Медленная печать, создаёт эффект вдумчивого текста.

LINE_DELAY = 0.1  # Задержка между строками (в секундах)
# Пример использования:
# - 0.1 (по умолчанию): Плавный переход между строками.
# - 0.05: Быстрый переход между строками, для сокращения времени вывода.
# - 0.2: Медленный переход, акцентирует внимание на новой строке.



def check_paths():
    """Проверяет существование файлов и директорий."""
    paths = {
        "BASE_DIR": BASE_DIR,
        "PROJECT_DIR": PROJECT_DIR,
        "WG_CONFIG_DIR": WG_CONFIG_DIR,
        "QR_CODE_DIR": QR_CODE_DIR,
        "USER_DB_PATH": USER_DB_PATH,
        "IP_DB_PATH": IP_DB_PATH,
        "SERVER_CONFIG_FILE": SERVER_CONFIG_FILE,
        "PARAMS_FILE": PARAMS_FILE,
        "LOG_DIR": LOG_DIR,
        "DIAGNOSTICS_LOG": DIAGNOSTICS_LOG,
        "SUMMARY_REPORT_PATH": SUMMARY_REPORT_PATH,
        "DEBUG_REPORT_PATH": DEBUG_REPORT_PATH,
        "TEST_REPORT_PATH": TEST_REPORT_PATH,
        "MESSAGES_DB_PATH": MESSAGES_DB_PATH,
        "HELP_JSON_PATH": HELP_JSON_PATH,
        "MODULES_DIR": MODULES_DIR,
        "AI_DIAGNOSTICS_DIR": AI_DIAGNOSTICS_DIR,
    }
    status = []
    for name, path in paths.items():
        exists = " ✅  Доступен" if path.exists() else " ❌  Отсутствует"
        status.append(f"{name}: {exists} ({path})")
    return "\n".join(status)


if __name__ == "__main__":
    print(f"\n === 🛠️  Состояние проекта wg_qr_generator  ===\n")
    print(f"  Корневая директория проекта: {BASE_DIR}")
    print(f"  Порт для запуска Gradio: {GRADIO_PORT}")
    print(f"  Порт WireGuard: {WIREGUARD_PORT}\n")
    print(f" === 📂  Проверка файлов и директорий  ===\n")
    print(check_paths())
    print(f"\n")
