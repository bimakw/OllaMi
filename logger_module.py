import datetime
import threading

LOG_HISTORY = ""
_lock = threading.Lock()
_MAX_ENTRIES = 50
_entry_count = 0


def log_message(prompt, response, ai_type):
    global LOG_HISTORY, _entry_count

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    short = prompt[:100] + "..." if len(prompt) > 100 else prompt

    status = "ERROR" if "ERROR" in response else "OK"
    detail = response if status == "ERROR" else f"OK ({len(response)} chars)"

    entry = (
        f"[{ts}] {status} | {ai_type}\n"
        f"  prompt: {short}\n"
        f"  detail: {detail}\n"
        f"{'—' * 40}\n"
    )

    with _lock:
        LOG_HISTORY = entry + LOG_HISTORY
        _entry_count += 1
        # potong log kalau sudah terlalu banyak
        if _entry_count > _MAX_ENTRIES:
            lines = LOG_HISTORY.split("—" * 40 + "\n")
            LOG_HISTORY = ("—" * 40 + "\n").join(lines[:_MAX_ENTRIES]) + "—" * 40 + "\n"
            _entry_count = _MAX_ENTRIES


def get_logs():
    with _lock:
        return LOG_HISTORY if LOG_HISTORY else "Belum ada log."
