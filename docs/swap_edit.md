### `swap_edit.py`

## Purpose

`swap_edit.py` is a utility for managing and optimizing the swap file in Linux systems.  
It allows creating, modifying, and deleting swap files, optimizing memory usage in the system.  
The script is suitable for both manual management and automation in projects.

---

## Table of Contents

1. [Features](#features)
2. [Supported Parameters](#supported-parameters)
3. [Operating Modes](#operating-modes)
4. [Usage Examples](#usage-examples)
5. [Silent Mode](#silent-mode)
6. [Logging](#logging)
7. [Benefits of Swap](#benefits-of-swap)
8. [Conclusion](#conclusion)

---

## Features

1. **Check current swap status:**
   - Detects swap presence, size, and usage.

2. **Create swap:**
   - Generates swap files with fixed or adaptive sizes.

3. **Delete swap:**
   - Disables and removes existing swap.

4. **Operating Modes:**
   - Interactive mode.
   - Command-line parameter control.

5. **Project Integration:**
   - Functions `swap_edit` and `check_swap_edit` can be used in external projects.

---

## Supported Parameters

1. `--memory_required` (`--mr`):
   - Minimum swap size (in MB) required for operation.
   - Limited to 10% of disk size or 2048 MB.
   - **Example:**
     ```bash
     sudo python3 swap_edit.py --memory_required 1024
     ```

2. `--min_swap` (`--ms`):
   - Creates a minimum swap size of 64 MB.
   - **Example:**
     ```bash
     sudo python3 swap_edit.py --min_swap
     ```

3. `--eco_swap`:
   - Creates a swap file with 2% of total disk size.
   - **Example:**
     ```bash
     sudo python3 swap_edit.py --eco_swap
     ```

4. `--micro_swap`:
   - Creates a 64 MB swap file without output messages.
   - **Example:**
     ```bash
     sudo python3 swap_edit.py --micro_swap
     ```

5. `--erase_swap`:
   - Removes existing swap.
   - **Example:**
     ```bash
     sudo python3 swap_edit.py --erase_swap
     ```

---

## Operating Modes

1. **Interactive Mode:**
   - The script prompts for action: create swap, delete existing swap, or exit.
   - **Example:**
     ```bash
     sudo python3 swap_edit.py
     ```

2. **Automatic Mode:**
   - When parameters are passed, such as `--min_swap`, the script executes commands without confirmation.
   - **Example:**
     ```bash
     sudo python3 swap_edit.py --min_swap
     ```

3. **Silent Mode:**
   - Suppresses console output, minimizing interaction.
   - **Example:**
     ```bash
     sudo python3 swap_edit.py --micro_swap
     ```

4. **Integration:**
   - Calling `swap_edit` and `check_swap_edit` functions from other projects.
   - **Example:**
     ```python
     from modules.swap_edit import check_swap_edit
     
     # Check swap with 128 MB size
     check_swap_edit(size_mb=128, silent=True)
     ```

---

## Usage Examples

### 1. Check Current Swap

```plaintext
📊 Current Memory Status:
+-------+-------+--------------+----------+
| Type  | Total | Used         | Free     |
+-------+-------+--------------+----------+
| Mem:  | 2048  |     1024     |   1024   |
| Swap: |  512  |      256     |    256   |
+-------+-------+--------------+----------+
```

### 2. Create Swap

```plaintext
🔍 Current swap: not found.
🛠️ Creating swap of size 1024 MB...
✅ Swap successfully created. Final size: 1024 MB.
```

### 3. Delete Swap

```plaintext
🔍 Found existing swap of 512 MB.
🗑️ Removing swap...
✅ Swap removed.
```

### 4. Automatic Mode with Parameters

```plaintext
✅ Current swap (1024 MB) is already optimized. No changes required.
```

---

## Silent Mode

Used to minimize output messages. Suitable for integration into automated scripts.

1. **Command Line:**
   ```bash
   sudo python3 swap_edit.py --micro_swap
   ```

2. **Programmatic Call:**
   ```python
   from modules.swap_edit import check_swap_edit
   check_swap_edit(size_mb=64, silent=True)
   ```

---

## Logging

**Description:**
- All actions are logged to a file specified in `settings.LOG_FILE_PATH`.
- Logging level can be configured via `settings.LOG_LEVEL`.

**Example Logs:**

```plaintext
2024-12-04 08:10:12,345 - DEBUG - Current swap: 512 MB
2024-12-04 08:10:12,345 - DEBUG - Required swap: 1024 MB
2024-12-04 08:10:12,345 - INFO - Swap (512 MB) is less than required (1024 MB). Creating new swap.
```

---

## Benefits of Swap

1. **Memory Reserve:**
   Swap prevents memory shortages by reallocating resources to disk.

2. **Stability:**
   Helps prevent crashes under peak loads.

3. **Flexibility:**
   Allows system configuration adaptation for specific tasks.

---

## Conclusion

`swap_edit.py` is a reliable solution for memory management in Linux.  
The script supports flexible configuration, automation, and integration.  
It is suitable for both users and system administrators.
