"""Graph modification history stack for tracking node graph undo/redo snapshots."""

import time
from typing import List, Dict, Any, Optional


class HistoryRecord:
    """Represents a single snapshot record in the node graph modification history."""

    def __init__(self, json_data: str, description: str = "Modify Node Graph"):
        self.json_data: str = json_data
        self.description: str = description
        self.timestamp: float = time.time()

    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "timestamp": self.timestamp,
            "data_len": len(self.json_data),
        }


class GraphHistory:
    """Manages a history stack of graph state snapshots integrated with Undo/Redo."""

    def __init__(self, max_depth: int = 100):
        self.max_depth: int = max_depth
        self.stack: List[HistoryRecord] = []
        self.index: int = -1

    def clear(self) -> None:
        self.stack.clear()
        self.index = -1

    def push_state(self, json_data: str, description: str = "Modify Node Graph") -> None:
        """Push a new state snapshot onto the history stack."""
        if self.index >= 0 and self.index < len(self.stack):
            if self.stack[self.index].json_data == json_data:
                return

        # Truncate any redo states if pushing from middle of stack
        if self.index < len(self.stack) - 1:
            self.stack = self.stack[: self.index + 1]

        record = HistoryRecord(json_data=json_data, description=description)
        self.stack.append(record)

        if len(self.stack) > self.max_depth:
            self.stack.pop(0)

        self.index = len(self.stack) - 1

    def can_undo(self) -> bool:
        return self.index > 0

    def can_redo(self) -> bool:
        return self.index < len(self.stack) - 1

    def undo(self) -> Optional[HistoryRecord]:
        """Move back one step in history stack and return state record."""
        if self.can_undo():
            self.index -= 1
            return self.stack[self.index]
        return None

    def redo(self) -> Optional[HistoryRecord]:
        """Move forward one step in history stack and return state record."""
        if self.can_redo():
            self.index += 1
            return self.stack[self.index]
        return None

    def current_state(self) -> Optional[HistoryRecord]:
        if 0 <= self.index < len(self.stack):
            return self.stack[self.index]
        return None

    def get_history_records(self) -> List[Dict[str, Any]]:
        """Return list of all recorded history entries with active state marker."""
        records = []
        for i, rec in enumerate(self.stack):
            records.append({
                "index": i,
                "description": rec.description,
                "timestamp": rec.timestamp,
                "is_current": (i == self.index),
            })
        return records
