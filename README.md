# FastRes

**FastRes** is a lightweight Windows resolution switcher designed primarily for stretched resolutions in games like **Valorant**.

Built with Python + Tkinter. Supports both English and Vietnamese, with dark and light themes.

---

## Features

- Quick switch between default presets and custom resolutions
- Create and delete custom resolutions
- English / Vietnamese interface
- Dark / Light theme
- Built-in FAQ
- Uses a custom window icon (`beu.ico`)
- Works both as a Python script and a standalone executable

### Default presets

| Resolution |
|-----------|
| 2560 × 1440 |
| 1920 × 1080 |
| 1440 × 1080 |
| 1280 × 1080 |

---

## Requirements

- Windows 10 / 11
- Python 3.10+
- Pillow

```bash
pip install -r requirements.txt
```

> Changing resolution may require **Run as Administrator**.
> Custom resolutions must already exist in NVIDIA / AMD / Intel Control Panel.

---

## Run

```bash
py main.py
```

---

## Build

```bash
pyinstaller --noconfirm --clean FastRes.spec
```

Output:

```text
dist/FastRes.exe
```

---

## Usage Tips (Valorant Stretched)

1. Keep your monitor at its native resolution.
2. In Valorant, switch between **Fullscreen** and **Windowed Fullscreen** once.
3. Join a match.
4. Use FastRes to switch to your stretched resolution.

### Notes

- If black bars appear, switch back to the native resolution and try again.
- Avoid opening the **Graphics Quality** menu while using a stretched resolution.

---

## Author

**Bêu** · `@beu1411`

---

## License

Personal / educational use. Feel free to modify it for your own setup.