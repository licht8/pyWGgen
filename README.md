
# wg_qr_generator

> **⚠️ Внимание!**
> 
> Этот проект находится в разработке и еще не готов к использованию.
> Пожалуйста, следите за обновлениями!



**wg_qr_generator** – это система автоматизации управления WireGuard, включающая генерацию конфигураций, создание QR-кодов, управление пользователями и очистку устаревших данных.

Система предоставляет как веб-интерфейс на базе **Gradio**, так и консольное меню для управления пользователями и конфигурациями.

---

## Оглавление

1. [Основные возможности](#основные-возможности)
2. [Веб-интерфейс Gradio](#веб-интерфейс-gradio)
   - [Как запустить админку](#как-запустить-админку)
3. [Требования](#требования)
4. [Установка и запуск проекта](#установка-и-запуск-проекта)
   - [Быстрая установка](#быстрая-установка)
5. [Использование меню](#использование-меню)
6. [Структура проекта](#структура-проекта)
7. [Тестирование](#тестирование)
8. [Обновление](#обновление)
9. [Лицензия](#лицензия)
10. [Контакты](#контакты)

---

## Основные возможности

- **Генерация конфигураций**: Автоматическое создание конфигурационных файлов и QR-кодов для пользователей.
- **Управление сроком действия**: Проверка, продление, сброс срока действия аккаунтов.
- **Удаление устаревших данных**: Автоматическое удаление просроченных аккаунтов, IP-адресов и QR-кодов.
- **Синхронизация конфигураций**: Интеграция с сервером WireGuard.
- **Проверка перед созданием**: Проверяет существование пользователя перед созданием нового.
- **Веб-интерфейс**: Простая и удобная админка на базе Gradio для управления пользователями.
- **Подробные отчеты**: Генерация детальных отчетов о состоянии проекта.
- **Обновление проекта**: Удобный механизм обновления кода и зависимостей.

---

## Веб-интерфейс Gradio

**Gradio Admin Panel** предоставляет интерфейс для:
- Просмотра списка пользователей.
- Создания нового пользователя.
- Удаления пользователей.
- Просмотра состояния системы и текущих конфигураций.

### Как запустить админку

Из консольного меню выберите пункт:
```plaintext
3. 🌐 Открыть Gradio админку
```

Админка запускается на порту **7860**. Локальный адрес:
```
http://127.0.0.1:7860
```

Если сервер имеет внешний IP, админка будет доступна в интернете после открытия порта **7860** через `firewalld`. Также автоматически создается временная публичная ссылка через Gradio:

```
🌐 Публичная ссылка: https://<уникальный_адрес>.gradio.live
```

---

## Требования

1. **Python 3.8+** (рекомендуется Python 3.11).
2. **Git** для клонирования репозитория.
3. **Node.js** для работы Gradio.
4. **lsof** для проверки портов.
5. **firewalld** для управления сетевыми правилами.

---

## Установка и запуск проекта

Подготовка к установке проекта:

```bash
sudo dnf update -y && sudo dnf install epel-release -y && \
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash - && \
sudo dnf install -y nodejs && node --version && \
sudo dnf update -y && \
sudo dnf install git mc htop tar gcc curl openssl-devel bzip2-devel libffi-devel zlib-devel -y && \
sudo dnf install net-tools lsof nano -y && \
sudo dnf install python3.11 -y && \
sudo alternatives --set python3 /usr/bin/python3.11 && python3 --version
```

### Описание команды:
1. **Обновление системы**: `sudo dnf update -y`.
2. **Установка EPEL-репозитория**: Для получения дополнительных пакетов.
3. **Установка Node.js**: Через официальный источник NodeSource.
4. **Обновление системных пакетов и установка зависимостей**:
   - Инструменты разработки (`gcc`, `curl`, `openssl-devel`, `bzip2-devel`, `libffi-devel`, `zlib-devel`).
   - Утилиты (`net-tools`, `lsof`, `mc`).
5. **Установка Python 3.11**: С последующей настройкой как основной версии Python.

### Быстрая установка

Для установки и запуска выполните:
```bash
mkdir -p pyWGgen && cd pyWGgen
wget https://raw.githubusercontent.com/licht8/wg_qr_generator/refs/heads/main/run_project.sh
chmod +x run_project.sh
./run_project.sh
```

Эта команда:
1. Создает директорию `pyWGgen` и переходит в нее.
2. Загружает скрипт `run_project.sh`.
3. Настраивает виртуальное окружение, устанавливает зависимости.
4. Запускает консольное меню.

---

## Использование меню

Консольное меню предоставляет следующие возможности:

```plaintext
==================  Меню  ==================

 1. 🛠️   Информация о состоянии проекта
 2. 🧪   Запустить тесты
 u. 🔄   Запустить обновление проекта и зависимостей
--------------------------------------------
 3. 🌐   Открыть Gradio админку
 4. 👤   Управление пользователями
--------------------------------------------
 5. ♻️   Переустановить WireGuard
 6. 🗑️   Удалить WireGuard
--------------------------------------------
 7. 🧹   Очистить базу пользователей
 8. 📋   Запустить генерацию отчета
 9. 🗂️   Показать краткий отчет
10. 📄   Показать полный отчет

	 0 или q. Выход
 ==========================================
```

---

## Структура проекта

```plaintext
wg_qr_generator
├── menu.py                      # Главное меню проекта. Управляет взаимодействием пользователя с функциями проекта через консоль.
├── run_project.sh               # Скрипт запуска и установки проекта. Проверяет зависимости, создает виртуальное окружение, настраивает проект.
├── requirements.txt             # Список Python-зависимостей, необходимых для работы проекта.
├── gradio_admin                 # Папка для веб-интерфейса Gradio.
│   ├── main_interface.py        # Главный скрипт интерфейса Gradio. Запускает вкладки и управляет настройками.
│   ├── tabs                     # Подпапка с вкладками веб-интерфейса.
│   │   ├── create_user_tab.py   # Вкладка создания пользователя через Gradio.
│   │   ├── delete_user_tab.py   # Вкладка удаления пользователей.
│   │   ├── statistics_tab.py    # Вкладка статистики и состояния системы.
│   └── functions                # Вспомогательные функции для интерфейса.
│       ├── format_helpers.py    # Форматирование текста и данных для отображения в Gradio.
│       ├── table_helpers.py     # Управление таблицами, отображаемыми в Gradio.
│       ├── user_records.py      # Функции для работы с файлами пользователей.
├── modules                      # Основные модули проекта.
│   ├── wireguard_utils.py       # Функции для работы с WireGuard: управление конфигурацией, проверка статуса.
│   ├── firewall_utils.py        # Управление портами через firewalld.
│   ├── gradio_utils.py          # Функции для работы с интерфейсом Gradio.
│   ├── report_utils.py          # Генерация и отображение отчетов о состоянии проекта.
│   ├── update_utils.py          # Функции для обновления проекта и зависимостей.
│   ├── user_management.py       # Управление пользователями: создание, удаление, проверка.
│   ├── directory_setup.py       # Создание и настройка необходимых директорий.
│   ├── qr_generator.py          # Генерация QR-кодов для конфигураций WireGuard.
│   ├── config_writer.py         # Запись конфигурационных файлов.
│   └── ip_management.py         # Управление IP-адресами пользователей.
└── test                         # Папка с тестами для модулей проекта.
    ├── test_wireguard_utils.py  # Тесты для wireguard_utils.py.
    ├── test_firewall_utils.py   # Тесты для firewall_utils.py.
    ├── test_gradio_utils.py     # Тесты для gradio_utils.py.
    ├── test_report_utils.py     # Тесты для report_utils.py.
    ├── test_update_utils.py     # Тесты для update_utils.py.
    ├── test_user_management.py  # Тесты для user_management.py.
    ├── test_directory_setup.py  # Тесты для directory_setup.py.
    ├── test_qr_generator.py     # Тесты для qr_generator.py.
    ├── test_config_writer.py    # Тесты для config_writer.py.
    └── test_ip_management.py    # Тесты для ip_management.py.
```

### Разделы структуры

#### 1. **Корневые файлы**
- **`menu.py`**: Основное меню для управления проектом через консоль. Вызывает функции из модулей и предоставляет доступ к основным возможностям проекта.
- **`run_project.sh`**: Автоматизирует процесс установки и запуска проекта. Создает виртуальное окружение, устанавливает зависимости, запускает меню.
- **`requirements.txt`**: Содержит все Python-библиотеки, необходимые для работы проекта.

#### 2. **`gradio_admin`**
- Хранилище веб-интерфейса проекта на базе Gradio.
- **`main_interface.py`**: Координирует запуск вкладок и настройки.
- **`tabs`**: Содержит файлы для каждого отдельного компонента интерфейса (создание пользователей, удаление, статистика).
- **`functions`**: Утилитарные функции для обработки данных в интерфейсе.

#### 3. **`modules`**
- Вспомогательные модули с ключевой бизнес-логикой проекта.
- **`wireguard_utils.py`**: Управление WireGuard (проверка статуса, конфигурации).
- **`firewall_utils.py`**: Работа с firewalld (открытие и закрытие портов).
- **`gradio_utils.py`**: Настройки и запуск Gradio.
- **`report_utils.py`**: Генерация текстовых отчетов.
- **`update_utils.py`**: Функции для обновления проекта.
- **`user_management.py`**: Создание, удаление и управление пользователями.
- **`directory_setup.py`**: Убедитесь, что все необходимые папки существуют.
- **`qr_generator.py`**: Создание QR-кодов для конфигураций.
- **`config_writer.py`**: Запись и управление конфигурационными файлами.
- **`ip_management.py`**: Назначение и управление IP-адресами пользователей.

#### 4. **`test`**
- Тесты для всех модулей проекта.
- Каждый файл тестирует соответствующий модуль, что обеспечивает надежность и предотвращение ошибок в коде.

---

## Тестирование

Запуск тестов:
```bash
pytest
```

---

## Обновление

Для обновления проекта выберите пункт `u` в меню или выполните команду:
```bash
git pull
pip install -r requirements.txt
```

---

## Лицензия

Проект распространяется под лицензией [MIT](LICENSE).

---

## Контакты

Свяжитесь через [Issues](https://github.com/licht8/wg_qr_generator/issues).

---

