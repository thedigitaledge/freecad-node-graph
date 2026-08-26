import os
import pytest
try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    try:
        from PySide2.QtWidgets import QApplication
    except ImportError:
        from PyQt5.QtWidgets import QApplication

# Set Qt offscreen platform plugin for headless test execution before Qt imports
os.environ["QT_QPA_PLATFORM"] = "offscreen"

@pytest.fixture(scope="session", autouse=True)
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
