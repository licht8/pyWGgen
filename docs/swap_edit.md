
### Полное описание скрипта `swap_edit.py`

**Назначение:**
Скрипт предназначен для управления и оптимизации файла подкачки (swap) в системах Linux. 
Его главная задача — обеспечить стабильность системы, особенно для серверов и приложений, критичных к использованию памяти. 
Правильная настройка swap помогает избежать сбоев из-за нехватки оперативной памяти.

---

#### Возможности:

1. **Проверка swap:**
   - Скрипт проверяет, существует ли файл подкачки в системе, и оценивает его текущий размер.

2. **Оптимизация swap:**
   - Если swap отсутствует, скрипт предлагает создать его с рекомендованным объемом (до 5% от общей файловой системы).
   - Если swap существует, но его размер меньше указанного в параметре `--memory_required` или меньше минимального рекомендованного, скрипт предлагает его расширить.

3. **Умный пропуск действий:**
   - Если swap уже оптимален, скрипт либо пропускает дальнейшие действия (в случае вызова из другого скрипта), либо уведомляет об этом (при запуске вручную).

4. **Расширенные режимы работы:**
   - Скрипт поддерживает интерактивное управление, а также автоматическую настройку через параметры командной строки.

---

#### Режимы работы:

1. **Интерактивный режим:**
   - Если скрипт запускается без аргументов, он предлагает пользователю выбрать размер swap, предоставляя подсказки и рекомендации.
   - Пример:
     ```bash
     sudo python3 swap_edit.py
     ```

2. **Режим с параметром `--memory_required`:**
   - Позволяет указать объем swap, необходимый для выполнения задачи, требовательной к памяти (до 10% от объема диска, не более 2048 MB).
   - Если текущий swap не удовлетворяет требованиям, скрипт предлагает увеличить его до заданного значения.
   - Пример:
     ```bash
     sudo python3 swap_edit.py --memory_required 1024
     ```

3. **Фиксированные режимы:**
   - `--min_swap` или `--ms`: Устанавливает фиксированный минимальный размер swap (64 MB).
   - `--eco_swap`: Устанавливает swap размером 2% от общего объема диска.
   - `--erase_swap`: Полностью удаляет swap.
   - Примеры:
     ```bash
     sudo python3 swap_edit.py --min_swap
     sudo python3 swap_edit.py --eco_swap
     sudo python3 swap_edit.py --erase_swap
     ```

4. **Вызов из других скриптов:**
   - Вы можете вызвать функцию `swap_edit` из другого скрипта для проверки и оптимизации swap.
   - Пример:
     ```python
     from modules.swap_edit import swap_edit

     # Проверить и установить swap размером 2048 MB
     swap_edit(size_mb=2048, action="memory_required")
     ```
Обновим скрипт, добавив поддержку параметра `--micro_swap`. Этот параметр активирует "тихий режим", в котором создается swap размером 64 MB без дополнительных сообщений.

---

### Обновленный скрипт с поддержкой `--micro_swap`

```python
def swap_edit(size_mb=None, action=None, silent=False):
    """Основная функция настройки swap."""
    check_root()

    if not silent:
        display_message_slowly("📊 Состояние памяти:")
        swap_info = get_swap_info()
        if swap_info:
            print(swap_info)

    total_disk = int(run_command("df --total | tail -1 | awk '{print $2}'")) // 1024
    recommended_swap = min(total_disk // 10, 2048)  # 10% или максимум 2048 MB
    eco_swap = total_disk // 50  # 2% от диска
    min_swap = 64
    micro_swap = 64  # Размер для тихого режима

    current_swap = run_command("free -m | awk '/^Swap:/ {print $2}'")
    current_swap = int(current_swap) if current_swap else 0

    if action == "micro":
        size_mb = micro_swap
        silent = True

    if current_swap >= size_mb:
        if not silent:
            display_message_slowly(
                f"✅ Текущий swap ({current_swap} MB) уже оптимален. Если хотите изменить, используйте --erase_swap."
            )
        return

    create_swap_file(size_mb, reason=action)

    if not silent:
        display_message_slowly("📊 Итоговое состояние памяти:")
        final_swap_info = get_swap_info()
        if final_swap_info:
            print(final_swap_info)


if __name__ == "__main__":
    parser = ArgumentParser(description="Утилита для управления swap-файлом.")
    parser.add_argument("--memory_required", "--mr", type=int, help="Указать минимальный объем swap в MB.")
    parser.add_argument("--min_swap", "--ms", action="store_true", help="Создать минимальный swap (64 MB).")
    parser.add_argument("--eco_swap", action="store_true", help="Создать eco swap (2% от объема диска).")
    parser.add_argument("--micro_swap", action="store_true", help="Создать swap размером 64 MB в тихом режиме.")
    parser.add_argument("--erase_swap", action="store_true", help="Удалить swap.")
    args = parser.parse_args()

    if args.erase_swap:
        swap_edit(action="erase")
    elif args.eco_swap:
        swap_edit(action="eco")
    elif args.min_swap:
        swap_edit(action="min")
    elif args.micro_swap:
        swap_edit(action="micro", silent=True)
    elif args.memory_required:
        swap_edit(size_mb=args.memory_required, action="memory_required")
    else:
        swap_edit()
```

