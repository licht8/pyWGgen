#!/usr/bin/env python3

"""
swap_edit.py - Utility for managing the swap file in Linux

Features:
- Check and optimize swap.
- Supports parameters for flexible configuration:
  * `--memory_required` or `--mr`: Allocates swap up to 10% of disk space.
  * `--min_swap` or `--ms`: Creates a minimal fixed swap (64 MB).
  * `--eco_swap`: Creates a swap file of 2% of disk space.
  * `--erase_swap`: Completely removes swap.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from argparse import ArgumentParser
from prettytable import PrettyTable

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = CURRENT_DIR.parent
sys.path.append(str(PROJECT_DIR))

from settings import PRINT_SPEED
from ai_diagnostics.ai_diagnostics import display_message_slowly

def run_command(command, check=True):
    """Execute a command in the terminal and return the output."""
    try:
        result = subprocess.run(
            command, shell=True, text=True, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e.stderr.strip()}")
        return None

def check_root():
    """Check if the script is run as root."""
    if os.geteuid() != 0:
        display_message_slowly("🚨 This script must be run as root.", indent=False)
        exit(1)

def display_table(data, headers):
    """Display a table with data."""
    table = PrettyTable(headers)
    for row in data:
        table.add_row(row)
    return table

def get_swap_info():
    """Retrieve information about swap and memory."""
    output = run_command("free -h")
    if not output:
        return None

    headers = ["Type", "Total", "Used", "Free"]
    rows = []
    for line in output.split("\n"):
        parts = line.split()
        if len(parts) >= 4 and parts[0] in ("Mem:", "Swap:"):
            rows.append(parts[:4])

    return display_table(rows, headers)

def disable_existing_swap(swap_file="/swap"):
    """Disable and remove the existing swap file if it is in use."""
    if os.path.exists(swap_file):
        display_message_slowly(f"\n   🔍 Detected existing swap file: {swap_file}")
        run_command(f"swapoff {swap_file}", check=False)
        try:
            os.remove(swap_file)
            display_message_slowly(f"   🗑️  Removed existing swap file: {swap_file}")
        except Exception as e:
            display_message_slowly(f"   ❌  Failed to remove file: {e}")

def create_swap_file(size_mb, reason=None):
    """Create and activate a swap file."""
    try:
        swap_file = "/swap"
        disable_existing_swap(swap_file)

        display_message_slowly(f"   🛠️  Creating swap file of size {size_mb} MB...")
        run_command(f"dd if=/dev/zero of={swap_file} bs=1M count={size_mb}", check=True)

        display_message_slowly("   🎨 Formatting swap file...")
        run_command(f"mkswap {swap_file}", check=True)

        display_message_slowly("   ⚡ Activating swap file...")
        run_command(f"swapon {swap_file}", check=True)

        display_message_slowly(f"\n   ✅ Swap created. Size: {size_mb} MB")
        if reason:
            display_message_slowly(f"   🔍 Reason: {reason}")

    except Exception as e:
        display_message_slowly(f"   ❌ An error occurred: {e}")

import logging
from settings import LOG_LEVEL, LOG_FILE_PATH

# Configure logging
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=getattr(logging, LOG_LEVEL.upper(), logging.DEBUG),
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

def check_swap_edit(size_mb, action=None, silent=True, tolerance=2):
    """
    Checks the state of swap and invokes swap_edit if necessary.

    :param size_mb: Required swap size (in MB).
    :param action: Action to perform (e.g., "micro", "min").
    :param silent: If True, operates in silent mode.
    :param tolerance: Allowed difference between current and required swap (in MB).
    """
    try:
        # Check current swap
        current_swap = run_command("free -m | awk '/^Swap:/ {print $2}'")
        current_swap = int(current_swap) if current_swap and current_swap.isdigit() else 0

        # Log current swap
        logger.debug(f"Current swap: {current_swap} MB")
        logger.debug(f"Required swap: {size_mb} MB")

        # Check condition with tolerance
        if current_swap >= size_mb - tolerance:
            if not silent:
                display_message_slowly(f"✅ Current swap ({current_swap} MB) is sufficient. No changes required.")
            logger.info(f"Swap ({current_swap} MB) is sufficient or within tolerance ({tolerance} MB).")
            return

        # If swap is less than required
        logger.info(f"Swap ({current_swap} MB) is less than required ({size_mb} MB). Invoking swap configuration.")
        swap_edit(size_mb=size_mb, action=action, silent=silent)

    except Exception as e:
        # Log errors
        logger.error(f"Error checking or configuring swap: {e}")
        if not silent:
            display_message_slowly(f"❌ Error: {e}")

def interactive_swap_edit():
    """
    Interactive mode for managing swap.
    """
    check_root()

    while True:
        display_message_slowly(f"\n📊 Current memory state:")
        swap_info = get_swap_info()
        if swap_info:
            print(swap_info)

        print("\nChoose an action:")
        print("1. Set new swap")
        print("2. Remove current swap")
        print("0. Exit")

        choice = input("Your choice: ").strip()
        if choice == "1":
            size_mb = input("Enter swap size (in MB): ").strip()
            if size_mb.isdigit():
                size_mb = int(size_mb)
                create_swap_file(size_mb, reason="interactive")
            else:
                print("❌ Invalid input. Please try again.")
        elif choice == "2":
            disable_existing_swap()
        elif choice == "0":
            print("👋 Exiting.")
            break
        else:
            print("❌ Invalid input. Please try again.")

def swap_edit(size_mb=None, action=None, silent=False):
    """
    Main function for configuring swap.

    :param size_mb: Required swap size in MB.
    :param action: Action type ("min", "eco", "erase", "memory_required").
    :param silent: If True, suppresses message output.
    """
    check_root()

    # Check current swap state
    current_swap = run_command("free -m | awk '/^Swap:/ {print $2}'")
    current_swap = int(current_swap) if current_swap and current_swap.isdigit() else 0

    # "erase" action
    if action == "erase":
        if current_swap > 0:
            disable_existing_swap()
            if not silent:
                display_message_slowly("🗑️ Swap successfully removed.")
        else:
            if not silent:
                display_message_slowly("🔍 No swap detected.")
        return

    # Actions to set up swap
    if action == "micro":
        size_mb = 512
        silent = True
    elif action == "min":
        size_mb = 64
    elif action == "eco":
        total_disk = int(run_command("df --total | tail -1 | awk '{print $2}'")) // 1024
        size_mb = total_disk // 50  # 2% of disk space
    elif action == "memory_required" and size_mb is None:
        total_disk = int(run_command("df --total | tail -1 | awk '{print $2}'")) // 1024
        size_mb = min(1024, total_disk // 10)  # 10% of disk space, but no more than 1024 MB

    if size_mb is None:
        raise ValueError("Swap size or action must be specified.")

    # Check: swap already exists and meets requirements
    if current_swap >= size_mb:
        if not silent:
            display_message_slowly(f"\n✅ Current swap ({current_swap} MB) is sufficient. No changes made.")
        return

    # Create new swap
    create_swap_file(size_mb, reason=action)

    # Final memory state (only if not silent)
    if not silent:
        display_message_slowly(f"\n 📊 Final memory state:")
        final_swap_info = get_swap_info()
        if final_swap_info:
            print(final_swap_info)

if __name__ == "__main__":
    parser = ArgumentParser(description="Utility for managing the swap file.")
    parser.add_argument(f"--memory_required", "--mr", type=int, help="Specify minimum swap size in MB.")
    parser.add_argument(f"--min_swap", "--ms", action="store_true", help="Create minimal swap (64 MB).")
    parser.add_argument(f"--eco_swap", action="store_true", help="Create eco swap (2%% of disk space).")
    parser.add_argument(f"--micro_swap", action="store_true", help="Create 64 MB swap in silent mode.")
    parser.add_argument(f"--erase_swap", action="store_true", help="Remove the current swap.\n")

    args = parser.parse_args()  # Parse command-line arguments

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
