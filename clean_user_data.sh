#!/bin/bash
# clean_user_data.sh
# Скрипт для выборочной очистки базы пользователей и обновления WireGuard

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
clear_user_records() {
    echo -n "🧹 Очистить файл user_records.json? (y/n): "
    read -r choice
    if [[ "$choice" == "y" ]]; then
        echo "{}" > "$USER_RECORDS_JSON"
        echo "✅ user_records.json очищен."
    else
        echo "⏭️ Очистка user_records.json пропущена."
    fi
}

clear_wg_users() {
    echo -n "🧹 Очистить файл wg_users.json? (y/n): "
    read -r choice
    if [[ "$choice" == "y" ]]; then
        echo "{}" > "$WG_USERS_JSON"
        echo "✅ wg_users.json очищен."
    else
        echo "⏭️ Очистка wg_users.json пропущена."
    fi
}

# Очистка конфигурации WireGuard
clear_wireguard_conf() {
    echo -n "🧹 Очистить файл конфигурации WireGuard (удалить все [Peer])? (y/n): "
    read -r choice
    if [[ "$choice" == "y" ]]; then
        check_file_exists "$WG_CONF"
        
        # Резервное копирование оригинального файла
        cp "$WG_CONF" "${WG_CONF}.bak"
        echo "✅ Резервная копия создана: ${WG_CONF}.bak"

        # Оставляем только заголовок интерфейса
        sed -i '/^\[Peer\]/,$d' "$WG_CONF"
        echo "✅ Конфигурация WireGuard очищена."
    else
        echo "⏭️ Очистка конфигурации WireGuard пропущена."
    fi
}

# Перезапуск службы WireGuard
restart_wireguard() {
    echo -n "🔄 Перезапустить WireGuard? (y/n): "
    read -r choice
    if [[ "$choice" == "y" ]]; then
        systemctl restart wg-quick@wg0
        if [[ $? -eq 0 ]]; then
            echo "✅ WireGuard успешно перезапущен."
        else
            echo "❌ Ошибка при перезапуске WireGuard!"
            exit 1
        fi
    else
        echo "⏭️ Перезапуск WireGuard пропущен."
    fi
}

# Основной процесс
main() {
    echo "🚀 Запуск выборочной очистки данных пользователей и обновления WireGuard..."

    # Проверяем существование файлов
    check_file_exists "$USER_RECORDS_JSON"
    check_file_exists "$WG_USERS_JSON"
    check_file_exists "$WG_CONF"

    # Выполняем очистку
    clear_user_records
    clear_wg_users
    clear_wireguard_conf
    restart_wireguard

    echo "🎉 Очистка завершена. Все данные обработаны."
}

# Запуск основного процесса
main
