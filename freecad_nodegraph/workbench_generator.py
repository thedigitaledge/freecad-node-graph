"""Workbench discovery and dynamic node generation for FreeCAD scriptable functions."""

import os
import json
import inspect
import sys
import tempfile
import importlib
from typing import Dict, List, Any, Callable, Type, Optional, Tuple

from PySide6.QtCore import QThread, Signal

from freecad_nodegraph.core.node import BaseNode
from freecad_nodegraph.core.socket import DataType
from freecad_nodegraph.core.registry import NodeRegistry

# Known FreeCAD scriptable modules to inspect
FREECAD_MODULE_NAMES = [
    "Part",
    "Draft",
    "Arch",
    "Mesh",
    "Sketcher",
    "PartDesign",
]

_discovered_workbenches_cache: Optional[Dict[str, Dict[str, Type[BaseNode]]]] = None


def get_cache_file_path() -> str:
    """Return path to persistent JSON cache file."""
    cache_dir = None
    try:
        import FreeCAD
        if hasattr(FreeCAD, "getUserAppDataDir"):
            cache_dir = os.path.join(FreeCAD.getUserAppDataDir(), "NodeGraph")
    except Exception:
        pass

    if not cache_dir:
        cache_dir = os.path.join(tempfile.gettempdir(), "freecad_nodegraph")

    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, "workbench_nodes_cache.json")


def load_cache_from_disk() -> Dict[str, Any]:
    """Load cached workbench function signatures from disk if available."""
    cache_path = get_cache_file_path()
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache_to_disk(cache_data: Dict[str, Any]) -> None:
    """Save workbench function signatures cache data to disk."""
    cache_path = get_cache_file_path()
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)
    except Exception:
        pass


def clear_disk_cache() -> None:
    """Clear persistent JSON cache file from disk."""
    cache_path = get_cache_file_path()
    if os.path.exists(cache_path):
        try:
            os.remove(cache_path)
        except Exception:
            pass


def _infer_data_type(param_name: str, default_val: Any) -> Tuple[DataType, Any]:
    """Infer socket DataType and default value from parameter name and default value."""
    p_lower = param_name.lower()

    if isinstance(default_val, float):
        return DataType.FLOAT, default_val
    elif isinstance(default_val, int) and not isinstance(default_val, bool):
        return DataType.FLOAT, float(default_val)
    elif isinstance(default_val, bool):
        return DataType.BOOLEAN, default_val
    elif isinstance(default_val, str):
        return DataType.STRING, default_val

    if any(k in p_lower for k in ["length", "width", "height", "radius", "r1", "r2", "angle", "distance", "size", "pitch"]):
        val = float(default_val) if isinstance(default_val, (int, float)) else 10.0
        return DataType.FLOAT, val

    if any(k in p_lower for k in ["vector", "point", "pos", "center", "dir", "axis", "offset"]):
        return DataType.VECTOR, None

    if "placement" in p_lower:
        return DataType.PLACEMENT, None

    if any(k in p_lower for k in ["shape", "base", "tool", "obj", "objects", "wires"]):
        return DataType.SHAPE, None

    return DataType.ANY, default_val if default_val != inspect.Parameter.empty else None


