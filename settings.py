from pathlib import Path

# Определяем базовый путь к корню проекта
BASE_DIR = Path(__file__).resolve().parent.parent  # Путь к корню проекта
PROJECT_DIR = BASE_DIR / "wg_qr_generator"         # Путь к рабочей директории проекта

# Пути к файлам и директориям
WG_CONFIG_DIR = BASE_DIR / "user/data/wg_configs"
QR_CODE_DIR = BASE_DIR / "user/data/qrcodes"
STALE_CONFIG_DIR = BASE_DIR / "user/data/usr_stale_config"
USER_DB_PATH = BASE_DIR / "user/data/user_records.json"
IP_DB_PATH = BASE_DIR / "user/data/ip_records.json"
SERVER_CONFIG_FILE = "/etc/wireguard/wg0.conf"  # Путь к конфигурационному файлу сервера WireGuard
PARAMS_FILE = "/etc/wireguard/params"           # Путь к файлу с параметрами WireGuard

# Параметры WireGuard
DEFAULT_TRIAL_DAYS = 30                          # Базовый срок действия аккаунта в днях

# Настройки для логирования
LOG_FILE_PATH = BASE_DIR / "user/data/logs/app.log"
LOG_LEVEL = "INFO"

# Пути к отчетам и базе сообщений
DEBUG_REPORT_PATH = PROJECT_DIR / "ai_diagnostics/debug_report.txt"  # Путь к отчету диагностики
TEST_REPORT_PATH = PROJECT_DIR / "ai_diagnostics/test_report.txt"    # Путь к отчету тестирования
MESSAGES_DB_PATH = PROJECT_DIR / "ai_diagnostics/messages_db.json"   # Путь к базе сообщений

# Путь к журналу диагностики
DIAGNOSTICS_LOG = BASE_DIR / "user/data/logs/diagnostics.log"

if __name__ == "__main__":
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"PROJECT_DIR: {PROJECT_DIR}")
    print(f"WG_CONFIG_DIR: {WG_CONFIG_DIR}")
    print(f"QR_CODE_DIR: {QR_CODE_DIR}")
    print(f"DEBUG_REPORT_PATH: {DEBUG_REPORT_PATH}")
    print(f"TEST_REPORT_PATH: {TEST_REPORT_PATH}")
    print(f"MESSAGES_DB_PATH: {MESSAGES_DB_PATH}")
    print(f"DIAGNOSTICS_LOG: {DIAGNOSTICS_LOG}")
