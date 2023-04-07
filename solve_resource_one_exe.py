import os
import sys

_base_path = None


def set_base_path():
    global _base_path
    if _base_path is None:
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            _base_path = sys._MEIPASS
        except Exception:
            _base_path = os.path.abspath(".")


def resource_path(relative_path):
    set_base_path()
    return os.path.join(_base_path, relative_path)
