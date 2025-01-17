import threading
import time
from modules.animate_status import start_loader, stop_loader

def test_loader():
    """Тестирует работу функций start_loader и stop_loader."""
    try:
        # Создаем поток для запуска лоадера
        loader_thread = threading.Thread(target=start_loader, args=("Testing Loader",))
        loader_thread.start()

        # Симулируем длительный процесс
        print("\nSimulating a long process...")
        time.sleep(5)  # Задержка на 5 секунд

        # Останавливаем лоадер
        stop_loader()
        loader_thread.join()  # Дожидаемся завершения потока
        print("Loader stopped successfully!")
    except Exception as e:
        print(f"An error occurred during the test: {e}")

if __name__ == "__main__":
    test_loader()
