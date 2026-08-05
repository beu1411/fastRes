"""
Valorant path detection, blood injection, launch & cleanup.
Launch flow mirrors HiddenDisplay:
  kill Riot -> start Riot -> wait lockfile/API -> trigger Play -> wait game -> inject.
"""
import os
import sys
import time
import json
import base64
import ssl
import shutil
import threading
import subprocess
import urllib.request
from pathlib import Path

from config import BASE_DIR, BUNDLE_DIR

BLOOD_FILES = [
    "MatureData-WindowsClient.pak",
    "MatureData-WindowsClient.sig",
    "MatureData-WindowsClient.ucas",
    "MatureData-WindowsClient.utoc",
]

# VNG logo/pak files that must be removed for Mature Content to work correctly.
# They are backed up on inject and restored when the game exits.
VNG_FILES = [
    "VNGLogo-WindowsClient.pak",
    "VNGLogo-WindowsClient.sig",
    "VNGLogo-WindowsClient.ucas",
    "VNGLogo-WindowsClient.utoc",
]

GAME_PROCESS = "VALORANT-Win64-Shipping.exe"

COMMON_VALORANT_PATHS = [
    r"C:\Riot Games\VALORANT\live",
    r"D:\Riot Games\VALORANT\live",
    r"E:\Riot Games\VALORANT\live",
    r"F:\Riot Games\VALORANT\live",
    r"C:\Program Files\Riot Games\VALORANT\live",
    r"D:\Program Files\Riot Games\VALORANT\live",
    r"C:\Program Files (x86)\Riot Games\VALORANT\live",
]

RIOT_CLIENT_PATHS = [
    r"C:\Riot Games\Riot Client\RiotClientServices.exe",
    r"D:\Riot Games\Riot Client\RiotClientServices.exe",
    r"E:\Riot Games\Riot Client\RiotClientServices.exe",
    r"F:\Riot Games\Riot Client\RiotClientServices.exe",
    r"C:\Program Files\Riot Games\Riot Client\RiotClientServices.exe",
    r"D:\Program Files\Riot Games\Riot Client\RiotClientServices.exe",
    r"C:\Program Files (x86)\Riot Games\Riot Client\RiotClientServices.exe",
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Riot Games", "Riot Client", "RiotClientServices.exe"),
]

LOCKFILE_PATH = os.path.join(
    os.environ.get("LOCALAPPDATA", ""), "Riot Games", "Riot Client", "Config", "lockfile"
)

RIOT_PROCESS_NAMES = (
    "RiotClientServices.exe",
    "Riot Client.exe",
    "RiotClientCrashHandler.exe",
    "RiotClientUx.exe",
    "RiotClientUxRender.exe",
)


def get_blood_dir():
    for p in (BASE_DIR / "blood", BUNDLE_DIR / "blood", Path(__file__).parent / "blood"):
        if p.exists() and p.is_dir():
            return p
    return BASE_DIR / "blood"


def get_backup_dir():
    return BASE_DIR / ".blood_backup"


def detect_valorant_path():
    for path in COMMON_VALORANT_PATHS:
        if os.path.exists(path):
            return path

    for reg_path in (
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Riot Game valorant.live",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Riot Game valorant.live",
    ):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            install_location, _ = winreg.QueryValueEx(key, "InstallLocation")
            winreg.CloseKey(key)
            if install_location and os.path.exists(install_location):
                return install_location
        except Exception:
            pass

    drives = ["C:", "D:", "E:", "F:", "G:", "H:"]
    suffixes = [
        r"\Riot Games\VALORANT\live",
        r"\valo\Riot Games\VALORANT\live",
        r"\Games\Riot Games\VALORANT\live",
        r"\VALORANT\live",
    ]
    for drive in drives:
        root = drive + "\\"
        if not os.path.exists(root):
            continue
        for suf in suffixes:
            candidate = drive + suf
            if os.path.exists(candidate):
                return candidate
        try:
            for name in os.listdir(root):
                candidate = os.path.join(root, name, "Riot Games", "VALORANT", "live")
                if os.path.exists(candidate):
                    return candidate
        except OSError:
            pass
    return ""


def get_paks_dir(valorant_path):
    if not valorant_path:
        return None
    for sub in ("ShooterGame/Content/Paks", "live/ShooterGame/Content/Paks"):
        p = os.path.join(valorant_path, sub)
        if os.path.exists(p):
            return p
    p = os.path.join(valorant_path, "ShooterGame", "Content", "Paks")
    return p if os.path.exists(p) else None


