import win32gui
import win32process
import psutil


def get_active_window() -> dict[str, str | int | None]:
    hwnd = win32gui.GetForegroundWindow()

    if not hwnd:
        return {
            "title": None,
            "process_name": None,
            "process_id": None,
        }

    title = win32gui.GetWindowText(hwnd)
    _, process_id = win32process.GetWindowThreadProcessId(hwnd)

    try:
        process = psutil.Process(process_id)
        process_name = process.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        process_name = None

    return {
        "title": title or None,
        "process_name": process_name,
        "process_id": process_id,
    }