import os
import sys

from src.gui import OrganizerGUI


def _setup_unicode_io() -> None:
    os.environ.setdefault("PYTHONUTF8", "1")
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def main() -> None:
    _setup_unicode_io()
    app = OrganizerGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
