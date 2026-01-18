#!/usr/bin/env python3
"""
swap_edit.py - Narzędzie do zarządzania plikiem swap w Linuksie

Funkcje:
- Sprawdzenie i optymalizacja swap.
- Obsługa parametrów dla elastycznej konfiguracji:
  * `--memory_required` lub `--mr`: Tworzy swap do 10% miejsca na dysku.
  * `--min_swap` lub `--ms`: Tworzy minimalny swap (64 MB).
  * `--eco_swap`: Tworzy plik swap 2% miejsca na dysku.
  * `--erase_swap`: Kompletnie usuwa swap.
"""

import os
import sys
import time
import shutil
import subprocess
import logging
from pathlib import Path
from argparse import ArgumentParser
from prettytable import PrettyTable

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
sys.path.append(str(PROJECT_DIR))

from settings import PRINT_SPEED, LOG_LEVEL, LOG_FILE_PATH

# Konfiguracja logowania
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=getattr(logging, LOG_LEVEL.upper(), logging.DEBUG),
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def display_message_slowly(message, print_speed=None, end="\n", indent=True):
    """
    Wyświetla wiadomość znak po znaku z opcjonalnym wcięciem i niestandardową prędkością.

    :param message: Wiadomość do wyświetlenia.
    :param print_speed: Prędkość wyświetlania znaków (w sekundach). Jeśli None, używany PRINT_SPEED.
    :param end: Końcowy znak linii (domyślnie: "\n").
    :param indent: Jeśli True, dodaje wcięcie 3-spacji przed każdą linią.
    """
    # Pobierz PRINT_SPEED z ustawień lub użyj domyślnej wartości
    try:
        effective_speed = print_speed if print_speed is not None else PRINT_SPEED
    except NameError:
        effective_speed = print_speed if print_speed is not None else 0.001  # domyślna wartość zapasowa

    # LINE_DELAY - zdefiniuj lokalnie jeśli brak w ustawieniach
    try:
        from settings import LINE_DELAY
        line_delay = LINE_DELAY
    except (ImportError, NameError):
        line_delay = 0.05  # domyślna wartość zapasowa

    for line in message.split("\n"):
        if indent:
            print("   ", end="")  # Dodaj wcięcie jeśli indent=True
        for char in line:
            print(char, end="", flush=True)
            time.sleep(effective_speed)
        print(end, end="", flush=True)
        time.sleep(line_delay)


