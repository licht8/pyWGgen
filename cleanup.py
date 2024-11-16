import os
import shutil
from datetime import datetime
from dateutil import parser # type: ignore
from modules.user_management import load_user_records, delete_user_record
from modules.config_writer import remove_user_from_server_config
from modules.ip_management import release_ip
import settings

def check_and_cleanup():
    os.makedirs(settings.STALE_CONFIG_DIR, exist_ok=True)
    user_data = load_user_records()
    now = datetime.now()

    for nickname, record in user_data.items():
        expires_at = parser.parse(record['expires_at'])
        if now >= expires_at:
            print(f"Удаление просроченного пользователя: {nickname}")

            # Удаляем конфигурацию пользователя с сервера
            remove_user_from_server_config(settings.SERVER_CONFIG_FILE, nickname)

            # Перемещаем конфигурационный файл пользователя в архив
            user_config_path = os.path.join(settings.WG_CONFIG_DIR, f"{nickname}.conf")
            if os.path.exists(user_config_path):
                shutil.move(user_config_path, os.path.join(settings.STALE_CONFIG_DIR, f"{nickname}.conf"))
                print(f"Конфигурация {nickname} перемещена в архив.")

            # Освобождаем IP-адрес, если он есть
            user_ip = record.get("address")
            if user_ip:
                print(f"Найден IP-адрес {user_ip} для пользователя {nickname}")
                
                # Проверяем наличие маски, прежде чем разделить IP
                if '/' in user_ip:
                    ip_address = user_ip.split('/')[0]
                else:
                    ip_address = user_ip
                
                print(f"Попытка освобождения IP-адреса для {nickname}: {ip_address}")
                release_ip(ip_address)  # Передаем IP без маски
            else:
                print(f"IP-адрес для пользователя {nickname} не найден в записи")

            # Удаляем QR-код пользователя
            qr_path = os.path.join(settings.QR_CODE_DIR, f"{nickname}.png")
            if os.path.exists(qr_path):
                os.remove(qr_path)
                print(f"QR-код для {nickname} удален.")

            # Удаляем запись пользователя из базы данных
            delete_user_record(nickname)
            print(f"Пользователь {nickname} успешно удален и его данные очищены.")

if __name__ == "__main__":
    check_and_cleanup()
