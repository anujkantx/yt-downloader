/**
 * yt-downloader — Interactive UI, Mobile Navigation, Copy Commands & Smart Device Detection
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Initialize Lucide Icons
  renderIcons();

  // 2. Setup Responsive Mobile Navigation
  initMobileMenu();

  // 3. Smart Device Detection & Dynamic CTA
  initDynamicDownloadButtons();

  // 4. One-Click Copy Buttons for Developer Commands
  initCopyCommands();

  // 5. Handle Window Resize (Orientation changes / Desktop testing)
  let resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      initDynamicDownloadButtons();
    }, 200);
  });
});

/**
 * Re-render Lucide icons safely
 */
function renderIcons() {
  if (window.lucide && typeof window.lucide.createIcons === "function") {
    window.lucide.createIcons();
  }
}

/**
 * Mobile Navigation Drawer Toggle
 */
function initMobileMenu() {
  const menuBtn = document.getElementById("mobile-menu-btn");
  const mobileMenu = document.getElementById("mobile-menu");
  const menuIcon = document.getElementById("mobile-menu-icon");

  if (!menuBtn || !mobileMenu) return;

  menuBtn.addEventListener("click", () => {
    const isHidden = mobileMenu.classList.contains("hidden");
    if (isHidden) {
      mobileMenu.classList.remove("hidden");
      if (menuIcon) menuIcon.setAttribute("data-lucide", "x");
    } else {
      mobileMenu.classList.add("hidden");
      if (menuIcon) menuIcon.setAttribute("data-lucide", "menu");
    }
    renderIcons();
  });

  // Close mobile menu when any nav link is clicked
  const navLinks = mobileMenu.querySelectorAll(".mobile-nav-link");
  navLinks.forEach((link) => {
    link.addEventListener("click", () => {
      mobileMenu.classList.add("hidden");
      if (menuIcon) menuIcon.setAttribute("data-lucide", "menu");
      renderIcons();
    });
  });
}

/**
 * Copy individual commands and copy-all for developer setup
 */
function initCopyCommands() {
  // 1. Individual Step Copy
  const cmdRows = document.querySelectorAll(".cmd-row");
  cmdRows.forEach((row) => {
    const codeEl = row.querySelector(".cmd-code");
    const copyBtn = row.querySelector(".copy-step-btn");
    const copyLabel = row.querySelector(".copy-step-label");

    if (!codeEl || !copyBtn) return;

    const copyHandler = (e) => {
      e.stopPropagation();
      const textToCopy = codeEl.textContent.trim();
      if (!textToCopy) return;

      navigator.clipboard.writeText(textToCopy).then(() => {
        const origLabel = copyLabel ? copyLabel.textContent : "Copy";
        if (copyLabel) copyLabel.textContent = "Copied!";
        copyBtn.classList.add("bg-emerald-600", "text-white");
        copyBtn.classList.remove("bg-slate-800", "text-slate-300");

        setTimeout(() => {
          if (copyLabel) copyLabel.textContent = origLabel;
          copyBtn.classList.remove("bg-emerald-600", "text-white");
          copyBtn.classList.add("bg-slate-800", "text-slate-300");
        }, 1600);
      }).catch((err) => {
        console.error("Clipboard copy failed:", err);
      });
    };

    copyBtn.addEventListener("click", copyHandler);
    row.addEventListener("click", copyHandler);
  });

  // 2. Copy All Commands At Once
  const copyAllBtn = document.getElementById("copy-all-btn");
  const copyAllLabel = document.getElementById("copy-all-label");
  if (copyAllBtn) {
    copyAllBtn.addEventListener("click", () => {
      const allCommands = [
        "git clone https://github.com/anujkantx/yt-downloader.git",
        "cd yt-downloader",
        "python -m venv .venv",
        ".\\.venv\\Scripts\\Activate.ps1",
        "pip install -r requirements-dev.txt",
        "python main.py"
      ].join("\n");

      navigator.clipboard.writeText(allCommands).then(() => {
        if (copyAllLabel) copyAllLabel.textContent = "Copied All!";
        copyAllBtn.classList.add("bg-emerald-600", "text-white");
        copyAllBtn.classList.remove("bg-slate-100", "text-slate-700");

        setTimeout(() => {
          if (copyAllLabel) copyAllLabel.textContent = "Copy All";
          copyAllBtn.classList.remove("bg-emerald-600", "text-white");
          copyAllBtn.classList.add("bg-slate-100", "text-slate-700");
        }, 1800);
      }).catch((err) => {
        console.error("Clipboard copy all failed:", err);
      });
    });
  }
}

/**
 * Detect client operating system and device type
 */
function getClientDevice() {
  const ua = navigator.userAgent || navigator.vendor || window.opera || "";
  const isAndroid = /android/i.test(ua);
  const isIOS = /iPad|iPhone|iPod/.test(ua) && !window.MSStream;
  const isWindows = /windows/i.test(ua);
  const isMobile = isAndroid || isIOS || window.innerWidth <= 768;

  return { isAndroid, isIOS, isWindows, isMobile };
}

/**
 * Render appropriate download buttons based on detected device
 */
