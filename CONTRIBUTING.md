# Contributing to yt-downloader

First off, thank you for considering contributing to **yt-downloader**! 🎉 

Open-source projects thrive because of community members like you. Whether you are fixing a typo, reporting a bug, adding automated tests, or developing a brand new feature, your help is warmly welcomed.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Code Contributions](#code-contributions)
- [Local Development Setup](#local-development-setup)
- [Project Architecture Guide](#project-architecture-guide)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Git Commit Guidelines](#git-commit-guidelines)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Good First Issues & Ideas](#good-first-issues--ideas)

---

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

---

## How Can I Contribute?

### Reporting Bugs
Before submitting an issue, please check the [existing issues](https://github.com/anujkantx/yt-downloader/issues) to avoid duplicates. When opening a bug report:
- Use the **Bug Report** template.
- Provide a clear, reproducible step-by-step description.
- Include log outputs from `%LOCALAPPDATA%\VideoDownloader\logs\videodownloader.log`.
- Mention your Windows and Python versions.

### Suggesting Enhancements
Feature requests are always appreciated! Use the **Feature Request** template and explain:
- The problem you want to solve.
- Your proposed solution or user experience.
- Mockups or alternative approaches if applicable.

---

## Local Development Setup

Follow these steps to get a working local development environment:

### Prerequisites
- **Python 3.11+** installed (Python 3.11, 3.12, or 3.13 recommended)
- **Git**
- **FFmpeg** (Optional for basic development, but recommended for testing 1080p+ merging and MP3 conversion)

### Step-by-Step Setup

1. **Fork the Repository**  
   Click the **Fork** button at the top-right of the repository on GitHub.

2. **Clone your Fork locally**
   ```powershell
   git clone https://github.com/<YOUR-USERNAME>/yt-downloader.git
   cd yt-downloader
   ```

3. **Create and Activate a Virtual Environment**
   ```powershell
   # Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   *(If you encounter an execution policy prompt in PowerShell, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

4. **Install Dependencies**
   ```powershell
   pip install --upgrade pip
   pip install -r requirements-dev.txt
   ```

5. **Run the Application**
   ```powershell
   python main.py
   ```

---

## Project Architecture Guide

When making changes, here is how the codebase is structured:

```text
yt-downloader/
├── main.py                     # Entry point (Windows DPI awareness, bootstrap)
├── app/
│   ├── application.py          # Application coordinator & graceful shutdown
│   ├── core/                   # Download engine & queue
│   │   ├── downloader.py       # yt-dlp API wrapper & format logic
│   │   ├── download_manager.py # Multi-task scheduler & thread pool
│   │   ├── download_worker.py  # Background worker thread & progress throttling
│   │   ├── download_events.py  # Thread-safe EventBus
│   │   └── download_models.py  # Dataclasses (DownloadTask, DownloadProgress)
│   ├── services/               # System and helper services
│   │   ├── download_service.py # UI facade for starting/cancelling downloads
│   │   ├── metadata_service.py # Asynchronous URL preview & format probing
│   │   ├── ffmpeg_service.py   # FFmpeg binary detection & diagnostics
│   │   └── file_service.py     # Safe file naming, Explorer reveal, Shell execution
│   ├── database/               # SQLite history
│   │   ├── database.py         # Connection manager & WAL mode setup
│   │   ├── repository.py       # CRUD operations for tasks
│   │   └── schema.sql          # DB schema & index definitions
│   ├── config/                 # User preferences
│   │   ├── settings.py         # SettingsManager (atomic JSON saving)
│   │   └── defaults.py         # Default configurations & resolution mappings
│   ├── ui/                     # CustomTkinter interface
│   │   ├── main_window.py      # Main window & tab navigation
│   │   ├── downloads_page.py   # Download input, options, & queue view
│   │   ├── history_page.py     # Download history viewer
│   │   ├── settings_page.py    # Settings & FFmpeg diagnostic view
│   │   ├── about_page.py       # About & system info view
│   │   ├── theme.py            # Dark theme color palette & styling
│   │   └── components/         # Reusable CustomTkinter widgets
│   └── utils/                  # Helpers (paths, validators, logging)
├── packaging/                  # PyInstaller spec and Inno Setup installer scripts
└── tests/                      # Automated pytest suite
```

---

## Testing & Quality Assurance

Before submitting any code changes, verify that all tests pass and formatting conforms to project standards.

### 1. Run the Test Suite
We use `pytest` for automated unit and integration tests:
```powershell
pytest -v
```

### 2. Linting and Formatting
We use `ruff` for ultra-fast linting and code styling:
```powershell
# Check for lint errors
ruff check app tests

# Auto-fix common issues
ruff check --fix app tests

# Check code formatting
ruff format --check app tests
```

---

## Git Commit Guidelines

We recommend using [Conventional Commits](https://www.conventionalcommits.org/) for clean, readable history:

* `feat: add subtitle download option`
* `fix: handle URLs with leading whitespace`
* `docs: update setup instructions in README`
* `test: add unit test for file collision sanitization`
* `refactor: optimize SQLite history query`
* `chore: update dependencies in requirements.txt`

---

## Submitting a Pull Request

1. **Create a Feature Branch**
   ```powershell
   git checkout -b feature/my-new-feature
   # or
   git checkout -b fix/issue-description
   ```

2. **Commit Your Changes**
   ```powershell
   git add .
   git commit -m "feat: description of change"
   ```

3. **Keep Your Branch in Sync**
   ```powershell
   git fetch origin
   git rebase origin/main
   ```

4. **Push to Your Fork**
   ```powershell
   git push origin feature/my-new-feature
   ```

5. **Open a Pull Request**
   - Head over to GitHub and submit a Pull Request to the `main` branch.
   - Fill in the provided Pull Request template.
   - Ensure the automated GitHub Actions CI passes.

---

## Good First Issues & Ideas

Looking for somewhere to start? Here are a few high-value ideas:
- [ ] **Subtitle Download Support**: Add an option to fetch `.srt` or `.vtt` subtitles alongside the video.
- [ ] **Light / System Theme Toggle**: Allow switching between Dark, Light, and System themes.
- [ ] **Custom Audio Bitrate**: Allow selecting 128kbps, 192kbps, or 320kbps when extracting MP3 audio.
- [ ] **Playlist Selection**: Add UI checkboxes to selectively choose videos from a playlist before queuing.
- [ ] **Cross-Platform Support**: Help test and support packaging for Linux or macOS.

---

Thank you for contributing to make **yt-downloader** better for everyone! 🚀
