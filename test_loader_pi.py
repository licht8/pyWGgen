import threading
import time
from modules.animate_status import start_loader, stop_loader

def calculate_pi(iterations):
    """
    Вычисляет значение числа π с использованием ряда Грегори-Лейбница.
    """
    pi = 0
    for i in range(iterations):
        pi += (-1) ** i / (2 * i + 1)
    return pi * 4

def test_loader_with_calculation():
    """Тестирует работу лоадера с реальным вычислением."""
    try:
        print(f" Запуск теста работы лоадера с вычислением числа π.")
        print(f" Подготовка к вычислениям...")

        # Количество итераций для вычисления числа π
        iterations = 10_000_000  # Выбираем разумное количество итераций

        print(f" Будет выполнено {iterations:,} итераций. Запускаем лоадер.")
        # Запуск лоадера в отдельном потоке
        loader_thread = threading.Thread(target=start_loader, args=("Calculating π",))
        loader_thread.start()

        # Запускаем длительное вычисление
        print(" Начинаем вычисление числа π...")
        start_time = time.time()
        pi_value = calculate_pi(iterations)
        end_time = time.time()

        # Останавливаем лоадер
        print(" Завершаем лоадер и выводим результат.")
        stop_loader()
        loader_thread.join()

        # Вывод результата
        print(f"\n Расчёты завершены успешно!")
        print(f" Рассчитанное значение π: {pi_value}")
        print(f" Время выполнения: {end_time - start_time:.2f} секунд")

        print(f"\n Демонстрация работы лоадера завершена.")
        print("-" * 50)
        display_loader_instructions()

    except Exception as e:
        print(f" Во время теста произошла ошибка: {e}")

def display_loader_instructions():
    """Выводит инструкции по использованию лоадера."""
    print(f"\n === Инструкция по использованию лоадера ===")
    print(f" Лоадер - это удобный способ показать процесс выполнения длительных операций в терминале.")
    print(f" Для его использования следуйте этим шагам:\n")
    print(f" 1. Импортируйте функции `start_loader` и `stop_loader` в ваш скрипт:")
    print(f"   ```python")
    print(f"   from modules.animate_status import start_loader, stop_loader")
    print(f"   ```\n")
    print(f" 2. Запустите лоадер перед началом длительной операции:")
    print(f"   ```python")
    print(f"   import threading")
    print(f"   loader_thread = threading.Thread(target=start_loader, args=(\"Your message here\",))")
    print(f"   loader_thread.start()")
    print(f"   ```\n")
    print(f" 3. Выполните вашу длительную операцию:")
    print(f"   ```python")
    print(f"   # Например, длительное вычисление")
    print(f"   result = some_long_computation()")
    print(f"   ```\n")
    print(f" 4. Остановите лоадер после завершения операции:")
    print(f"   ```python")
    print(f"   stop_loader()")
    print(f"   loader_thread.join()")
    print(f"   ```\n")
    print(f" Пример полного кода:")
    print(f"   ```python")
    print(f"   import threading")
    print(f"   from modules.animate_status import start_loader, stop_loader")
    print(f"   def some_long_computation():")
    print(f"       time.sleep(5)  # Имитация длительного процесса")
    print(f"       return \"Completed!\"")
    print(f"   loader_thread = threading.Thread(target=start_loader, args=(\"Working\",))")
    print(f"   loader_thread.start()")
    print(f"   result = some_long_computation()")
    print(f"   stop_loader()")
    print(f"   loader_thread.join()")
    print(f"   print(result)")
    print(f"   ```")
    print(f"===========================================\n")

if __name__ == "__main__":
    test_loader_with_calculation()
