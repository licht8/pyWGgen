#!/usr/bin/env python3
import json
import shutil
from pathlib import Path
from settings import USER_DB_PATH, SERVER_CONFIG_FILE
from modules.main_registration_fields import create_user_record
from modules.qr_generator import generate_qr_code

def get_valid_path(prompt):
    """Запрашивает путь у пользователя до получения валидной директории"""
    while True:
        path = Path(input(prompt).strip())
        if path.exists() and path.is_dir():
            return path
        print(f"Ошибка: Директория '{path}' не существует или недоступна. Попробуйте снова.\n")

def find_user_files(username, config_dir, qr_dir):
    """Ищет файлы пользователя в указанных директориях"""
    # Поиск конфига
    config_path = next(
        (f for ext in ['.conf', '.txt'] 
         if (f := config_dir / f"{username}{ext}").exists()), None
    )
    
    # Поиск QR-кода
    qr_path = next(
        (f for ext in ['.png', '.jpg', '.svg'] 
         if (f := qr_dir / f"{username}{ext}").exists()), None
    )
    
    return config_path, qr_path

def sync_users_interactive():
    """Основная функция синхронизации с интерактивным вводом"""
    try:
        # Шаг 1: Запрос путей у пользователя
        print("\n=== 🛠 СИНХРОНИЗАЦИЯ ПОЛЬЗОВАТЕЛЕЙ ===")
        print("Укажите пути к существующим файлам:")
        
        config_dir = get_valid_path("Директория с конфигами клиентов: ")
        qr_dir = get_valid_path("Директория с QR-кодами клиентов: ")

        # Шаг 2: Парсинг серверного конфига
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

        # Шаг 3: Обработка пользователей
        user_records = {}
        if Path(USER_DB_PATH).exists():
            with open(USER_DB_PATH, "r") as f:
                user_records = json.load(f)

        new_users = 0
        for user in users:
            username = user["username"]
            print(f"\n🔍 Обработка пользователя: {username}")
            
            # Поиск файлов
            config_path, qr_path = find_user_files(username, config_dir, qr_dir)
            
            # Пути в проекте
            target_config = Path(f"user/data/wg_configs/{username}.conf")
            target_qr = Path(f"user/data/qrcodes/{username}.png")
            
            # Создаем директории если отсутствуют
            target_config.parent.mkdir(parents=True, exist_ok=True)
            target_qr.parent.mkdir(parents=True, exist_ok=True)

            # Копирование конфига
            if config_path:
                shutil.copy(config_path, target_config)
                print(f"✅ Конфиг скопирован: {config_path} → {target_config}")
            else:
                print(f"⚠️ Конфиг для {username} не найден! Создан пустой файл.")
                target_config.touch()
                
            # Генерация/копирование QR-кода
            if qr_path:
                shutil.copy(qr_path, target_qr)
                print(f"✅ QR-код скопирован: {qr_path} → {target_qr}")
            elif config_path:
                generate_qr_code(target_config.read_text(), str(target_qr))
                print(f"🔄 QR-код сгенерирован из конфига")
            else:
                print(f"⚠️ QR-код для {username} не создан (отсутствует конфиг)")

            # Обновление записей
            if username not in user_records:
                user_records[username] = create_user_record(
                    username=username,
                    address=user["allowed_ips"],
                    public_key=user["public_key"],
                    preshared_key=user["preshared_key"],
                    config_path=str(target_config),
                    qr_code_path=str(target_qr) if target_qr.exists() else None
                )
                new_users += 1

        # Сохранение данных
        with open(USER_DB_PATH, "w") as f:
            json.dump(user_records, f, indent=4)

        print(f"\n🎉 Синхронизация завершена! Добавлено новых пользователей: {new_users}")
        return True

    except Exception as e:
        print(f"\n❌ Критическая ошибка: {str(e)}")
        return False

if __name__ == "__main__":
    sync_users_interactive()