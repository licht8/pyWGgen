#!/usr/bin/env python3
import json
import shutil
from pathlib import Path
from settings import USER_DB_PATH, SERVER_CONFIG_FILE
from modules.main_registration_fields import create_user_record
from modules.qr_generator import generate_qr_code

def get_valid_path(prompt):
    """Запрашивает путь у пользователя до тех пор, пока не найдет существующую директорию."""
    while True:
        path_str = input(prompt).strip()
        path = Path(path_str)
        if path.exists() and path.is_dir():
            return path
        print(f"Ошибка: Директория '{path_str}' не существует или недоступна. Повторите ввод.\n")

def find_user_files(username, config_dir, qr_dir):
    """Поиск файлов пользователя (конфиг, QR) в указанных директориях."""
    config_path = next(
        (f for ext in ['.conf', '.txt']
         if (f := config_dir / f"{username}{ext}").exists()), 
        None
    )
    qr_path = next(
        (f for ext in ['.png', '.jpg', '.svg']
         if (f := qr_dir / f"{username}{ext}").exists()), 
        None
    )
    return config_path, qr_path

def sync_users_from_config_paths(config_dir_str: str, qr_dir_str: str):
    """
    Основная логика синхронизации пользователей. 
    Принимает строки путей к директориям с конфигами и QR‑кодами.
    
    Возвращает кортеж (success: bool, logs: str), 
    где logs - текстовый отчет (логи) о проделанной работе.
    """
    logs = []
    try:
        config_dir = Path(config_dir_str)
        qr_dir = Path(qr_dir_str)

        # Проверяем, что директории существуют
        if not config_dir.is_dir():
            raise ValueError(f"Директория конфигов не найдена: {config_dir}")
        if not qr_dir.is_dir():
            raise ValueError(f"Директория QR-кодов не найдена: {qr_dir}")

        logs.append("=== 🛠 Начало синхронизации пользователей ===")
        logs.append(f"Путь к конфигам: {config_dir}")
        logs.append(f"Путь к QR‑кодам: {qr_dir}\n")

        # Парсим SERVER_CONFIG_FILE
        with open(SERVER_CONFIG_FILE, "r") as f:
            config_content = f.read()

        users = []
        current_user = {}

        for line in config_content.split('\n'):
            line = line.strip()
            if line.startswith("### Client"):
                if current_user:
                    users.append(current_user)
                current_user = {"username": line.split("### Client")[1].strip()}
            elif line.startswith("PublicKey ="):
                current_user["public_key"] = line.split("=")[1].strip()
            elif line.startswith("PresharedKey ="):
                current_user["preshared_key"] = line.split("=")[1].strip()
            elif line.startswith("AllowedIPs ="):
                current_user["allowed_ips"] = line.split("=")[1].strip()
            elif line == "" and current_user:
                users.append(current_user)
                current_user = {}

        if current_user:
            users.append(current_user)

        # Загружаем существующую БД пользователей
        user_records = {}
        if Path(USER_DB_PATH).exists():
            with open(USER_DB_PATH, "r") as f:
                user_records = json.load(f)

        new_users = 0
        for user in users:
            username = user["username"]
            logs.append(f"Обработка пользователя: {username}")

            # Ищем файлы
            config_path, qr_path = find_user_files(username, config_dir, qr_dir)
            
            # Целевые пути
            target_config = Path(f"user/data/wg_configs/{username}.conf")
            target_qr = Path(f"user/data/qrcodes/{username}.png")

            # Создаем директории, если их нет
            target_config.parent.mkdir(parents=True, exist_ok=True)
            target_qr.parent.mkdir(parents=True, exist_ok=True)

            # Копируем или создаем конфиг
            if config_path:
                shutil.copy(config_path, target_config)
                logs.append(f"  ✅ Config скопирован: {config_path} → {target_config}")
            else:
                target_config.touch()
                logs.append(f"  ⚠️ Config для {username} не найден! Создан пустой файл.")

            # Копируем или генерируем QR‑код
            if qr_path:
                shutil.copy(qr_path, target_qr)
                logs.append(f"  ✅ QR‑код скопирован: {qr_path} → {target_qr}")
            elif config_path:
                qr_text = target_config.read_text()
                generate_qr_code(qr_text, str(target_qr))
                logs.append(f"  🔄 QR‑код сгенерирован на основе конфига.")
            else:
                logs.append(f"  ⚠️ QR‑код не создан (конфиг отсутствует).")

            # Обновляем user_records
            if username not in user_records:
                from modules.main_registration_fields import create_user_record
                user_record = create_user_record(
                    username=username,
                    address=user.get("allowed_ips", ""),
                    public_key=user.get("public_key", ""),
                    preshared_key=user.get("preshared_key", ""),
                    qr_code_path=str(target_qr)
                )
                # Добавляем пути
                user_record["config_path"] = str(target_config)
                user_record["qr_code_path"] = str(target_qr) if target_qr.exists() else None

                user_records[username] = user_record
                new_users += 1

        # Сохраняем изменения
        with open(USER_DB_PATH, "w") as f:
            json.dump(user_records, f, indent=4)

        logs.append(f"\n🎉 Синхронизация завершена! Новых пользователей добавлено: {new_users}")
        return True, "\n".join(logs)

    except Exception as e:
        error_msg = f"❌ Ошибка синхронизации: {str(e)}"
        logs.append(error_msg)
        return False, "\n".join(logs)


def sync_users_from_config():
    """
    Старая «консольная» функция: запрашивает пути у пользователя 
    и вызывает sync_users_from_config_paths.
    """
    try:
        print("\n=== 🛠 USER SYNCHRONIZATION (консольный режим) ===")
        config_dir = get_valid_path("Client configs directory: ")
        qr_dir = get_valid_path("QR codes directory: ")

        success, log = sync_users_from_config_paths(str(config_dir), str(qr_dir))
        print(log)  # Выводим все логи в консоль

        return success
    except KeyboardInterrupt:
        print("\nСинхронизация прервана пользователем.")
        return False


if __name__ == "__main__":
    # Если запустить скрипт напрямую, сработает интерактивный режим (через консоль).
    sync_users_from_config()
