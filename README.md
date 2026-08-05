# FastRes

**FastRes** is a lightweight Windows tool for **Valorant** players — switch stretched resolutions quickly and optionally enable limited mature content (red blood & corpses).

Built with Python + Tkinter. Supports **English / Vietnamese** and **Dark / Light** themes.

---

## Features

- Quick switch between default presets and custom resolutions
- Create and delete custom resolutions
- **Disable / Enable monitors** (Device Manager) for true stretched — state is remembered
- Guide popup when a resolution is missing on the GPU (NVIDIA custom resolution + scaling steps)
- **System tray**: close (X) hides to tray instead of quitting; right-click → Show / Quit
- **Mods tab**: auto-find Valorant folder, inject Mature Content (Blood), launch game
- English / Vietnamese interface
- Dark / Light theme
- Built-in FAQ + welcome tip
- Custom window / tray icon (`beu.ico`)
- Works as a Python script or standalone `.exe`

### Default resolution presets

| Resolution  |
|-------------|
| 2560 × 1440 |
| 1920 × 1080 |
| 1440 × 1080 |
| 1280 × 1080 |

---

## What's new in v1.2.0

- Smoother app startup (no UI flicker)
- Disable / Enable all monitors from the Resolutions tab
- Minimize to system tray on window close (requires `pystray`)
- NVIDIA custom-resolution guide when Apply fails (including **Adjust desktop size and position** → Full-screen + GPU scaling)
- Safer NVIDIA Control Panel launcher (no error dialog when `nvcplui.exe` is missing)

---

## Requirements

- Windows 10 / 11
- Python 3.10+ (only if running from source)
- Pillow, psutil, pystray

```bash
pip install -r requirements.txt
```

> Changing resolution and controlling monitors require **Run as Administrator**.  
> Custom resolutions must already exist in NVIDIA / AMD / Intel Control Panel.

---

## Download (Release)

1. Go to **[Releases](https://github.com/beu1411/fastRes/releases)** and download the latest `FastRes-vX.X.X.zip`
2. Extract the zip
3. (Optional) Put Mature Content files into the `blood\` folder — see [Blood files](#blood-files-optional)
4. Run `FastRes.exe` **as Administrator**

```text
FastRes-v1.2.0/
├── FastRes.exe
└── blood/
    └── README.txt
```

---

## Run from source

```bash
cd fastRes-1.2.0
pip install -r requirements.txt
py main.py
```

The app will request Administrator rights on start.

---

## Build

```bash
pip install pyinstaller
python -m PyInstaller --noconfirm --clean FastRes.spec
```

Output:

```text
dist/FastRes.exe
```

---

## Blood files (optional)

Mature Content is **not** bundled in the repo or release for size and licensing reasons.  
If you want red blood / corpses, place these 4 files in the `blood\` folder **next to** `FastRes.exe` (or next to the source when developing):

```text
blood/
├── MatureData-WindowsClient.pak
├── MatureData-WindowsClient.sig
├── MatureData-WindowsClient.ucas
└── MatureData-WindowsClient.utoc
```

You obtain these files yourself (e.g. from a trusted mature-content pack for your client region).

### What happens when “Inject Blood” is enabled

1. Copy `MatureData-*` into the game `Paks\` folder  
2. Backup then remove original `VNGLogo-*` files (required for mature content on VNG clients)  
3. When VALORANT exits → restore `VNGLogo-*` and remove `MatureData-*`  

Ban risk is very low — no permanent changes to game files.

Without blood files, FastRes still works fully for **resolution switching** and launching the game; only inject is skipped.

---

## Usage — stretched resolution (Valorant)

1. Keep your monitor at its **native** resolution  
2. In Valorant → Settings → Video:  
   - Fullscreen + Fill → Apply  
   - then Windowed Fullscreen + Fill → Apply  
3. Enter a **live match** (not Agent Select / loading)  
4. Use FastRes to switch to your stretched resolution  

### Notes

- Switching too early can cause black bars — switch back to native and repeat from step 2  
- Do not open **Graphics Quality** while on a stretched resolution  
- For **true stretched**, disable extra monitors (Device Manager) via the buttons on the Resolutions tab  

### Create custom resolution (NVIDIA)

1. Open NVIDIA Control Panel  
2. Under **Display** → Change resolution → Customize → Create custom resolution  
3. Enter width, height and refresh rate (do not exceed your display max) → Test → Yes → OK  
4. Under **Display** → Adjust desktop size and position → Scaling: **Full-screen**, Perform scaling on: **GPU** → Apply  
5. Return to FastRes and Apply again  

---

## Usage — Mods / Blood

1. Open the **Mods** tab  
2. Click **Search** (or paste the game folder path, e.g. `D:\...\Riot Games\VALORANT\live`)  
3. Enable **Inject Blood** if you placed the files in `blood\`  
4. Click **PLAY VALORANT**  
5. When you quit the game, injected files are cleaned up automatically  

---

## Project structure

```text
FastRes/
├── main.py              # Entry (admin check)
├── valorant.py          # Path detect, blood inject, launch
├── resolution.py        # ChangeDisplaySettings + monitors + NVIDIA open
├── config.py / i18n.py  # Config + translations
├── ui/                  # Tkinter pages
├── assets/              # Icons
├── blood/               # Place MatureData files here
│   └── README.txt
└── FastRes.spec         # PyInstaller spec
```

---

## Author

**Bêu** · [TikTok @beuu1411](https://www.tiktok.com/@beuu1411) · [GitHub @beu1411](https://github.com/beu1411)

---

## License

Personal / educational use. Feel free to modify it for your own setup.  
Not affiliated with Riot Games or VNG.
