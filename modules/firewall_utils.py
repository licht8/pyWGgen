#!/usr/bin/env python3
# modules/firewall_utils.py
# Funkcje do zarządzania portami przez firewalld

import subprocess
import psutil
from modules.port_manager import handle_port_conflict
import socket


def get_external_ip():
    """
    Pobiera zewnętrzny adres IP przez wewnętrzne ustawienia lub interfejsy sieciowe.

    :return: Zewnętrzny adres IP (string) lub komunikat błędu.
    """
    try:
        # Próba określenia zewnętrznego IP przez standardowe interfejsy sieciowe
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Połączenie z publicznym serwerem DNS Google aby określić IP
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]  # Pobranie adresu IP z socketa
    except OSError as e:
        return f"N/A ❌ (Błąd: {e})"


def open_firewalld_port(port):
    """
    Otwiera port w firewalld.

    :param port: Numer portu do otwarcia.
    """
    # Moduł do zarządzania portami i rozwiązywania konfliktów
    # Sprawdza czy port jest używany i pyta użytkownika o akcje.
    handle_port_conflict(port)
    print(f" 🔓  Otwieranie portu {port} przez firewalld...\n")
    subprocess.run(["firewall-cmd", "--add-port", f"{port}/tcp"])
    # Odkomentuj poniższą linię aby przeładować firewalld po zmianach
    # subprocess.run(["firewall-cmd", "--reload"])


def close_firewall_port(port):
    """
    Zamyka port w firewalld.

    :param port: Numer portu do zamknięcia.
    """
    print(f" 🔒  Zamykanie portu {port} przez firewalld...\n")
    subprocess.run(["firewall-cmd", "--remove-port", f"{port}/tcp"])
    # Odkomentuj poniższą linię aby przeładować firewalld po zmianach
    # subprocess.run(["firewall-cmd", "--reload"])
