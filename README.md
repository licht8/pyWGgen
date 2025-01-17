# pyWGgen

> **⚠️ Attention!**
> This project is under development and is not yet ready for use. Stay tuned for updates!

**pyWGgen** is a modern WireGuard management system that includes:
- Configuration and QR code generation.
- User and expiration management.
- Removal of outdated data.
- A web interface based on **Gradio** and a console menu for management.

---

## Table of Contents

1. [Key Features](#key-features)
2. [Gradio Web Interface](#gradio-web-interface)
   - [How to Launch the Admin Panel](#how-to-launch-the-admin-panel)
3. [Requirements](#requirements)
4. [Installing and Running the Project](#installing-and-running-the-project)
   - [Quick Installation](#quick-installation)
5. [Using the Menu](#using-the-menu)
6. [Project Structure](#project-structure)
7. [Testing](#testing)
8. [Updating](#updating)
9. [License](#license)
10. [Contacts](#contacts)

---

## Key Features

- **Configuration Generation**: Create configuration files and QR codes.
- **Expiration Management**: Check and update user data.
- **Automation**: Remove outdated accounts and sync with the WireGuard server.
- **Web Interface**: Easy-to-use interface powered by Gradio.
- **Pre-Creation Validation**: Prevent data duplication.
- **Updates and Reports**: Simplified updates and detailed reports.

---

## Gradio Web Interface

Gradio provides an intuitive interface for managing the system. With it, you can:
- View and edit users.
- Create new configurations.
- Manage server status.
- Generate system state reports.

### How to Launch the Admin Panel

1. Select **g. 🌐 Open Gradio Admin Panel** in the console menu.
2. The admin panel will launch on port **7860**:
   ```plaintext
   http://127.0.0.1:7860
   ```
3. For external access, open the port in `firewalld`. Gradio will also generate a temporary public link:
   ```plaintext
   🌐 Public link: https://<unique_address>.gradio.live
   ```

---

## Requirements

1. **Python 3.8+** (Python 3.11 recommended).
2. **Git** for cloning the repository.
3. **Node.js** for Gradio support.
4. **lsof** for port checks.
5. **firewalld** for managing network rules.

---

## Installing dependencies:

```bash
sudo dnf update -y && sudo dnf install epel-release -y && \
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash - && \
sudo dnf install -y nodejs && node --version && \
sudo dnf update -y && \
sudo dnf install git mc htop tar gcc curl openssl-devel bzip2-devel libffi-devel zlib-devel -y && \
sudo dnf install net-tools lsof nano -y && \
sudo dnf install python3.11 -y && \
sudo alternatives --set python3 /usr/bin/python3.11 && python3 --version
```

#### Command Description:
1. **System Update**: `sudo dnf update -y`.
2. **Install EPEL repository**: To obtain additional packages.
3. **Installing Node.js**: Via the official NodeSource.
4. **Updating system packages and installing dependencies**:
   - Development tools (`gcc`, `curl`, `openssl-devel`, `bzip2-devel`, `libffi-devel`, `zlib-devel`).
   - Utilities (`net-tools`, `lsof`, `mc`).
5. **Installation of Python 3.11**: Followed by customization as a major version of Python.

---

## Installing and Running the Project

Run the following commands:
```bash
mkdir -p pyWGgenerator && cd pyWGgenerator
wget https://raw.githubusercontent.com/licht8/pyWGgen/refs/heads/main/run_project.sh
chmod +x run_project.sh
./run_project.sh
```

### Installation Overview
1. Creates a `pyWGgen` directory.
2. Downloads and executes the `run_project.sh` script.
3. Sets up a virtual environment and installs libraries.

---

## Using the Menu

The console menu provides convenient access to the project's main features:

```plaintext
🛡️  ======  Menu pyWGgen  ======= 🛡️
 ------------------------------------------
  g. 🌐  Open Gradio Admin Panel
  u. 👤  Manage Users
 sy. 📡  Synchronize Users
 du. 🧹  Clear User Database
 ------------------------------------------
  rw. ♻️   Reinstall WireGuard
  dw. 🗑️   Remove WireGuard
  iw. ⚙️   Install WireGuard
 up. 🔄  Update Dependencies
 ------------------------------------------
  i. 🛠️   Project Status Information
 rg. 📋  Generate Project Status Report
 fr. 📄  Show Project Status Report
 dg. 🛠️   Run Project Diagnostics
 sd. 📋  Show Diagnostics Log
  t. 🧪  Run Tests

🧩 === Help and Diagnostics Section ==== 🧩
  aih. 🗨️  Help and Diagnostics
  aid. 🤖 Run Project Diagnostics

	 0 or q. Exit
 ==========================================
```

---

## Project Structure

```plaintext
pyWGgen/
├── ai_assistant/
│   ├── chats/                # Stores chat logs and history related to the AI assistant.
│   ├── contexts/             # Contextual data used by the AI assistant for generating responses.
│   ├── inputs/               # Input files and data used by the AI assistant.
│   ├── logs/                 # Logs generated during AI assistant operations.
│   ├── models/               # Pre-trained and custom models used by the AI assistant.
│   ├── outputs/              # Output files and generated data from the AI assistant.
│   ├── prompts/              # Prompt templates and configurations for the AI assistant.
│   └── scripts/              # Custom scripts related to the AI assistant's functionality.
├── ai_diagnostics/
│   ├── ai_help/              # Contains diagnostic tools and scripts for AI troubleshooting.
│   ├── modules/              # Additional modules for AI diagnostics.
├── docs/                     # Documentation for the project.
├── gradio_admin/
│   ├── functions/            # Core utility functions used by the Gradio admin interface.
│   └── tabs/                 # Tabs and sections for the Gradio interface.
├── logs/                     # General logs for the entire project.
├── modules/                  # Core project modules for various functionalities.
├── temp/                     # Temporary files and data.
├── test/                     # Test scripts and files for the project.
├── user/                     # User-specific data and configurations.
│   └── data/                 # Detailed user data structure.
│       ├── logs/             # User-specific logs.
│       ├── qrcodes/          # QR codes generated for users.
│       ├── usr_stale_config/ # Stale or outdated user configurations.
│       └── wg_configs/       # WireGuard configuration files for users.
└── venv/                     # Python virtual environment for the project dependencies.
```

---

## Updating

To update the project you can start .sh script:
```bash
./run_project.sh
```

Or select `up. 🔄 Update Dependencies` in the console menu.

---

## License

This project is distributed under the [MIT License](LICENSE).

---

## Contacts

If you have questions, create an [Issue](https://github.com/licht8/pyWGgen/issues).