def find_riot_client():
    for path in RIOT_CLIENT_PATHS:
        if path and os.path.exists(path):
            return path
    try:
        installs_json = os.path.join(
            os.environ.get("PROGRAMDATA", ""), "Riot Games", "RiotClientInstalls.json"
        )
        if os.path.exists(installs_json):
            with open(installs_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            for val in data.values():
                if isinstance(val, str) and val.endswith(".exe") and os.path.exists(val):
                    return val
                if isinstance(val, dict):
                    for v in val.values():
                        if isinstance(v, str) and "RiotClientServices" in v and os.path.exists(v):
                            return v
    except Exception:
        pass
    try:
        import psutil
        for proc in psutil.process_iter(["name", "exe"]):
            try:
                if proc.info["name"] == "RiotClientServices.exe" and proc.info["exe"]:
                    return proc.info["exe"]
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except ImportError:
        pass
    return None


def is_game_running():
    try:
        import psutil
        for proc in psutil.process_iter(["name"]):
            try:
                if proc.info["name"] == GAME_PROCESS:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except ImportError:
        try:
            out = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {GAME_PROCESS}"],
                capture_output=True, text=True, timeout=5,
                creationflags=0x08000000,
            )
            return GAME_PROCESS.lower() in out.stdout.lower()
        except Exception:
            return False
    return False


def _is_riot_running():
    try:
        import psutil
        for proc in psutil.process_iter(["name"]):
            try:
                if proc.info["name"] in RIOT_PROCESS_NAMES:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except ImportError:
        pass
    return False


def _kill_riot_client():
    try:
        import psutil
        for proc in psutil.process_iter(["name"]):
            try:
                if proc.info["name"] in RIOT_PROCESS_NAMES:
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except ImportError:
        for name in RIOT_PROCESS_NAMES:
            try:
                subprocess.run(
                    ["taskkill", "/F", "/IM", name],
                    capture_output=True, timeout=5,
                    creationflags=0x08000000,
                )
            except Exception:
                pass
    time.sleep(1.5)
    if os.path.exists(LOCKFILE_PATH):
        try:
            os.remove(LOCKFILE_PATH)
        except OSError:
            pass


def _read_lockfile():
    if not os.path.exists(LOCKFILE_PATH):
        return None, None
    try:
        with open(LOCKFILE_PATH, "r", encoding="utf-8") as f:
            content = f.read().strip()
        parts = content.split(":")
        if len(parts) >= 5:
            return int(parts[2]), parts[3]
    except Exception:
        pass
    return None, None


def _riot_api_ping(port, password):
    url = f"https://127.0.0.1:{port}/riotclient/region-locale"
    try:
        result = subprocess.run(
            ["curl", "-sk", "-u", f"riot:{password}", url],
            capture_output=True, text=True, timeout=3,
            creationflags=0x08000000,
        )
        return result.returncode == 0 and len(result.stdout.strip()) > 2
    except Exception:
        return False


def _riot_api_launch(port, password, log_func=None):
    """POST to local Riot API to launch VALORANT (same as HiddenDisplay)."""
    log = log_func or (lambda m: None)
    url = f"https://127.0.0.1:{port}/product-launcher/v1/products/valorant/patchlines/live"

    try:
        result = subprocess.run(
            ["curl", "-sk", "-u", f"riot:{password}", "-X", "POST", url],
            capture_output=True, text=True, timeout=10,
            creationflags=0x08000000,
        )
        log(f"API: {result.stdout.strip()[:120]}")
        if result.returncode == 0 and len(result.stdout.strip()) > 0:
            return True
    except FileNotFoundError:
        pass
    except Exception as e:
        log(f"curl failed: {e}")

    # Fallback urllib
    try:
        auth = base64.b64encode(f"riot:{password}".encode()).decode()
        req = urllib.request.Request(url, method="POST")
        req.add_header("Authorization", f"Basic {auth}")
        req.add_header("Content-Type", "application/json")
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        resp = urllib.request.urlopen(req, data=b"", context=ctx, timeout=10)
        body = resp.read().decode()
        log(f"API: {resp.status} {body[:80]}")
        return True
    except Exception as e:
        log(f"API exception: {e}")
        return False


