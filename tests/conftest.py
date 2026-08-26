import os
import pytest
from PySide6.QtWidgets import QApplication

# Set Qt offscreen platform plugin for headless test execution before Qt imports
os.environ["QT_QPA_PLATFORM"] = "offscreen"

@pytest.fixture(scope="session", autouse=True)
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
