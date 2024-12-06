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
        print("Запуск теста работы лоадера с вычислением числа π.")
        print("Подготовка к вычислениям...")

        # Количество итераций для вычисления числа π
        iterations = 10_000_000  # Выбираем разумное количество итераций

        print(f"Будет выполнено {iterations:,} итераций. Запускаем лоадер.")
        # Запуск лоадера в отдельном потоке
        loader_thread = threading.Thread(target=start_loader, args=("Calculating π",))
        loader_thread.start()

        # Запускаем длительное вычисление
        print("Начинаем вычисление числа π...")
        start_time = time.time()
        pi_value = calculate_pi(iterations)
        end_time = time.time()

        # Останавливаем лоадер
        print("Завершаем лоадер и выводим результат.")
        stop_loader()
        loader_thread.join()

        # Вывод результата
        print("\nРасчёты завершены успешно!")
        print(f"Рассчитанное значение π: {pi_value}")
        print(f"Время выполнения: {end_time - start_time:.2f} секунд")

        print("\nДемонстрация работы лоадера завершена.")
        print("-" * 50)
        display_loader_instructions()

    except Exception as e:
        print(f"Во время теста произошла ошибка: {e}")

def display_loader_instructions():
    """Выводит инструкции по использованию лоадера."""
    print("\n=== Инструкция по использованию лоадера ===")
    print("Лоадер - это удобный способ показать процесс выполнения длительных операций в терминале.")
    print("Для его использования следуйте этим шагам:\n")
    print("1. Импортируйте функции `start_loader` и `stop_loader` в ваш скрипт:")
    print("   ```python")
    print("   from modules.animate_status import start_loader, stop_loader")
    print("   ```\n")
    print("2. Запустите лоадер перед началом длительной операции:")
    print("   ```python")
    print("   import threading")
    print("   loader_thread = threading.Thread(target=start_loader, args=(\"Your message here\",))")
    print("   loader_thread.start()")
    print("   ```\n")
    print("3. Выполните вашу длительную операцию:")
    print("   ```python")
    print("   # Например, длительное вычисление")
    print("   result = some_long_computation()")
    print("   ```\n")
    print("4. Остановите лоадер после завершения операции:")
    print("   ```python")
    print("   stop_loader()")
    print("   loader_thread.join()")
    print("   ```\n")
    print("Пример полного кода:")
    print("   ```python")
    print("   import threading")
    print("   from modules.animate_status import start_loader, stop_loader")
    print("   def some_long_computation():")
    print("       time.sleep(5)  # Имитация длительного процесса")
    print("       return \"Completed!\"")
    print("   loader_thread = threading.Thread(target=start_loader, args=(\"Working\",))")
    print("   loader_thread.start()")
    print("   result = some_long_computation()")
    print("   stop_loader()")
    print("   loader_thread.join()")
    print("   print(result)")
    print("   ```")
    print("===========================================")

if __name__ == "__main__":
    test_loader_with_calculation()
