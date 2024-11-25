#!/usr/bin/env python3
# debug_project.py
# Скрипт для отладки проекта wg_qr_generator

#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

# Путь к корню проекта
PROJECT_ROOT = Path(__file__).resolve().parent

# Файл для отчета
DEBUG_REPORT = PROJECT_ROOT / "debug_report.txt"

# Список интересующих функций
TARGET_FUNCTIONS = [
    "create_user_tab",
    "delete_user_tab",
    "statistics_tab",
    "handle_port_conflict"
]

def debug_environment():
    """Проверка переменных среды и Python-путей."""
    output = [
        "=== PYTHON ENVIRONMENT DEBUG ===\n",
        f"Current Working Directory: {os.getcwd()}\n",
        f"Python Executable: {sys.executable}\n",
        f"Python Version: {sys.version}\n",
        f"PYTHONPATH:\n{sys.path}\n"
    ]
    return output

def check_project_structure(base_path):
    """Проверка структуры проекта."""
    expected_structure = [
        "menu.py",
        "modules",
        "modules/__init__.py",
        "modules/test_report_generator.py",
        "gradio_admin",
        "gradio_admin/tabs/create_user_tab.py",
        "gradio_admin/tabs/delete_user_tab.py",
        "gradio_admin/tabs/statistics_tab.py",
        "modules/port_manager.py",
    ]
    output = ["=== PROJECT STRUCTURE DEBUG ===\n"]
    for path in expected_structure:
        full_path = base_path / path
        if full_path.exists():
            output.append(f"✅ Found: {path}\n")
        else:
            output.append(f"❌ Missing: {path}\n")
    return output

def test_module_imports():
    """Проверка импорта модулей."""
    modules_to_check = [
        "modules.test_report_generator",
        "gradio_admin.tabs.create_user_tab",
        "gradio_admin.tabs.delete_user_tab",
        "gradio_admin.tabs.statistics_tab",
        "modules.port_manager",
    ]
    output = ["=== MODULE IMPORT DEBUG ===\n"]
    for module in modules_to_check:
        try:
            __import__(module)
            output.append(f"✅ Module '{module}' imported successfully.\n")
        except ModuleNotFoundError as e:
            output.append(f"❌ Error importing module '{module}': {e}\n")
        except Exception as e:
            output.append(f"❌ Unexpected error during import of '{module}': {e}\n")
    return output

def check_test_report_script():
    """Проверка выполнения скрипта генерации отчета."""
    output = ["=== TEST REPORT GENERATION DEBUG ===\n"]
    try:
        subprocess.run(["python3", "modules/test_report_generator.py"], check=True)
        output.append("✅ Test report script executed successfully.\n")
    except FileNotFoundError:
        output.append("❌ 'test_report_generator.py' not found in 'modules/'.\n")
    except subprocess.CalledProcessError as e:
        output.append(f"❌ Error during test report script execution: {e}\n")
    return output

def grep_functions_in_project(functions):
    """Находит функции в проекте."""
    function_occurrences = {}
    for function in functions:
        command = f"grep -rnw {PROJECT_ROOT} -e 'def {function}'"
        try:
            output = subprocess.check_output(command, shell=True, text=True)
            function_occurrences[function] = output.strip().split("\n")
        except subprocess.CalledProcessError:
            function_occurrences[function] = []
    return function_occurrences

def search_functions_report(functions):
    """Генерация отчета по найденным функциям."""
    output = ["=== FUNCTION SEARCH DEBUG ===\n"]
    function_occurrences = grep_functions_in_project(functions)
    for function, occurrences in function_occurrences.items():
        output.append(f"🔍 Function '{function}':\n")
        if occurrences:
            output.extend([f"  {line}\n" for line in occurrences])
        else:
            output.append("  ⚠️ Function not found in project.\n")
    return output

def main():
    # Генерация отчета
    report_lines = []
    
    # Добавляем оригинальные проверки
    report_lines.extend(debug_environment())
    report_lines.extend(check_project_structure(PROJECT_ROOT))
    report_lines.extend(test_module_imports())
    report_lines.extend(check_test_report_script())
    
    # Добавляем новые проверки
    report_lines.extend(search_functions_report(TARGET_FUNCTIONS))
    
    # Запись в файл
    with open(DEBUG_REPORT, "w", encoding="utf-8") as report_file:
        report_file.writelines(report_lines)
    
    print(f"✅ Отчет сохранен в {DEBUG_REPORT}")

if __name__ == "__main__":
    main()
