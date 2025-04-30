# 🚀 Docker Volume Renamer
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-blue?logo=github)](https://github.com/sponsors/kevinveenbirkenbach) [![Patreon](https://img.shields.io/badge/Support-Patreon-orange?logo=patreon)](https://www.patreon.com/c/kevinveenbirkenbach) [![Buy Me a Coffee](https://img.shields.io/badge/Buy%20me%20a%20Coffee-Funding-yellow?logo=buymeacoffee)](https://buymeacoffee.com/kevinveenbirkenbach) [![PayPal](https://img.shields.io/badge/Donate-PayPal-blue?logo=paypal)](https://s.veen.world/paypaldonate)

A simple Python script to rename Docker volume directories and automatically stop/restart affected containers.

---

## 📋 Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
- [Help & Support](#-help--support)
- [Author](#-author)
- [License](#-license)

---

## ✨ Features

- Detects containers using the specified Docker volume
- Stops all affected containers (optional confirmation)
- Renames the volume directory under `/var/lib/docker/volumes/`
- Updates the `_data` symlink if present
- Restarts any containers that were running before the rename
- Supports `-f`/`--force` flag to skip confirmations

---

## 🛠️ Prerequisites

- Python 3.6+
- Docker Engine
- Access to `/var/lib/docker/volumes/` (usually requires root)
- [Docker SDK for Python](https://pypi.org/project/docker/)

---

## 📥 Installation

This project is installable via Kevin’s Package Manager:

```bash
pkgmgr install dovore
```

> Replace `dovore` with the latest package name if necessary.

---

## 🏃‍♂️ Usage

After installation, run the command:

```bash
dovore <old-volume-name> <new-volume-name> [--force]
```

- `<old-volume-name>`: the current name of the Docker volume folder
- `<new-volume-name>`: the desired new name for the volume folder
- `--force` or `-f`: skip all yes/no confirmation prompts

### Examples

Rename volume interactively:

```bash
sudo dovore friendica_data friendica_data_new
```

Rename without prompts:

```bash
sudo dovore -f friendica_data friendica_data_new
```

---

## ❓ Help & Support

Once installed, you can view detailed help with:

```bash
dovore --help
```

For additional support, visit the repo or contact the author.

---

## 👤 Author

**Kevin Veen-Birkenbach**  
Website: [veen.world](https://www.veen.world)
GitHub: [kevinveenbirkenbach](https://github.com/kevinveenbirkenbach)
Repo: [docker-volume-renamer](https://github.com/kevinveenbirkenbach/docker-volume-renamer)

---

## 📄 License

This project is licensed under the **GNU AFFERO GENERAL PUBLIC LICENSE V3**. See the [LICENSE](LICENSE) file for details.