from datetime import date, timedelta

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class DashboardScreen(QWidget):
    """Dashboard content: welcome message, KPI cards, and Do Next list."""

    def __init__(self, tasks=None, user_name=""):
        super().__init__()
        self.tasks = tasks if tasks is not None else []
        self.user_name = user_name
        self.kpi_values = {}

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        self.setStyleSheet("""
            QWidget {
                color: #F1F5F9;
                font-family: Segoe UI;
                font-size: 10pt;
            }

            QFrame#KpiCard {
                background: #2C5B80;
                border: 2px solid #2C5B80;
                border-radius: 12px;
            }

            QFrame#Panel {
                background: #10243D;
                border: 2px solid #2C5B80;
                border-radius: 12px;
            }

            QFrame#DoNextHeader {
                background: #2C5B80;
                border-radius: 8px;
            }

            QLabel#Muted {
                color: #94A3B8;
            }

            QLabel#KpiNumber {
                color: #F1F5F9;
                font-size: 23pt;
                font-weight: 800;
            }

            QTableWidget {
                background: #081B31;
                alternate-background-color: #0B213A;
                color: #E7F0FA;
                border: 2px solid #2C5B80;
                border-top: none;
                gridline-color: #2C5B80;
                selection-background-color: #164A78;
            }

            QHeaderView::section {
                background: #10243D;
                color: #8FCBFF;
                border: none;
                border-bottom: 1px solid #2C5B80;
                padding: 10px 6px;
                font-weight: 700;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        self.welcome_label = QLabel()
        self.welcome_label.setStyleSheet(
            "font-size: 16pt; font-weight: 700; padding: 7px;"
        )
        layout.addWidget(self.welcome_label)

        cards_layout = QGridLayout()
        cards_layout.setSpacing(12)

        cards = [
            ("Total Tasks", "total", "#2583E8"),
            ("Completed Tasks", "completed", "#16D6C1"),
            ("Overdue Tasks", "overdue", "#EF4444"),
            ("Due This Week", "week", "#F59E0B"),
        ]

        for column, (title, key, color) in enumerate(cards):
            card = QFrame()
            card.setObjectName("KpiCard")

            card_layout = QVBoxLayout(card)

            label = QLabel(title)
            label.setStyleSheet(
                f"color: {color}; font-weight: 700; background: transparent;"
            )

            value = QLabel("0")
            value.setObjectName("KpiNumber")
            value.setStyleSheet("background: transparent;")

            subtitle = QLabel("Task Mind overview")
            subtitle.setObjectName("Muted")
            subtitle.setStyleSheet("background: transparent;")

            card_layout.addWidget(label)
            card_layout.addWidget(value)
            card_layout.addWidget(subtitle)

            cards_layout.addWidget(card, 0, column)
            self.kpi_values[key] = value

        layout.addLayout(cards_layout)

        panel = QFrame()
        panel.setObjectName("Panel")

        panel_layout = QVBoxLayout(panel)
        panel_layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("DoNextHeader")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 5, 10, 5)

        icon = QLabel("☑")
        icon.setStyleSheet(
            "font-size: 22pt; color: #20C9D8; "
            "font-weight: 700; background: transparent;"
        )

        title = QLabel("Do Next")
        title.setStyleSheet(
            "font-size: 16pt; font-weight: 700; background: transparent;"
        )

        helper = QLabel("Top 5 tasks you can start now")
        helper.setObjectName("Muted")
        helper.setStyleSheet("background: transparent;")

        header_layout.addWidget(icon)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(helper)

        panel_layout.addWidget(header)

        self.do_next_table = QTableWidget(0, 4)
        self.do_next_table.setHorizontalHeaderLabels(
            ["Task Name", "Project", "Priority", "Due Date"]
        )
        self.do_next_table.setAlternatingRowColors(True)
        self.do_next_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.do_next_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.do_next_table.verticalHeader().setVisible(False)
        self.do_next_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.do_next_table.verticalHeader().setDefaultSectionSize(42)
        self.do_next_table.setMaximumHeight(300)

        panel_layout.addWidget(self.do_next_table)
        layout.addWidget(panel)
        layout.addStretch()

    def set_tasks(self, tasks):
        """Update the dashboard with the latest task list."""
        self.tasks = tasks
        self.refresh()

    def set_user_name(self, user_name):
        self.user_name = user_name
        self.refresh_welcome()

    def refresh(self):
        self.refresh_welcome()
        self.refresh_kpis()
        self.refresh_do_next()

    def refresh_welcome(self):
        if self.user_name:
            greeting = f"☀   Good Morning, {self.user_name}!"
        else:
            greeting = "☀   Good Morning!"

        self.welcome_label.setText(
            greeting + "\n      Stay focused. Get things done."
        )

    def refresh_kpis(self):
        today = date.today()
        week_end = today + timedelta(days=7)

        completed = sum(
            task["status"] == "Completed"
            for task in self.tasks
        )

        overdue = sum(
            task["status"] == "Overdue"
            or (
                task["status"] != "Completed"
                and date.fromisoformat(task["due"]) < today
            )
            for task in self.tasks
        )

        due_this_week = sum(
            today <= date.fromisoformat(task["due"]) <= week_end
            and task["status"] != "Completed"
            for task in self.tasks
        )

        values = {
            "total": len(self.tasks),
            "completed": completed,
            "overdue": overdue,
            "week": due_this_week,
        }

        for key, value in values.items():
            self.kpi_values[key].setText(str(value))

    def refresh_do_next(self):
        completed_ids = {
            task["id"]
            for task in self.tasks
            if task["status"] == "Completed"
        }

        available_tasks = [
            task
            for task in self.tasks
            if task["status"] not in ("Completed", "Overdue")
            and all(
                dependency in completed_ids
                for dependency in task.get("dependencies", [])
            )
        ]

        priority_order = {
            "High": 0,
            "Medium": 1,
            "Low": 2,
        }

        available_tasks.sort(
            key=lambda task: (
                priority_order.get(task["priority"], 3),
                task["due"],
            )
        )

        tasks_to_show = available_tasks[:5]
        self.do_next_table.setRowCount(len(tasks_to_show))

        priority_colors = {
            "High": "#EF4444",
            "Medium": "#F59E0B",
            "Low": "#16D6C1",
        }

        for row, task in enumerate(tasks_to_show):
            values = [
                task["name"],
                task["project"],
                task["priority"],
                task["due"],
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))

                if column == 2:
                    color = priority_colors.get(
                        task["priority"],
                        "#2583E8",
                    )
                    item.setForeground(QColor(color))

                self.do_next_table.setItem(row, column, item)