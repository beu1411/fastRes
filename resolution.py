import ctypes

user32 = ctypes.windll.user32


class DEVMODE(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", ctypes.c_wchar * 32), ("dmSpecVersion", ctypes.c_ushort),
        ("dmDriverVersion", ctypes.c_ushort), ("dmSize", ctypes.c_ushort),
        ("dmDriverExtra", ctypes.c_ushort), ("dmFields", ctypes.c_ulong),
        ("dmPositionX", ctypes.c_long), ("dmPositionY", ctypes.c_long),
        ("dmDisplayOrientation", ctypes.c_ulong), ("dmDisplayFixedOutput", ctypes.c_ulong),
        ("dmColor", ctypes.c_short), ("dmDuplex", ctypes.c_short),
        ("dmYResolution", ctypes.c_short), ("dmTTOption", ctypes.c_short),
        ("dmCollate", ctypes.c_short), ("dmFormName", ctypes.c_wchar * 32),
        ("dmLogPixels", ctypes.c_ushort), ("dmBitsPerPel", ctypes.c_ulong),
        ("dmPelsWidth", ctypes.c_ulong), ("dmPelsHeight", ctypes.c_ulong),
        ("dmDisplayFlags", ctypes.c_ulong), ("dmDisplayFrequency", ctypes.c_ulong),
    ]


def set_resolution(w, h):
    dm = DEVMODE()
    dm.dmSize = ctypes.sizeof(DEVMODE)
    dm.dmPelsWidth = w
    dm.dmPelsHeight = h
    dm.dmFields = 0x80000 | 0x100000
    result = user32.ChangeDisplaySettingsW(ctypes.byref(dm), 0)
    return result == 0, result
