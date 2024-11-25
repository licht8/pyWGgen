#!/bin/bash
# clean_user_data.sh
# Скрипт для очистки базы пользователей и обновления WireGuard

# Пути к файлам
BASE_DIR="/root/pyWGgen/wg_qr_generator"
USER_RECORDS_JSON="$BASE_DIR/user/data/user_records.json"
WG_USERS_JSON="$BASE_DIR/logs/wg_users.json"
WG_CONF="/etc/wireguard/wg0.conf"

# Функция для проверки существования файла
check_file_exists() {
    if [[ ! -f "$1" ]]; then
        echo "❌ Файл $1 не найден!"
        exit 1
    fi
}

# Очистка базы данных
clear_user_data() {
    echo "🧹 Очистка базы пользователей..."
    echo "{}" > "$USER_RECORDS_JSON"
    echo "{}" > "$WG_USERS_JSON"
    echo "✅ База пользователей очищена."
}

# Очистка конфигурации WireGuard
clear_wireguard_conf() {
    echo "🧹 Очистка конфигурации WireGuard..."
    check_file_exists "$WG_CONF"
    
    # Резервное копирование оригинального файла
    cp "$WG_CONF" "${WG_CONF}.bak"
    echo "✅ Резервная копия создана: ${WG_CONF}.bak"

    # Оставляем только заголовок интерфейса
    sed -i '/^\[Peer\]/,$d' "$WG_CONF"
    echo "✅ Конфигурация WireGuard очищена."
}

# Перезапуск службы WireGuard
restart_wireguard() {
    echo "🔄 Перезапуск службы WireGuard..."
    systemctl restart wg-quick@wg0
    if [[ $? -eq 0 ]]; then
        echo "✅ WireGuard успешно перезапущен."
    else
        echo "❌ Ошибка при перезапуске WireGuard!"
        exit 1
    fi
}

# Основной процесс
main() {
    echo "🚀 Запуск очистки данных пользователей и обновления WireGuard..."

    # Проверяем существование файлов
    check_file_exists "$USER_RECORDS_JSON"
    check_file_exists "$WG_USERS_JSON"
    check_file_exists "$WG_CONF"

    # Выполняем очистку
    clear_user_data
    clear_wireguard_conf
    restart_wireguard

    echo "🎉 Очистка завершена. Все данные сброшены."
}

# Запуск основного процесса
main