def generate_node_class_for_function(
    workbench_name: str,
    func_name: str,
    func: Callable,
    cached_params_info: Optional[List[Tuple[str, str, Any]]] = None,
) -> Type[BaseNode]:
    """Dynamically generate a BaseNode class wrapping a scriptable function."""

    cls_type_id = f"{workbench_name}_{func_name}_Node"
    display_title = func_name.replace("make_", "").replace("make", "").strip("_")
    if not display_title:
        display_title = func_name
    display_title = display_title[0].upper() + display_title[1:] if display_title else func_name

    params_info = []
    serializable_params = []

    if cached_params_info:
        for pname, stype_str, def_val in cached_params_info:
            try:
                dt = DataType[stype_str]
            except KeyError:
                dt = DataType.ANY
            params_info.append((pname, dt, def_val))
            serializable_params.append((pname, dt.name, def_val))
    else:
        # Inspect function signature if possible
        try:
            sig = inspect.signature(func)
            for name, param in sig.parameters.items():
                if name in ("self", "cls", "args", "kwargs"):
                    continue
                dtype, def_val = _infer_data_type(name, param.default)
                params_info.append((name, dtype, def_val))
                serializable_params.append((name, dtype.name, def_val))
        except (ValueError, TypeError):
            # Fallback if function signature is C-extension / builtin
            params_info = [
                ("Shape / Input 1", DataType.SHAPE, None),
                ("Value / Input 2", DataType.ANY, None),
            ]
            serializable_params = [
                ("Shape / Input 1", DataType.SHAPE.name, None),
                ("Value / Input 2", DataType.ANY.name, None),
            ]

    def setup_sockets(self) -> None:
        for pname, ptype, pdef in self._params_info:
            self.add_input(pname, ptype, pdef)
        self.add_output("Result", DataType.SHAPE)

    def compute(self) -> None:
        args = []
        kwargs = {}
        for pname, _, _ in self._params_info:
            val = self.get_input_value(pname)
            if val is not None:
                kwargs[pname] = val

        try:
            if kwargs:
                res = self._target_func(**kwargs)
            else:
                res = self._target_func()
        except TypeError:
            # If kwargs failed due to position-only C arguments, pass positional args
            pos_args = [self.get_input_value(pname) for pname, _, _ in self._params_info]
            pos_args = [a for a in pos_args if a is not None]
            try:
                res = self._target_func(*pos_args)
            except Exception as ex:
                res = f"<Error: {ex}>"
        except Exception as ex:
            res = f"<Error: {ex}>"

        self.set_output_value("Result", res)

    class_dict = {
        "node_type": cls_type_id,
        "category": workbench_name,
        "title": f"{workbench_name}: {display_title}",
        "_target_func": staticmethod(func),
        "_params_info": params_info,
        "_serializable_params": serializable_params,
        "setup_sockets": setup_sockets,
        "compute": compute,
    }

    GeneratedWorkbenchNode = type(cls_type_id, (BaseNode,), class_dict)
    NodeRegistry.register(GeneratedWorkbenchNode)
    return GeneratedWorkbenchNode


def discover_workbench_functions(force_reload: bool = False) -> Dict[str, Dict[str, Type[BaseNode]]]:
    """Scan FreeCAD workbenches and generate node classes for scriptable functions using persistent caching."""
    global _discovered_workbenches_cache
    if _discovered_workbenches_cache is not None and not force_reload:
        return _discovered_workbenches_cache

    disk_cache = {} if force_reload else load_cache_from_disk()
    new_disk_cache = {}

    discovered: Dict[str, Dict[str, Type[BaseNode]]] = {}

    try:
        from tests.mocks import get_mock_workbenches
        mock_modules = get_mock_workbenches()
    except ImportError:
        mock_modules = {}

    for mod_name in FREECAD_MODULE_NAMES:
        mod = None
        if mod_name in sys.modules:
            mod = sys.modules[mod_name]
        else:
            try:
                mod = importlib.import_module(mod_name)
            except ImportError:
                mod = mock_modules.get(mod_name)

        if not mod:
            continue

        funcs_dict: Dict[str, Type[BaseNode]] = {}
        mod_cache = disk_cache.get(mod_name, {})
        new_mod_cache = {}

        for attr_name in dir(mod):
            if attr_name.startswith("_"):
                continue

            # Look for scriptable shape/object generator functions
            if attr_name.startswith(("make", "create", "build")):
                attr_val = getattr(mod, attr_name)
                if callable(attr_val):
                    cached_params = mod_cache.get(attr_name)
                    node_cls = generate_node_class_for_function(
                        mod_name, attr_name, attr_val, cached_params_info=cached_params
                    )
                    funcs_dict[attr_name] = node_cls
                    new_mod_cache[attr_name] = getattr(node_cls, "_serializable_params", [])

        if funcs_dict:
            discovered[mod_name] = funcs_dict
            new_disk_cache[mod_name] = new_mod_cache

    save_cache_to_disk(new_disk_cache)
    _discovered_workbenches_cache = discovered
    return discovered


class NodeGeneratorWorker(QThread):
    """Background worker thread that runs workbench discovery and node generation."""

    finished_discovery = Signal(dict)

    def __init__(self, force_reload: bool = False, parent=None):
        super().__init__(parent)
        self.force_reload = force_reload

    def run(self):
        discovered = discover_workbench_functions(force_reload=self.force_reload)
        self.finished_discovery.emit(discovered)