function initDynamicDownloadButtons() {
  const device = getClientDevice();
  const heroCtaContainer = document.getElementById("dynamic-hero-cta");
  const navDownloadBtn = document.getElementById("nav-download-btn");
  const deviceBadge = document.getElementById("device-indicator-badge");

  // Direct Download URLs (Bypasses GitHub UI — triggers instant browser download)
  const windowsInstallerUrl = "https://github.com/anujkantx/yt-downloader/releases/latest/download/VideoDownloader-Setup.exe";
  const windowsPortableZipUrl = "https://github.com/anujkantx/yt-downloader/releases/latest/download/VideoDownloader-Portable.zip";
  const sealApkDownloadUrl = "https://github.com/JunkFood02/Seal/releases/latest/download/Seal-1.12.1-universal-release.apk";
  const sealRepoUrl = "https://github.com/JunkFood02/Seal";
  const githubRepoUrl = "https://github.com/anujkantx/yt-downloader";

  if (device.isAndroid || (device.isMobile && !device.isWindows)) {
    // ---- MOBILE / ANDROID VIEW ----
    if (deviceBadge) {
      deviceBadge.innerHTML = `
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>
        <span class="truncate">Mobile Device • Recommended Android App</span>
      `;
    }

    if (heroCtaContainer) {
      heroCtaContainer.innerHTML = `
        <div class="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 w-full">
          <!-- Primary Mobile CTA: Seal Android APK -->
          <a href="${sealApkDownloadUrl}" target="_blank"
             class="w-full sm:w-auto px-6 sm:px-8 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm sm:text-base shadow-md transition flex items-center justify-center gap-2.5 whitespace-nowrap shrink-0">
            <i data-lucide="smartphone" class="w-4 h-4 sm:w-5 sm:h-5 text-emerald-400 shrink-0"></i>
            <span class="whitespace-nowrap">Download Seal APK (Android)</span>
          </a>

          <!-- Secondary CTA: Seal GitHub Repo -->
          <a href="${sealRepoUrl}" target="_blank"
             class="w-full sm:w-auto px-5 sm:px-6 py-3.5 rounded-xl bg-white hover:bg-slate-50 text-slate-800 border border-slate-300 font-semibold text-sm sm:text-base transition flex items-center justify-center gap-2 card-shadow whitespace-nowrap shrink-0">
            <i data-lucide="github" class="w-4 h-4 sm:w-5 sm:h-5 shrink-0"></i>
            <span class="whitespace-nowrap">Seal on GitHub</span>
          </a>
        </div>

        <div class="mt-4 text-xs text-slate-500 font-medium flex flex-wrap items-center justify-center gap-1.5 sm:gap-2 text-center px-2">
          <span>Need the Windows Desktop app?</span>
          <a href="${windowsInstallerUrl}" class="text-slate-900 font-bold hover:underline inline-flex items-center gap-1 whitespace-nowrap">
            Download for PC (.exe) <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
          </a>
        </div>
      `;
    }

    if (navDownloadBtn) {
      navDownloadBtn.href = sealApkDownloadUrl;
      navDownloadBtn.innerHTML = `
        <i data-lucide="smartphone" class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-emerald-400 shrink-0"></i>
        <span class="whitespace-nowrap">Get Seal APK</span>
      `;
    }
  } else {
    // ---- DESKTOP / WINDOWS VIEW (Default Primary Goal) ----
    if (deviceBadge) {
      deviceBadge.innerHTML = `
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>
        <span class="truncate">Open Source Windows Desktop Application</span>
      `;
    }

    if (heroCtaContainer) {
      heroCtaContainer.innerHTML = `
        <div class="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 w-full">
          <!-- Primary Desktop CTA: Direct Windows .exe Download -->
          <a href="${windowsInstallerUrl}"
             class="w-full sm:w-auto px-6 sm:px-8 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm sm:text-base shadow-md transition flex items-center justify-center gap-2.5 whitespace-nowrap shrink-0">
            <i data-lucide="download" class="w-4 h-4 sm:w-5 sm:h-5 shrink-0"></i>
            <span class="whitespace-nowrap">Download for Windows (64-bit)</span>
          </a>

          <!-- Secondary CTA: GitHub Repo -->
          <a href="${githubRepoUrl}" target="_blank"
             class="w-full sm:w-auto px-5 sm:px-6 py-3.5 rounded-xl bg-white hover:bg-slate-50 text-slate-800 border border-slate-300 font-semibold text-sm sm:text-base transition flex items-center justify-center gap-2 card-shadow whitespace-nowrap shrink-0">
            <i data-lucide="star" class="w-4 h-4 sm:w-5 sm:h-5 text-amber-500 fill-amber-500 shrink-0"></i>
            <span class="whitespace-nowrap">Star on GitHub</span>
          </a>
        </div>

        <div class="mt-4 flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-xs text-slate-500 font-medium text-center px-2">
          <span class="inline-flex items-center gap-1.5">
            <i data-lucide="archive" class="w-3.5 h-3.5 text-slate-700"></i>
            <span>Prefer no setup?</span>
            <a href="${windowsPortableZipUrl}" class="text-slate-900 font-bold hover:underline inline-flex items-center gap-1 whitespace-nowrap">
              Download Portable (.zip) <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
            </a>
          </span>
          <span class="hidden sm:inline text-slate-300">•</span>
          <span class="inline-flex items-center gap-1.5">
            <i data-lucide="smartphone" class="w-3.5 h-3.5 text-emerald-600"></i>
            <span>Looking for Android?</span>
            <a href="#android-section" class="text-slate-900 font-bold hover:underline inline-flex items-center gap-1 whitespace-nowrap">
              Get Seal App <i data-lucide="arrow-down" class="w-3.5 h-3.5"></i>
            </a>
          </span>
        </div>
      `;
    }

    if (navDownloadBtn) {
      navDownloadBtn.href = windowsInstallerUrl;
      navDownloadBtn.innerHTML = `
        <i data-lucide="download" class="w-3.5 h-3.5 sm:w-4 sm:h-4 shrink-0"></i>
        <span class="whitespace-nowrap">Download .exe</span>
      `;
    }
  }

  // Refresh Lucide icons
  renderIcons();
}
