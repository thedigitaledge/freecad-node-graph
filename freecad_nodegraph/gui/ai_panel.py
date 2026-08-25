"""AI Assistant GUI Panel for prompt-driven graph creation."""

try:
    from PySide6.QtWidgets import (
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QTextEdit,
        QLineEdit,
        QPushButton,
        QCheckBox,
        QComboBox,
        QGroupBox,
    )
    from PySide6.QtCore import Signal
except ImportError:
    try:
        from PySide2.QtWidgets import (
            QWidget,
            QVBoxLayout,
            QHBoxLayout,
            QLabel,
            QTextEdit,
            QLineEdit,
            QPushButton,
            QCheckBox,
            QComboBox,
            QGroupBox,
        )
        from PySide2.QtCore import Signal
    except ImportError:
        from PyQt5.QtWidgets import (
            QWidget,
            QVBoxLayout,
            QHBoxLayout,
            QLabel,
            QTextEdit,
            QLineEdit,
            QPushButton,
            QCheckBox,
            QComboBox,
            QGroupBox,
        )
        from PyQt5.QtCore import pyqtSignal as Signal

from freecad_nodegraph.ai.generator import AIGraphGenerator


class AIAssistantPanel(QWidget):
    """Panel widget for interacting with the AI Assistant to generate node graphs."""

    graph_generated = Signal()

    def __init__(self, editor_window=None, parent=None):
        super().__init__(parent)
        self.editor_window = editor_window
        self.generator = AIGraphGenerator()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Header
        header = QLabel("<b>AI CAD Assistant</b>")
        layout.addWidget(header)

        # Preset prompts combo
        layout.addWidget(QLabel("Preset Prompts:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Select an example prompt...",
            "Create a box 20x20x30 with a cylinder hole radius 5",
            "Create a sphere radius 15 fused with a box 10x10x10",
            "Translate a box 15x15x15 by vector (10, 0, 20) named MyMovedPart",
            "Create a cone radius1 10 radius2 2 height 25 cut from a box 30x30x30",
        ])
        self.preset_combo.currentIndexChanged.connect(self.on_preset_selected)
        layout.addWidget(self.preset_combo)

        # Prompt input label
        layout.addWidget(QLabel("Prompt:"))
        self.prompt_text = QTextEdit()
        self.prompt_text.setPlaceholderText("Type prompt here... e.g., 'Create a box 10x20x30 and cut a cylinder radius 4'")
        self.prompt_text.setMaximumHeight(80)
        layout.addWidget(self.prompt_text)

        # Options
        self.clear_canvas_cb = QCheckBox("Clear canvas before generate")
        self.clear_canvas_cb.setChecked(True)
        layout.addWidget(self.clear_canvas_cb)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.gen_btn = QPushButton("Generate Graph")
        self.gen_btn.setStyleSheet("font-weight: bold;")
        self.gen_btn.clicked.connect(self.generate_graph)
        btn_layout.addWidget(self.gen_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_prompt)
        btn_layout.addWidget(self.clear_btn)

        layout.addLayout(btn_layout)

        # Response / Log view
        layout.addWidget(QLabel("Assistant Output:"))
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)

    def on_preset_selected(self, index: int):
        if index > 0:
            self.prompt_text.setText(self.preset_combo.currentText())

    def clear_prompt(self):
        self.prompt_text.clear()
        self.log_view.clear()

    def generate_graph(self):
        prompt = self.prompt_text.toPlainText().strip()
        if not prompt:
            self.log_view.setText("Please enter a prompt to generate a graph.")
            return

        if not self.editor_window or not hasattr(self.editor_window, "graph"):
            self.log_view.setText("Error: No active editor window or graph bound.")
            return

        try:
            graph = self.editor_window.graph
            clear_existing = self.clear_canvas_cb.isChecked()

            self.generator.generate_from_prompt(
                prompt=prompt,
                graph=graph,
                clear_existing=clear_existing,
            )

            if hasattr(self.editor_window, "scene"):
                self.editor_window.scene.sync_from_graph()

            self.log_view.setText(
                f"Successfully generated graph with {len(graph.nodes)} nodes and {len(graph.edges)} connections.\n\n"
                f"Prompt processed: '{prompt}'"
            )
            self.graph_generated.emit()

        except Exception as e:
            self.log_view.setText(f"Error generating graph: {str(e)}")
