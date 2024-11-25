#!/usr/bin/env python3
import os
import sys
import subprocess

def debug_environment():
    """Проверка переменных среды и Python-путей."""
    print("=== PYTHON ENVIRONMENT DEBUG ===\n")
    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}\n")
    print(f"PYTHONPATH:\n{sys.path}\n")

def check_project_structure(base_path):
    """Проверка структуры проекта."""
    print("=== PROJECT STRUCTURE DEBUG ===\n")
    expected_structure = [
        "menu.py",
        "modules",
        "modules/__init__.py",
        "modules/test_report_generator.py",
    ]

    for path in expected_structure:
        full_path = os.path.join(base_path, path)
        if os.path.exists(full_path):
            print(f"✅ Found: {path}")
        else:
            print(f"❌ Missing: {path}")

def test_module_imports():
    """Проверка импорта модулей."""
    print("\n=== MODULE IMPORT DEBUG ===\n")
    try:
        from modules.test_report_generator import generate_report
        print("✅ Module 'test_report_generator' imported successfully.")
    except ModuleNotFoundError as e:
        print(f"❌ Error importing module 'test_report_generator': {e}")
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")

def check_test_report_script():
    """Проверка скрипта генерации отчета."""
    print("\n=== TEST REPORT GENERATION DEBUG ===\n")
    try:
        subprocess.run(["python3", "modules/test_report_generator.py"], check=True)
        print("✅ Test report script executed successfully.")
    except FileNotFoundError:
        print("❌ 'test_report_generator.py' not found in 'modules/'.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during test report script execution: {e}")

def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    debug_environment()
    check_project_structure(base_path)
    test_module_imports()
    check_test_report_script()

if __name__ == "__main__":
    main()