def _t(strings, key, **kwargs):
    """Safe translate helper."""
    if not strings:
        return key
    text = strings.get(key, key)
    try:
        return text.format(**kwargs) if kwargs else text
    except Exception:
        return text


def inject_blood(paks_dir, log_func=None, strings=None):
    log = log_func or (lambda m: None)
    blood_dir = get_blood_dir()
    if not blood_dir.exists():
        return False, _t(strings, "log_blood_missing", path=str(blood_dir)), []

    backup_dir = get_backup_dir()
    backup_dir.mkdir(parents=True, exist_ok=True)

    injected = []
    errors = []
    for fname in BLOOD_FILES:
        src = blood_dir / fname
        dst = Path(paks_dir) / fname
        if not src.exists():
            errors.append(_t(strings, "log_missing_file", name=fname))
            continue
        try:
            if dst.exists():
                shutil.copy2(dst, backup_dir / fname)
            shutil.copy2(src, dst)
            injected.append(fname)
            log(_t(strings, "log_injected_file", name=fname))
        except Exception as e:
            errors.append(f"{fname}: {e}")

    # Remove VNG logo files so Mature Content activates correctly.
    # Backup first so they can be restored when the game exits.
    vng_removed = 0
    for fname in VNG_FILES:
        game_path = Path(paks_dir) / fname
        if not game_path.exists():
            continue
        try:
            shutil.copy2(game_path, backup_dir / fname)
            game_path.unlink()
            vng_removed += 1
            log(_t(strings, "log_removed_vng", name=fname))
        except Exception as e:
            errors.append(f"{fname}: {e}")

    if not injected:
        msg = _t(strings, "log_no_blood_injected")
        if errors:
            msg += " " + "; ".join(errors)
        return False, msg, []
    msg = _t(strings, "log_inject_summary", n=len(injected))
    if vng_removed:
        msg += _t(strings, "log_inject_vng_summary", n=vng_removed)
    if errors:
        msg += f" ({'; '.join(errors)})"
    return True, msg, injected


def restore_blood(paks_dir, injected_list, log_func=None, strings=None):
    log = log_func or (lambda m: None)
    backup_dir = get_backup_dir()
    restored = removed = 0

    # Remove injected MatureData files (or restore previous versions if any)
    for fname in injected_list:
        game_path = Path(paks_dir) / fname
        backup_path = backup_dir / fname
        try:
            if backup_path.exists():
                shutil.copy2(backup_path, game_path)
                backup_path.unlink(missing_ok=True)
                restored += 1
            elif game_path.exists():
                game_path.unlink()
                removed += 1
        except Exception as e:
            log(_t(strings, "log_restore_error", name=fname, err=e))

    # Restore VNG logo files that were removed during inject
    vng_restored = 0
    for fname in VNG_FILES:
        game_path = Path(paks_dir) / fname
        backup_path = backup_dir / fname
        if not backup_path.exists():
            continue
        try:
            shutil.copy2(backup_path, game_path)
            backup_path.unlink(missing_ok=True)
            vng_restored += 1
            log(_t(strings, "log_restored_file", name=fname))
        except Exception as e:
            log(_t(strings, "log_restore_error", name=fname, err=e))

    try:
        if backup_dir.exists() and not any(backup_dir.iterdir()):
            backup_dir.rmdir()
    except OSError:
        pass
    log(_t(strings, "log_cleanup_summary", restored=restored, removed=removed, vng=vng_restored))
    return True


def emergency_cleanup(paks_dir=None):
    backup_dir = get_backup_dir()
    if not backup_dir.exists():
        return
    if not paks_dir:
        paks_dir = get_paks_dir(detect_valorant_path())
    if not paks_dir or not os.path.exists(paks_dir):
        return
    try:
        # Restore everything that was backed up (includes VNG files + any prior MatureData)
        for fname in os.listdir(backup_dir):
            try:
                shutil.copy2(backup_dir / fname, Path(paks_dir) / fname)
                (backup_dir / fname).unlink(missing_ok=True)
            except Exception:
                pass
        # Remove leftover MatureData injects that had no prior version to restore
        for fname in BLOOD_FILES:
            gp = Path(paks_dir) / fname
            if gp.exists() and not (backup_dir / fname).exists():
                try:
                    gp.unlink()
                except Exception:
                    pass
        if backup_dir.exists() and not any(backup_dir.iterdir()):
            backup_dir.rmdir()
    except Exception:
        pass


