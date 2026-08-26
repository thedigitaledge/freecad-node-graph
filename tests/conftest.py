import os

# Set Qt offscreen platform plugin for headless test execution before Qt imports
os.environ["QT_QPA_PLATFORM"] = "offscreen"
