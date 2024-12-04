from memory_profiler import memory_usage
import importlib
import inspect

def profile_function(func, *args, **kwargs):
    """Профилирует функцию и возвращает потребление памяти."""
    def wrapper():
        return func(*args, **kwargs)
    
    # Измеряем использование памяти
    mem_usage = memory_usage(wrapper, interval=0.1, timeout=1)
    return max(mem_usage) - min(mem_usage)

def analyze_module(module_name):
    """Анализирует функции указанного модуля."""
    module = importlib.import_module(module_name)
    
    results = []
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        if obj.__module__ == module_name:  # Убеждаемся, что функция из целевого модуля
            try:
                # Профилируем функцию, если она без аргументов
                if not inspect.signature(obj).parameters:
                    mem_diff = profile_function(obj)
                    results.append((name, mem_diff))
                else:
                    results.append((name, "⚠️ Требуются параметры"))
            except Exception as e:
                results.append((name, f"Ошибка: {e}"))

    results.sort(key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0, reverse=True)
    return results

def main():
    module_name = input("Введите имя модуля для анализа: ")
    results = analyze_module(module_name)
    
    print(f"\n{'Function':<30}{'Memory Usage (MB)':<20}")
    print("=" * 50)
    for func, mem in results:
        print(f"{func:<30}{mem:<20}")

if __name__ == "__main__":
    main()
