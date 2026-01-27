#!/usr/bin/env python3
"""
Testy jednostkowe CLI Gradio dla WireGuard VPN Admin.

Moduł testuje uruchamianie projektu przez CLI:
- Stałe ścieżek (PROJECT_ROOT, VENV, run_project.sh)
- Sprawdzanie istnienia skryptu i venv
- Wywołania subprocess z obsługą błędów
- Obsługa timeout i wyjątków
- Główny blok if __name__ == "__main__"
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gradio_admin.gradio_cli import (
    PROJECT_ROOT, VENV_ACTIVATE_PATH, RUN_PROJECT_SCRIPT, run_project
)

class TestGradioCLI:
    """Testy jednostkowe gradio_cli.py."""

    @staticmethod
    def get_project_root():
        return Path(__file__).resolve().parent.parent.parent

    def test_paths_structure(self):
        """Test struktury ścieżek."""
        expected_root = self.get_project_root()
        assert PROJECT_ROOT == expected_root
        assert isinstance(PROJECT_ROOT, Path)
        assert isinstance(VENV_ACTIVATE_PATH, Path)
        assert isinstance(RUN_PROJECT_SCRIPT, Path)

    def test_paths_relative_correct(self):
        """Test poprawności ścieżek względnych."""
        assert str(VENV_ACTIVATE_PATH.relative_to(PROJECT_ROOT)) == "venv/bin/activate"
        assert str(RUN_PROJECT_SCRIPT.relative_to(PROJECT_ROOT)) == "run_project.sh"

    @patch('pathlib.Path.exists')
    def test_run_project_script_missing(self, mock_exists):
        """Test braku skryptu run_project.sh."""
        mock_exists.return_value = False
        result = run_project()
        assert "❌ Skrypt" in result
        assert "run_project.sh" in result

    @patch('pathlib.Path.exists')
    def test_venv_missing(self, mock_exists):
        """Test braku środowiska wirtualnego."""
        mock_exists.side_effect = [True, False]
        result = run_project()
        assert "❌ Środowisko wirtualne" in result
        assert "venv/bin/activate" in result

    @patch('subprocess.run')
    def test_subprocess_success(self, mock_run):
        """Test sukcesu subprocess."""
        mock_run.return_value = Mock(returncode=0, stdout="OK", stderr="")
        result = run_project()
        assert "✅ Projekt pomyślnie uruchomiony" in result
        assert "OK" in result
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_subprocess_error(self, mock_run):
        """Test błędu subprocess."""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="BŁĄD")
        result = run_project()
        assert "❌ Błąd podczas uruchamiania" in result
        assert "BŁĄD" in result

    @patch('subprocess.run', side_effect=Exception("Timeout"))
    def test_subprocess_exception(self, mock_run):
        """Test obsługi wyjątków."""
        result = run_project()
        assert "❌ Wystąpił błąd: Timeout" in result

    def test_main_block(self):
        """Test bloku głównego."""
        with open('gradio_admin/gradio_cli.py', 'r') as f:
            content = f.read()
        assert 'if __name__ == "__main__":' in content
        assert 'run_project()' in content
        assert 'print(output)' in content

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
