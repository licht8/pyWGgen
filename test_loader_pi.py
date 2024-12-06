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
        # Количество итераций для вычисления числа π
        iterations = 10_000_000  # Выбираем разумное количество итераций

        # Запуск лоадера в отдельном потоке
        loader_thread = threading.Thread(target=start_loader, args=("Calculating π",))
        loader_thread.start()

        # Запускаем длительное вычисление
        print("\nStarting π calculation...")
        start_time = time.time()
        pi_value = calculate_pi(iterations)
        end_time = time.time()

        # Останавливаем лоадер
        stop_loader()
        loader_thread.join()

        # Вывод результата
        print(f"Calculation completed successfully!")
        print(f"Calculated π value: {pi_value}")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
    except Exception as e:
        print(f"An error occurred during the test: {e}")

if __name__ == "__main__":
    test_loader_with_calculation()
