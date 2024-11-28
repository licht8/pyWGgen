import os

# Пути к файлам и директориям
BASE_DIR = "user/data"
WG_CONFIG_DIR = os.path.join(BASE_DIR, "wg_configs")
QR_CODE_DIR = os.path.join(BASE_DIR, "qrcodes")
STALE_CONFIG_DIR = os.path.join(BASE_DIR, "usr_stale_config")
USER_DB_PATH = os.path.join(BASE_DIR, "user_records.json")
IP_DB_PATH = os.path.join(BASE_DIR, "ip_records.json")
SERVER_CONFIG_FILE = "/etc/wireguard/wg0.conf"  # Путь к конфигурационному файлу сервера WireGuard
PARAMS_FILE = "/etc/wireguard/params"           # Путь к файлу с параметрами WireGuard

# Параметры WireGuard
DEFAULT_TRIAL_DAYS = 30                          # Базовый срок действия аккаунта в днях

# Настройки для логирования
LOG_FILE_PATH = os.path.join(BASE_DIR, "logs", "app.log")
LOG_LEVEL = "INFO"

# Путь к журналу диагностики
DIAGNOSTICS_LOG = os.path.join(BASE_DIR, "logs", "diagnostics.log")  # Унифицированный лог диагностики
DEBUG_REPORT_PATH = os.path.join(BASE_DIR, "logs", "debug_report.txt")  # Альтернативный лог диагностики
