from datetime import date
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QFrame, QPushButton, QScrollArea
)

PRIORITY_COLORS = {
    "High": "#EF4444",
    "Medium": "#F59E0B",
    "Low": "#16D6C1",
}


class PriorityPage(QWidget):
    """S3: Priority Board Screen"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = []
        self.priority_columns = {}
        self.priority_counts = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        heading = QLabel("Priority Board")
        heading.setObjectName("PageTitle")
        subtitle = QLabel("Focus on the most important work first.")
        subtitle.setObjectName("Muted")
        layout.addWidget(heading)
        layout.addWidget(subtitle)

        board = QGridLayout()
        board.setSpacing(14)

        priorities = [
            ("High", "#EF4444"),
            ("Medium", "#F59E0B"),
            ("Low", "#16D6C1"),
        ]

        for col, (priority, color) in enumerate(priorities):
            panel = QFrame()
            panel.setObjectName("Panel")
            panel_layout = QVBoxLayout(panel)
            panel_layout.setContentsMargins(12, 12, 12, 12)
            panel_layout.setSpacing(10)

            header = QFrame()
            header.setObjectName("DoNextHeader")
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(10, 8, 10, 8)

            marker = QLabel("●")
            marker.setStyleSheet(f"color:{color}; font-size:14pt;")
            name = QLabel(f"{priority} Priority")
            name.setStyleSheet("font-size:12pt; font-weight:700;")
            count = QLabel("0")
            count.setObjectName("Muted")

            header_layout.addWidget(marker)
            header_layout.addWidget(name)
            header_layout.addStretch()
            header_layout.addWidget(count)
            panel_layout.addWidget(header)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

            content = QWidget()
            content_layout = QVBoxLayout(content)
            content_layout.setContentsMargins(2, 2, 4, 2)
            content_layout.setSpacing(9)

            scroll.setWidget(content)
            panel_layout.addWidget(scroll, 1)

            board.addWidget(panel, 0, col)
            board.setColumnStretch(col, 1)

            self.priority_columns[priority] = content_layout
            self.priority_counts[priority] = count

        layout.addLayout(board, 1)

    def set_tasks(self, tasks):
        self.tasks = tasks
        self.refresh_priority_board()

    def refresh_priority_board(self):
        for priority, column in self.priority_columns.items():
            while column.count():
                item = column.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        grouped = {"High": [], "Medium": [], "Low": []}
        for task in self.tasks:
            priority = task.get("priority", "Medium")
            grouped.setdefault(priority, []).append(task)

        today = date.today()
        for priority, tasks in grouped.items():
            tasks.sort(key=lambda t: (
                1 if t.get("status") == "Completed" else 0,
                t.get("due", "9999-12-31"),
                t.get("name", "").casefold(),
            ))
            self.priority_counts[priority].setText(str(len(tasks)))
            column = self.priority_columns[priority]

            for task in tasks:
                card = QFrame()
                card.setObjectName("TaskCard")
                card.setStyleSheet(
                    "QFrame#TaskCard { background:#081B31; border:1px solid #2C5B80; "
                    f"border-left:4px solid {PRIORITY_COLORS.get(priority, '#2583E8')}; "
                    "border-radius:8px; }"
                )
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(11, 9, 9, 9)
                card_layout.setSpacing(5)

                task_name = QLabel(task.get("name", "Untitled task"))
                task_name.setWordWrap(True)
                task_name.setStyleSheet("font-weight:700; background:transparent; border:none;")

                project = QLabel(task.get("project", "No project"))
                project.setObjectName("Muted")
                project.setStyleSheet("background:transparent; border:none;")

                bottom = QHBoxLayout()
                due = task.get("due", "")
                try:
                    due_date = date.fromisoformat(due)
                    due_text = due_date.strftime("%b %d")
                    due_color = "#EF4444" if due_date < today and task.get("status") != "Completed" else "#94A3B8"
                    if due_date < today and task.get("status") != "Completed":
                        due_text = "Overdue · " + due_text
                except (TypeError, ValueError):
                    due_text, due_color = "No due date", "#94A3B8"

                due_label = QLabel("◷  " + due_text)
                due_label.setStyleSheet(f"color:{due_color}; background:transparent; border:none;")

                edit_button = QPushButton("Edit")
                edit_button.setMaximumWidth(58)

                bottom.addWidget(due_label)
                bottom.addStretch()
                bottom.addWidget(edit_button)

                card_layout.addWidget(task_name)
                card_layout.addWidget(project)
                card_layout.addLayout(bottom)
                column.insertWidget(column.count(), card)

            column.addStretch()