class LaunchWorker:
    """
    Full HiddenDisplay-style launch:
      1. Find Riot Client
      2. Kill existing Riot (clean state, avoid update loop)
      3. Start Riot with --launch-product=valorant
      4. Wait for lockfile + API ready
      5. POST local API to trigger Play
      6. Wait for game process
      7. Inject blood + cleanup watcher
    """

    def __init__(self, paks_dir, enable_blood=True, on_log=None, on_ok=None, on_err=None, strings=None):
        self.paks_dir = paks_dir
        self.enable_blood = enable_blood
        self.on_log = on_log or (lambda m: None)
        self.on_ok = on_ok or (lambda: None)
        self.on_err = on_err or (lambda m: None)
        self.strings = strings or {}
        self._thread = None
        self.injected = []

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _log(self, msg):
        try:
            self.on_log(msg)
        except Exception:
            pass

    def _ts(self, key, **kwargs):
        return _t(self.strings, key, **kwargs)

    def _start_riot(self, riot_exe):
        self._log(self._ts("log_starting_riot"))
        try:
            subprocess.Popen(
                f'cmd /c start "" "{riot_exe}" --launch-product=valorant --launch-patchline=live',
                shell=True,
                creationflags=0x08000000,
            )
        except Exception as e:
            self.on_err(self._ts("log_start_riot_fail", err=e))
            return False

        # Wait for lockfile
        self._log(self._ts("log_waiting_riot"))
        for _ in range(60):
            if os.path.exists(LOCKFILE_PATH) and _is_riot_running():
                break
            time.sleep(0.25)
        else:
            self.on_err(self._ts("log_riot_timeout"))
            return False

        port, password = _read_lockfile()
        if not port:
            self._log(self._ts("log_no_lockfile"))
            return True

        self._log(self._ts("log_waiting_api"))
        for _ in range(20):
            if _riot_api_ping(port, password):
                self._log(self._ts("log_riot_ready"))
                return True
            # User closed Riot mid-wait
            if not _is_riot_running():
                self.on_err(self._ts("log_riot_closed"))
                return False
            time.sleep(1)

        self._log(self._ts("log_api_not_ready"))
        return True

    def _run(self):
        try:
            riot_exe = find_riot_client()
            if not riot_exe:
                self.on_err(self._ts("log_riot_not_found"))
                return

            self._log(self._ts("log_riot_path", path=riot_exe))

            if _is_riot_running():
                self._log(self._ts("log_closing_riot"))
                _kill_riot_client()

            if not self._start_riot(riot_exe):
                return

            # Trigger Play via local API (critical — flags alone often not enough)
            port, password = _read_lockfile()
            api_ok = False
            if port and password:
                self._log(self._ts("log_trigger_play"))
                for _ in range(3):
                    api_ok = _riot_api_launch(port, password, self._log)
                    if api_ok:
                        break
                    time.sleep(1)
                if api_ok:
                    self._log(self._ts("log_play_triggered"))
                else:
                    self._log(self._ts("log_api_failed"))
            else:
                self._log(self._ts("log_no_api"))

            # Wait for game process
            timeout = 180
            start = time.time()
            while time.time() - start < timeout:
                if is_game_running():
                    self._log(self._ts("log_valorant_detected"))
                    break
                if time.time() - start > 8 and not _is_riot_running() and not is_game_running():
                    self.on_err(self._ts("log_riot_closed"))
                    return
                time.sleep(0.4)
            else:
                self.on_err(self._ts("log_timeout"))
                return

            if self.enable_blood and self.paks_dir:
                self._log(self._ts("log_injecting"))
                ok, msg, injected = inject_blood(self.paks_dir, self._log, self.strings)
                self.injected = injected
                self._log(msg)
                if ok and injected:
                    self._log(self._ts("log_watcher_active"))
                    threading.Thread(target=self._cleanup_watcher, daemon=True).start()
            else:
                self._log(self._ts("log_blood_skipped"))

            self.on_ok()
        except Exception as e:
            self.on_err(str(e))

    def _cleanup_watcher(self):
        while is_game_running():
            time.sleep(2)
        self._log(self._ts("log_game_closed"))
        restore_blood(self.paks_dir, self.injected, self._log, self.strings)
        self._log(self._ts("log_cleanup_done"))