---

### Что делает параметр `--micro_swap`:

- **Назначение:**
  Включает "тихий режим" создания swap размером 64 MB.
  
- **Как работает:**
  - Без вывода дополнительных сообщений.
  - Пропускает проверку текущего состояния памяти.
  - Автоматически создает swap размером 64 MB.

---

### Пример вызова:

1. **Запуск из командной строки:**
   ```bash
   sudo python3 swap_edit.py --micro_swap
   ```
   - Результат: создается swap размером 64 MB без дополнительных сообщений.

2. **Вызов из другого скрипта:**
   ```python
   from modules.swap_edit import swap_edit

   # Создать swap в тихом режиме
   swap_edit(action="micro", silent=True)
   ```

---

### Расширенный хелп:

Добавьте в документацию следующие примеры:

```plaintext
#### Параметр `--micro_swap`

- Описание: Создает swap размером 64 MB в "тихом режиме". Подходит для систем, где требуется минимальный swap для корректной работы приложений.
- Особенности: Без вывода сообщений и проверки текущего состояния памяти.

**Примеры использования:**

1. Запуск из командной строки:
   ```bash
   sudo python3 swap_edit.py --micro_swap
   ```

2. Использование в другом скрипте:
   ```python
   from modules.swap_edit import swap_edit

   # Создать минимальный swap в тихом режиме
   swap_edit(action="micro", silent=True)
   ```

**Результат:**
- Создается swap размером 64 MB, если текущий swap отсутствует или его объем меньше 64 MB.
``` 

Теперь параметр `--micro_swap` позволяет быстро и без лишних сообщений создать минимальный swap размером 64 MB.

---

#### Примеры работы:

1. **Swap отсутствует:**
   - Если swap отсутствует, скрипт выдает:
     ```
     ❌ Swap отсутствует в системе.
     Рекомендуется создать swap размером 512 MB (или введите свой размер).
     ```
   - Пользователь может согласиться с рекомендацией или указать другой размер.

2. **Недостаточный swap:**
   - Если текущий swap меньше минимального рекомендованного:
     ```
     🔍 Текущий swap: 256 MB. Рекомендуемый: 1024 MB.
     Хотите увеличить размер swap до 1024 MB? [Y/n]:
     ```
   - Пользователь может подтвердить или задать собственный размер.

3. **Swap уже оптимален:**
   - Если swap соответствует требованиям:
     - При вызове из другого скрипта:
       ```
       (действия пропускаются, сообщения не выводятся)
       ```
     - При запуске вручную:
       ```
       ✅ Текущий swap (2048 MB) уже оптимален.
       ```

4. **Удаление swap:**
   - При запуске с `--erase_swap`:
     ```
     🔍 Обнаружен существующий swap.
     🗑️ Swap удален успешно.
     ```

---

#### Зачем нужен swap?

1. **Резерв памяти:**
   Swap позволяет компенсировать нехватку оперативной памяти, выделяя место на диске для временного хранения данных.

2. **Стабильность системы:**
   Swap особенно важен для серверов, где нагрузка на память может неожиданно увеличиться.

3. **Гибкость настройки:**
   Swap можно оптимизировать под конкретные задачи, например, базы данных, рендеринг или анализ данных.

---

#### Итог:

Скрипт `swap_edit.py` — это мощный инструмент для настройки swap в Linux. 
Он подходит как для ручного управления, так и для интеграции в другие скрипты, помогая избежать проблем с нехваткой памяти 
и обеспечивая стабильную работу системы.
