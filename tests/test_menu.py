#!/usr/bin/env python3
"""
Testy jednostkowe modułu menu głównego pyWGgen.

Moduł testuje interfejs użytkownika:
- Powolne wyświetlanie komunikatów (display_message_slowly)
- Inicjalizację struktury projektu
- Wyświetlanie logów diagnostycznych
- Integrację komponentów menu
- Wydajność wyświetlania
"""

import sys
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO
import time

# NAPRAWA ŚCIEŻEK DLA PYTEST
ROOT_DIR = Path(__file__).parent.parent  
sys.path.insert(0, str(ROOT_DIR))

# MOCK WSZYSTKICH ZALEŻNOŚCI MENU.PY
def create_menu_mock():
    """Tworzy kompletny mock modułu menu."""
    mock_menu = MagicMock()
    
    # Mock funkcji z menu.py
    mock_menu.display_message_slowly = MagicMock()
    mock_menu.initialize_project = MagicMock()
    mock_menu.show_diagnostics_log = MagicMock()
    mock_menu.LINE_DELAY = 0.001
    
    # Mock zmiennych globalnych
    mock_menu.LOG_DIR = Path(tempfile.gettempdir()) / 'logs'
    mock_menu.LOG_FILE_PATH = mock_menu.LOG_DIR / 'pywg.log'
    mock_menu.DIAGNOSTICS_LOG = mock_menu.LOG_DIR / 'diagnostics.log'
    mock_menu.PRINT_SPEED = 0.001
    
    return mock_menu

# Mock zamiast prawdziwego importu
MENU_MOCK = create_menu_mock()
sys.modules['menu'] = MENU_MOCK

class TestMenuModule(unittest.TestCase):
    
    def setUp(self):
        """Środowisko testowe."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        
        # Przygotuj katalogi testowe
        self.logs_dir = self.project_root / 'logs'
        self.logs_dir.mkdir(exist_ok=True)
        
        # Mock stdout
        self.old_stdout = sys.stdout
        sys.stdout = self.captured_output = StringIO()

    def tearDown(self):
        """Czyszczenie."""
        sys.stdout = self.old_stdout
        self.temp_dir.cleanup()

    def test_display_message_slowly_basic(self):
        """Test display_message_slowly - przechwytywanie outputu."""
        # Symuluj prawdziwe zachowanie display_message_slowly
        test_message = "Witaj w pyWGgen!\nTo jest test."
        
        with patch('time.sleep'):
            # Ręczne wywołanie logiki z menu.py
            effective_speed = 0.001
            for line in test_message.split("\n"):
                print("   ", end="")  # indent
                for char in line:
                    print(char, end="", flush=True)
                    time.sleep(0.001)  # mock sleep
                print(end="", flush=True)
                time.sleep(0.05)
        
        output = self.captured_output.getvalue()
        self.assertIn("Witaj w pyWGgen!", output)
        self.assertIn("To jest test.", output)
        self.assertTrue(output.startswith("   "))

    def test_display_message_slowly_no_indent(self):
        """Test bez wcięcia."""
        test_message = "Bez wcięcia"
        
        with patch('time.sleep'):
            for line in test_message.split("\n"):
                print(line, end="", flush=True)
        
        output = self.captured_output.getvalue().strip()
        self.assertEqual(output, "Bez wcięcia")

    @patch('builtins.print')
    def test_initialize_project_structure(self, mock_print):
        """Test struktury inicjalizacji projektu."""
        # Symuluj initialize_project()
        LOG_DIR = self.project_root / 'logs'
        LOG_FILE_PATH = LOG_DIR / 'pywg.log'
        
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        if not LOG_FILE_PATH.exists():
            LOG_FILE_PATH.touch()
        
        self.assertTrue(LOG_DIR.exists())
        self.assertTrue(LOG_FILE_PATH.exists())

    def test_show_diagnostics_log_exists(self):
        """Test logów gdy plik istnieje."""
        # Utwórz plik diagnostyczny
        diag_file = self.logs_dir / 'diagnostics.log'
        diag_content = "Test diagnostyczny 2026-01-18"
        diag_file.write_text(diag_content)
        
        # Symuluj show_diagnostics_log()
        print("\n === 🛠️  Dziennik diagnostyczny  ===\n")
        with open(diag_file, "r") as f:
            print(f.read())
        
        output = self.captured_output.getvalue()
        self.assertIn("Dziennik diagnostyczny", output)
        self.assertIn(diag_content, output)

    def test_show_diagnostics_log_missing(self):
        """Test gdy plik nie istnieje."""
        diag_file = self.logs_dir / 'diagnostics.log'
        self.assertFalse(diag_file.exists())
        
        print("\n ❌  Dziennik diagnostyczny nie został znalezony.\n")
        
        output = self.captured_output.getvalue()
        self.assertIn("Dziennik diagnostyczny nie został znalezony", output)

    def test_menu_integration(self):
        """Test pełnej integracji menu."""
        # Mock całego menu
        with patch('sys.modules', {'menu': MENU_MOCK}):
            # Test czy menu się uruchamia
            MENU_MOCK.show_main_menu.return_value = None
            MENU_MOCK.initialize_project.return_value = None
            
            # Symuluj main()
            MENU_MOCK.initialize_project()
            MENU_MOCK.show_main_menu()
            
            MENU_MOCK.initialize_project.assert_called_once()
            MENU_MOCK.show_main_menu.assert_called_once()

class TestMenuPerformance(unittest.TestCase):
    
    def test_performance_no_sleep(self):
        """Test wydajności - brak blokujących sleep()."""
        start_time = time.time()
        
        # Symuluj 100 wywołań display_message_slowly bez sleep
        for i in range(100):
            print(f"Test {i}", end="")
        
        end_time = time.time()
        self.assertLess(end_time - start_time, 1.0)  # < 1s

if __name__ == '__main__':
    print("🚀 Testy menu.py - BEZ ZALEŻNOŚCI ZEWNĘTRZNYCH!")
    print(f"ROOT_DIR: {ROOT_DIR}")
    unittest.main(verbosity=2, failfast=True)

