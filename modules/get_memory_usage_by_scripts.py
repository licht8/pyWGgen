#!/usr/bin/env python3

"""
get_memory_usage_by_scripts.py
Script to analyze memory consumption of the pyWGgen project with detailed breakdown.
"""

import psutil
import os
import sys
import time
import gc
import objgraph
from pathlib import Path
from memory_profiler import memory_usage

# Add the project's root directory to sys.path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
sys.path.append(str(PROJECT_DIR))

# Import project settings
try:
    from settings import BASE_DIR
except ImportError:
    print("❌ Unable to find settings.py. Ensure the file is located in the project's root directory.")
    sys.exit(1)


def get_memory_usage_by_scripts(project_dir):
    """
    Collects memory usage information for project scripts and sorts by memory consumption.
    
    Args:
        project_dir (str): The root directory of the project.

    Returns:
        list: Sorted list of processes with their memory usage.
    """
    project_dir = os.path.abspath(project_dir)
    processes_info = []

    for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline', 'memory_info', 'cwd']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            cmdline = proc.info['cmdline']
            cwd = proc.info.get('cwd')  # Current working directory of the process
            memory_usage = proc.info['memory_info'].rss  # Memory usage in bytes

            # Check if the process belongs to the project
            if (
                cmdline and any(project_dir in arg for arg in cmdline)
                or (cwd and project_dir in cwd)
            ):
                processes_info.append({
                    'pid': pid,
                    'name': name,
                    'cmdline': ' '.join(cmdline),
                    'memory_usage': memory_usage,
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Sort processes by memory usage in descending order
    sorted_processes = sorted(processes_info, key=lambda x: x['memory_usage'], reverse=True)
    return sorted_processes


def analyze_memory_objects():
    """
    Analyzes objects in memory, displaying their growth and memory consumption.
    """
    print("\n🔍 Analyzing live objects:")
    print("Object Type              Count")
    print("-" * 50)
    for obj_type, count in objgraph.most_common_types(limit=10):
        print(f"{obj_type:<25}{count}")

    print("\n🔍 Object growth:")
    objgraph.show_growth(limit=10)


def display_memory_usage(project_dir, interval=1):
    """
    Displays real-time memory usage information for the project's scripts.

    Args:
        project_dir (str): The root directory of the project.
        interval (int): The time interval in seconds for updates.
    """
    try:
        while True:
            os.system('clear')
            processes = get_memory_usage_by_scripts(project_dir)

            if not processes:
                print(f"No processes associated with the project: {project_dir}")
                time.sleep(interval)
                continue

            total_memory = sum(proc['memory_usage'] for proc in processes)

            print(f"{'ID':<10}{'Name':<20}{'Memory Usage (MB)':<20}{'Command Line':<50}")
            print("-" * 100)
            for proc in processes:
                print(f"{proc['pid']:<10}{proc['name']:<20}{proc['memory_usage'] / (1024 ** 2):<20.2f}{proc['cmdline']:<50}")
            print("-" * 100)
            print(f"{'Total':<30}{total_memory / (1024 ** 2):<20.2f}{'MB':<50}")

            analyze_memory_objects()

            print(f"\nUpdating every {interval} seconds...")
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nProgram stopped by user.")


if __name__ == "__main__":
    # Use BASE_DIR from settings.py
    project_directory = str(BASE_DIR)
    print(f"🔍 Collecting memory usage information for the project: {project_directory}")
    display_memory_usage(project_directory, interval=1)
