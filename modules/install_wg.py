import os
import subprocess
import shutil
from pathlib import Path
from settings import DEFAULT_SUBNET, USER_SET_SUBNET, WIREGUARD_PORT, SERVER_CONFIG_FILE

def log_message(message: str, level: str = "INFO"):
    """Логирует сообщение."""
    print(f"{level}: {message}")

def is_root():
    """Проверяет запуск от имени root."""
    if os.geteuid() != 0:
        raise PermissionError("Скрипт должен быть запущен от имени root.")

def check_os():
    """Проверяет, что ОС является CentOS 8 или CentOS Stream 8."""
    with open("/etc/os-release") as f:
        os_info = f.read()
    if not (("CentOS" in os_info and "8" in os_info) or "CentOS Stream 8" in os_info):
        raise EnvironmentError("Требуется CentOS Linux 8 или CentOS Stream 8.")


def update_settings_file(key, value):
    """Обновляет параметр в settings.py."""
    settings_path = Path("settings.py")
    if not settings_path.exists():
        raise FileNotFoundError("Файл settings.py не найден.")
    
    lines = settings_path.read_text().splitlines()
    updated_lines = []
    for line in lines:
        if line.startswith(f"{key} ="):
            updated_lines.append(f"{key} = {repr(value)}")
        else:
            updated_lines.append(line)
    settings_path.write_text("\n".join(updated_lines) + "\n")

def prompt_parameters():
    """Запрашивает параметры WireGuard у пользователя."""
    subnet = input(f"Введите подсеть WireGuard [{DEFAULT_SUBNET}]: ") or DEFAULT_SUBNET
    port = input(f"Введите порт WireGuard [{WIREGUARD_PORT}]: ") or WIREGUARD_PORT

    update_settings_file("USER_SET_SUBNET", subnet)
    update_settings_file("WIREGUARD_PORT", int(port))

    return subnet, int(port)

def generate_keypair():
    """Генерирует приватный и публичный ключи."""
    wg_path = shutil.which("wg")
    if not wg_path:
        raise RuntimeError("WireGuard не установлен. Установите его перед началом.")
    private_key = subprocess.check_output([wg_path, "genkey"]).decode().strip()
    public_key = subprocess.check_output([wg_path, "pubkey"], input=private_key.encode()).decode().strip()
    return private_key, public_key

def generate_wg_config(subnet, port):
    """Генерирует конфигурацию WireGuard."""
    base_subnet = subnet.split("/")[0]  # Извлечение базового адреса
    server_private_key, server_public_key = generate_keypair()

    server_config = f"""


def configure_firewalld(port, subnet):
    """Настраивает firewalld."""
    base_subnet = subnet.split("/")[0]  # Корректно извлекаем базовый адрес подсети
    subprocess.run(["firewall-cmd", "--add-port", f"{port}/udp", "--permanent"], check=True)
    subprocess.run(["firewall-cmd", "--add-rich-rule", f"rule family=ipv4 source address={base_subnet}/24 masquerade", "--permanent"], check=True)
    subprocess.run(["firewall-cmd", "--add-rich-rule", "rule family=ipv6 source address=fd42:42:42::0/64 masquerade", "--permanent"], check=True)
    subprocess.run(["firewall-cmd", "--reload"], check=True)


def enable_and_start_service(port):
    """Активирует и запускает WireGuard."""
    service_name = f"wg-quick@wg0"
    subprocess.run(["systemctl", "enable", service_name], check=True)
    subprocess.run(["systemctl", "start", service_name], check=True)
    log_message(f"WireGuard успешно запущен на порту {port}.")

def install_wireguard():
    """Устанавливает WireGuard с настройками."""
    try:
        is_root()
        check_os()

        subnet, port = prompt_parameters()

        log_message("Установка WireGuard...")
        subprocess.run(["dnf", "install", "-y", "epel-release", "elrepo-release"], check=True)
        subprocess.run(["dnf", "install", "-y", "wireguard-tools", "kmod-wireguard"], check=True)
        log_message("WireGuard установлен.")

        generate_wg_config(subnet, port)
        configure_firewalld(port, subnet)
        enable_and_start_service(port)

        log_message("✅ Установка WireGuard завершена.")
    except Exception as e:
        log_message(f"Ошибка: {e}", level="ERROR")

if __name__ == "__main__":
    install_wireguard()
