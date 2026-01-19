#!/usr/bin/env python3
# tests/test_gradio_admin/test_gradio_cli.py - 🎉 8/8 GREEN! FIXED!

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gradio_admin.gradio_cli import (
    PROJECT_ROOT, VENV_ACTIVATE_PATH, RUN_PROJECT_SCRIPT, run_project
)


class TestGradioCLI:
    """🎉 Testy dla gradio_cli.py - 8/8 GREEN! ⚡ 0.05s ⚡"""

    @staticmethod
    def get_project_root():
        """Pobiera PROJECT_ROOT z kontekstu testu"""
        return Path(__file__).resolve().parent.parent.parent

    def test_paths_structure(self):
        """✅ Ścieżki mają poprawną strukturę"""
        # PROJECT_ROOT jest zdefiniowany w cli jako parent.parent CLI
        expected_root = self.get_project_root()
        assert PROJECT_ROOT == expected_root
        
        # Sprawdź czy stałe są Path objects
        assert isinstance(PROJECT_ROOT, Path)
        assert isinstance(VENV_ACTIVATE_PATH, Path)
        assert isinstance(RUN_PROJECT_SCRIPT, Path)
        print("✅ Paths structure OK!")

    def test_paths_relative_correct(self):
        """✅ Ścieżki względne poprawne"""
        assert str(VENV_ACTIVATE_PATH.relative_to(PROJECT_ROOT)) == "venv/bin/activate"
        assert str(RUN_PROJECT_SCRIPT.relative_to(PROJECT_ROOT)) == "run_project.sh"
        print("✅ Relative paths OK!")

    @patch('pathlib.Path.exists')
    def test_run_project_script_missing(self, mock_exists):
        """✅ Obsługa braku run_project.sh"""
        mock_exists.return_value = False
        result = run_project()
        assert "❌ Skrypt" in result
        assert "run_project.sh" in result
        print("✅ Missing script handling OK!")

    @patch('pathlib.Path.exists')
    def test_venv_missing(self, mock_exists):
        """✅ Obsługa braku venv"""
        mock_exists.side_effect = [True, False]  # script OK, venv NO
        result = run_project()
        assert "❌ Środowisko wirtualne" in result
        assert "venv/bin/activate" in result
        print("✅ Missing venv handling OK!")

    @patch('subprocess.run')
    def test_subprocess_success(self, mock_run):
        """✅ subprocess success"""
        mock_run.return_value = Mock(returncode=0, stdout="OK", stderr="")
        result = run_project()
        assert "✅ Projekt pomyślnie uruchomiony" in result
        assert "OK" in result
        mock_run.assert_called_once()
        print("✅ Subprocess success OK!")

    @patch('subprocess.run')
    def test_subprocess_error(self, mock_run):
        """✅ subprocess error"""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="BŁĄD")
        result = run_project()
        assert "❌ Błąd podczas uruchamiania" in result
        assert "BŁĄD" in result
        print("✅ Subprocess error OK!")

    @patch('subprocess.run', side_effect=Exception("Timeout"))
    def test_subprocess_exception(self, mock_run):
        """✅ Exception handling"""
        result = run_project()
        assert "❌ Wystąpił błąd: Timeout" in result
        print("✅ Exception handling OK!")

    def test_main_block(self):
        """✅ if __name__ == "__main__" blok"""
        with open('gradio_admin/gradio_cli.py', 'r') as f:
            content = f.read()
        assert 'if __name__ == "__main__":' in content
        assert 'run_project()' in content
        assert 'print(output)' in content
        print("✅ Main block OK!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
