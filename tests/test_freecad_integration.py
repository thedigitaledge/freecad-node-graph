"""Integration tests verifying FreeCAD workbench loading and checking FreeCAD log/console output for errors."""

import sys
import os
import pytest


class MockFreeCADConsole:
    """Mock FreeCAD.Console object for intercepting error messages in tests."""

    def __init__(self):
        self.messages = []
        self.errors = []
        self.warnings = []

    def PrintMessage(self, msg):
        self.messages.append(str(msg))

    def PrintError(self, msg):
        self.errors.append(str(msg))

    def PrintWarning(self, msg):
        self.warnings.append(str(msg))


class MockFreeCADGui:
    """Mock FreeCADGui object for workbench registration tests."""

    _workbenches = {}
    _icon_paths = []

    @classmethod
    def addWorkbench(cls, wb):
        wb_name = getattr(wb, "MenuText", wb.__class__.__name__)
        cls._workbenches[wb_name] = wb

    @classmethod
    def addIconPath(cls, path):
        if path not in cls._icon_paths:
            cls._icon_paths.append(path)

    @classmethod
    def addCommand(cls, name, cmd):
        pass

    @classmethod
    def Workbench(cls):
        class WorkbenchBase:
            def appendToolbar(self, name, cmds):
                pass
            def appendMenu(self, name, cmds):
                pass
        return WorkbenchBase


def test_freecad_module_loading_no_log_errors(monkeypatch, capsys):
    """Test importing Init.py and InitGui.py in FreeCAD mock environment and confirm zero log errors."""

    mock_console = MockFreeCADConsole()

    # Create mock FreeCAD module if FreeCAD is not installed in standalone test environment
    if "FreeCAD" not in sys.modules:
        import types
        mock_freecad = types.ModuleType("FreeCAD")
        mock_freecad.Console = mock_console
        mock_freecad.getUserAppDataDir = lambda: "/app"
        monkeypatch.setitem(sys.modules, "FreeCAD", mock_freecad)
    else:
        monkeypatch.setattr(sys.modules["FreeCAD"], "Console", mock_console)

    if "FreeCADGui" not in sys.modules:
        import types
        mock_freecad_gui = types.ModuleType("FreeCADGui")
        mock_freecad_gui.addWorkbench = MockFreeCADGui.addWorkbench
        mock_freecad_gui.addIconPath = MockFreeCADGui.addIconPath
        mock_freecad_gui.addCommand = MockFreeCADGui.addCommand
        mock_freecad_gui.Workbench = MockFreeCADGui.Workbench()
        monkeypatch.setitem(sys.modules, "FreeCADGui", mock_freecad_gui)

    # 1. Load Init.py
    init_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Init.py")
    with open(init_path, "r", encoding="utf-8") as f:
        code_init = f.read()

    global_scope_init = {}
    exec(code_init, global_scope_init)

    # 2. Load InitGui.py
    init_gui_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "InitGui.py")
    with open(init_gui_path, "r", encoding="utf-8") as f:
        code_init_gui = f.read()

    global_scope_gui = {}
    exec(code_init_gui, global_scope_gui)

    # 3. Instantiate and initialize workbench class if present in globals
    if "NodeGraphWorkbench" in global_scope_gui:
        wb_cls = global_scope_gui["NodeGraphWorkbench"]
        wb_inst = wb_cls()
        if hasattr(wb_inst, "Initialize"):
            wb_inst.Initialize()

    # Capture stdout and stderr
    captured = capsys.readouterr()

    # Assert no errors occurred in mock FreeCAD Console log
    assert len(mock_console.errors) == 0, f"FreeCAD Console logged errors: {mock_console.errors}"
    assert "Error" not in captured.err, f"Stderr contained error output: {captured.err}"