def run_command(command, check=True):
    """Wykonuje polecenie w terminalu i zwraca wynik."""
    try:
        result = subprocess.run(
            command, shell=True, text=True, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Błąd: {e.stderr.strip()}")
        return None


def check_root():
    """Sprawdza czy skrypt jest uruchamiany jako root."""
    if os.geteuid() != 0:
        display_message_slowly("🚨 Ten skrypt musi być uruchomiony jako root.", indent=False)
        exit(1)


def display_table(data, headers):
    """Wyświetla tabelę z danymi."""
    table = PrettyTable(headers)
    for row in data:
        table.add_row(row)
    return table


def get_swap_info():
    """Pobiera informacje o swap i pamięci."""
    output = run_command("free -h")
    if not output:
        return None

    headers = ["Typ", "Razem", "Używane", "Wolne"]
    rows = []
    for line in output.split("\n"):
        parts = line.split()
        if len(parts) >= 4 and parts[0] in ("Mem:", "Swap:"):
            rows.append(parts[:4])

    return display_table(rows, headers)


def disable_existing_swap(swap_file="/swap"):
    """Wyłącza i usuwa istniejący plik swap jeśli jest używany."""
    if os.path.exists(swap_file):
        display_message_slowly(f"\n   🔍 Wykryto istniejący plik swap: {swap_file}")
        run_command(f"swapoff {swap_file}", check=False)
        try:
            os.remove(swap_file)
            display_message_slowly(f"   🗑️  Usunięto istniejący plik swap: {swap_file}")
        except Exception as e:
            display_message_slowly(f"   ❌  Nie udało się usunąć pliku: {e}")


def create_swap_file(size_mb, reason=None):
    """Tworzy i aktywuje plik swap."""
    try:
        swap_file = "/swap"
        disable_existing_swap(swap_file)

        display_message_slowly(f"   🛠️  Tworzenie pliku swap o rozmiarze {size_mb} MB...")
        run_command(f"dd if=/dev/zero of={swap_file} bs=1M count={size_mb}", check=True)

        display_message_slowly("   🎨 Formatowanie pliku swap...")
        run_command(f"mkswap {swap_file}", check=True)

        display_message_slowly("   ⚡ Aktywacja pliku swap...")
        run_command(f"swapon {swap_file}", check=True)

        display_message_slowly(f"\n   ✅ Swap utworzony. Rozmiar: {size_mb} MB")
        if reason:
            display_message_slowly(f"   🔍 Powód: {reason}")

    except Exception as e:
        display_message_slowly(f"   ❌ Wystąpił błąd: {e}")


def check_swap_edit(size_mb, action=None, silent=True, tolerance=2):
    """
    Sprawdza stan swap i wywołuje swap_edit jeśli potrzeba.

    :param size_mb: Wymagany rozmiar swap (w MB).
    :param action: Akcja do wykonania (np. "micro", "min").
    :param silent: Jeśli True, działa w trybie cichym.
    :param tolerance: Dopuszczalna różnica między aktualnym a wymaganym swap (w MB).
    """
    try:
        # Sprawdź aktualny swap
        current_swap = run_command("free -m | awk '/^Swap:/ {print $2}'")
        current_swap = int(current_swap) if current_swap and current_swap.isdigit() else 0

        # Loguj aktualny swap
        logger.debug(f"Aktualny swap: {current_swap} MB")
        logger.debug(f"Wymagany swap: {size_mb} MB")

        # Sprawdź warunek z tolerancją
        if current_swap >= size_mb - tolerance:
            if not silent:
                display_message_slowly(f"✅ Aktualny swap ({current_swap} MB) jest wystarczający. Brak zmian.")
            logger.info(f"Swap ({current_swap} MB) jest wystarczający lub w tolerancji ({tolerance} MB).")
            return

        # Jeśli swap jest za mały
        logger.info(f"Swap ({current_swap} MB) jest mniejszy niż wymagany ({size_mb} MB). Wywołanie konfiguracji swap.")
        swap_edit(size_mb=size_mb, action=action, silent=silent)

    except Exception as e:
        # Loguj błędy
        logger.error(f"Błąd sprawdzania lub konfiguracji swap: {e}")
        if not silent:
            display_message_slowly(f"❌ Błąd: {e}")


def interactive_swap_edit():
    """
    Tryb interaktywny zarządzania swap.
    """
    check_root()

    while True:
        display_message_slowly(f"\n📊 Aktualny stan pamięci:")
        swap_info = get_swap_info()
        if swap_info:
            print(swap_info)

        print("\nWybierz akcję:")
        print("1. Ustaw nowy swap")
        print("2. Usuń aktualny swap")
        print("0. Wyjście")

        choice = input("Twój wybór: ").strip()
        if choice == "1":
            size_mb = input("Wprowadź rozmiar swap (w MB): ").strip()
            if size_mb.isdigit():
                size_mb = int(size_mb)
                create_swap_file(size_mb, reason="interaktywny")
            else:
                print("❌ Nieprawidłowe dane. Spróbuj ponownie.")
        elif choice == "2":
            disable_existing_swap()
        elif choice == "0":
            print("👋 Wyjście.")
            break
        else:
            print("❌ Nieprawidłowe dane. Spróbuj ponownie.")


def swap_edit(size_mb=None, action=None, silent=False):
    """
    Główna funkcja konfiguracji swap.

    :param size_mb: Wymagany rozmiar swap w MB.
    :param action: Typ akcji ("min", "eco", "erase", "memory_required").
    :param silent: Jeśli True, tłumi komunikaty.
    """
    check_root()

    # Sprawdź aktualny stan swap
    current_swap = run_command("free -m | awk '/^Swap:/ {print $2}'")
    current_swap = int(current_swap) if current_swap and current_swap.isdigit() else 0

    # Akcja "erase"
    if action == "erase":
        if current_swap > 0:
            disable_existing_swap()
            if not silent:
                display_message_slowly("🗑️ Swap pomyślnie usunięty.")
        else:
            if not silent:
                display_message_slowly("🔍 Nie wykryto swap.")
        return

    # Akcje ustawiające swap
    if action == "micro":
        size_mb = 512
        silent = True
    elif action == "min":
        size_mb = 64
    elif action == "eco":
        total_disk = int(run_command("df --total | tail -1 | awk '{print $2}'")) // 1024
        size_mb = total_disk // 50  # 2% miejsca na dysku
    elif action == "memory_required" and size_mb is None:
        total_disk = int(run_command("df --total | tail -1 | awk '{print $2}'")) // 1024
        size_mb = min(1024, total_disk // 10)  # 10% miejsca na dysku, ale max 1024 MB

    if size_mb is None:
        raise ValueError("Musisz podać rozmiar swap lub akcję.")

    # Sprawdź: swap już istnieje i spełnia wymagania
    if current_swap >= size_mb:
        if not silent:
            display_message_slowly(f"\n✅ Aktualny swap ({current_swap} MB) jest wystarczający. Brak zmian.")
        return

    # Utwórz nowy swap
    create_swap_file(size_mb, reason=action)

    # Końcowy stan pamięci (tylko jeśli nie cichy)
    if not silent:
        display_message_slowly(f"\n 📊 Końcowy stan pamięci:")
        final_swap_info = get_swap_info()
        if final_swap_info:
            print(final_swap_info)


if __name__ == "__main__":
    parser = ArgumentParser(description="Narzędzie do zarządzania plikiem swap.")
    parser.add_argument("--memory_required", "--mr", type=int, help="Podaj minimalny rozmiar swap w MB.")
    parser.add_argument("--min_swap", "--ms", action="store_true", help="Utwórz minimalny swap (64 MB).")
    parser.add_argument("--eco_swap", action="store_true", help="Utwórz eco swap (2% miejsca na dysku).")
    parser.add_argument("--micro_swap", action="store_true", help="Utwórz 64 MB swap w trybie cichym.")
    parser.add_argument("--erase_swap", action="store_true", help="Usuń aktualny swap.\n")

    args = parser.parse_args()  # Parsuj argumenty wiersza poleceń

    if args.erase_swap:
        swap_edit(action="erase")
    elif args.eco_swap:
        swap_edit(action="eco", silent=True)
    elif args.min_swap:
        swap_edit(action="min")
    elif args.micro_swap:
        swap_edit(action="micro", silent=True)
    elif args.memory_required:
        swap_edit(size_mb=args.memory_required, action="memory_required")
    else:
        interactive_swap_edit()
