# Contributing to yt-downloader

First off, thank you for considering contributing to **yt-downloader**! 🎉 

Open-source projects thrive because of community members like you. Whether you are fixing a typo, reporting a bug, adding automated tests, or developing a brand new feature, your help is warmly welcomed.

---

## 🗺️ Contribution Workflow at a Glance

```text
[1. Fork Repo] ──> [2. Clone Fork] ──> [3. Create Branch] ──> [4. Code & Test]
                                                                     │
[7. Merged to Main! 🎉] <── [6. Review & Approval] <── [5. Open Pull Request]
```

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
- [Complete Step-by-Step Developer Guide](#complete-step-by-step-developer-guide)
  - [Step 1: Fork the Repository](#step-1-fork-the-repository)
  - [Step 2: Clone Your Fork Locally](#step-2-clone-your-fork-locally)
  - [Step 3: Setup Local Virtual Environment](#step-3-setup-local-virtual-environment)
  - [Step 4: Create a Dedicated Feature Branch](#step-4-create-a-dedicated-feature-branch)
  - [Step 5: Code & Local Testing](#step-5-code--local-testing)
  - [Step 6: Commit and Push to Your Fork](#step-6-commit-and-push-to-your-fork)
  - [Step 7: Submit the Pull Request (PR) on GitHub](#step-7-submit-the-pull-request-pr-on-github)
  - [Step 8: Code Review & Merging Process](#step-8-code-review--merging-process)
- [Project Architecture Guide](#project-architecture-guide)
- [Git Commit Guidelines](#git-commit-guidelines)
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

## Complete Step-by-Step Developer Guide

Direct pushes to the `main` branch are protected. All contributions must go through the **Fork & Pull Request (PR)** workflow. Follow this step-by-step guide:

### Step 1: Fork the Repository
1. Navigate to the main repository: [https://github.com/anujkantx/yt-downloader](https://github.com/anujkantx/yt-downloader)
2. In the top-right corner, click the **"Fork"** button.
3. This creates a personal copy of the repository under your own GitHub account (`https://github.com/<your-username>/yt-downloader`).

---

### Step 2: Clone Your Fork Locally
Open your terminal (PowerShell, Command Prompt, or Bash) and clone your fork:

```bash
# Clone your fork (replace <your-username> with your GitHub username)
git clone https://github.com/<your-username>/yt-downloader.git

# Enter project directory
cd yt-downloader

# Link the original repository as 'upstream' to stay in sync
git remote add upstream https://github.com/anujkantx/yt-downloader.git
```

Verify your remotes:
```bash
git remote -v
# origin   https://github.com/<your-username>/yt-downloader.git (fetch & push)
# upstream https://github.com/anujkantx/yt-downloader.git (fetch & push)
```

---

### Step 3: Setup Local Virtual Environment
Create and activate an isolated Python virtual environment:

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

*(Note: If PowerShell shows an execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and retry activation).*

Upgrade pip and install all development dependencies:
```powershell
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

Launch the app to verify your local setup:
```powershell
python main.py
```

---

### Step 4: Create a Dedicated Feature Branch
Never make changes directly on your `main` branch. Always create a new branch:

```powershell
# Ensure you are on the latest upstream main
git checkout main
git pull upstream main

# Create and switch to your feature branch
git checkout -b feature/my-awesome-feature
# Or for a bug fix:
git checkout -b fix/issue-description
```

---

### Step 5: Code & Local Testing
Write your clean code following PEP 8 conventions. Before committing, run our automated verification suite:

```powershell
# 1. Run automated unit and integration tests
pytest -v

# 2. Check for linting errors with Ruff
ruff check app tests

# 3. Auto-fix formatting and lint issues
ruff check --fix app tests
ruff format app tests
```

> [!IMPORTANT]
> All unit tests must pass (`26 passed`) and Ruff must report zero errors before you proceed to the next step.

---

### Step 6: Commit and Push to Your Fork
Stage your changes and write a clear, concise commit message following conventional commit standards:

```powershell
# Stage your modified files
git add .

# Commit with a meaningful message
git commit -m "feat(ui): add subtitle language selection dropdown"

# Push the branch to YOUR GitHub fork (origin)
git push -u origin feature/my-awesome-feature
```

---

### Step 7: Submit the Pull Request (PR) on GitHub
1. Open your browser and go to your fork: `https://github.com/<your-username>/yt-downloader`
2. You will see a banner: **"feature/my-awesome-feature had recent pushes"** with a green **"Compare & pull request"** button. Click it!
3. Confirm the branch targets:
   - **Base repository**: `anujkantx/yt-downloader` (branch: `main`)
   - **Head repository**: `<your-username>/yt-downloader` (branch: `feature/my-awesome-feature`)
4. Fill in the **Pull Request Template**:
   - Provide a clear summary of your changes.
   - Reference any linked issues (e.g., `Closes #12`).
   - Confirm your verification checklist.
5. Click **"Create pull request"**!

---

### Step 8: Code Review & Merging Process
Once your PR is submitted:
1. **Automated CI Checks**: GitHub Actions will automatically trigger:
   - Pytest test suite across Python 3.11, 3.12, and 3.13.
   - Ruff linting verification.
   - CodeQL security analysis.
2. **Reviewer Assignment**: Project maintainer ([@anujkantx](https://github.com/anujkantx)) will be automatically requested for review via `.github/CODEOWNERS`.
3. **Addressing Review Comments**: If requested to make tweaks, simply make the edits locally, commit, and push to the same branch. The PR will update automatically:
   ```powershell
   git add .
   git commit -m "refactor: apply reviewer feedback"
   git push origin feature/my-awesome-feature
   ```
4. **Merge & Celebrate**: Once approved and all status checks pass green, [@anujkantx](https://github.com/anujkantx) will merge your PR into `main`! Your contribution is officially part of the project! 🎉

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
│   │   ├── ffmpeg_service.py   # FFmpeg binary detection & auto-download
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
├── packaging/                  # PyInstaller spec, Inno Setup, and build scripts
├── docs/                       # Official website & documentation landing page
└── tests/                      # Automated pytest suite
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

## Good First Issues & Ideas

Looking for somewhere to start? Here are a few high-value ideas:
- [ ] **Subtitle Download Support**: Add an option to fetch `.srt` or `.vtt` subtitles alongside the video.
- [ ] **Light / System Theme Toggle**: Allow switching between Dark, Light, and System themes.
- [ ] **Custom Audio Bitrate**: Allow selecting 128kbps, 192kbps, or 320kbps when extracting MP3 audio.
- [ ] **Playlist Selection**: Add UI checkboxes to selectively choose videos from a playlist before queuing.
- [ ] **Cross-Platform Support**: Help test and support packaging for Linux or macOS.

---

Thank you for contributing to make **yt-downloader** better for everyone! 🚀
