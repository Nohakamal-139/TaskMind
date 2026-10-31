from datetime import date, timedelta

from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


STATUS_COLORS = {
    "Completed": "#16D6C1",
    "In Progress": "#2583E8",
    "Pending": "#F59E0B",
    "Overdue": "#EF4444",
    "Not Started": "#94A3B8",
}

PRIORITY_COLORS = {
    "High": "#EF4444",
    "Medium": "#F59E0B",
    "Low": "#16D6C1",
}


class TaskFormDialog(QDialog):
    def __init__(self, projects, tasks, current_task=None, parent=None):
        super().__init__(parent)

        self.tasks = tasks
        self.current_task = current_task

        self.setWindowTitle("Edit Task" if current_task else "Add New Task")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter task name")

        self.project_input = QComboBox()
        self.project_input.addItems(projects)

        self.priority_input = QComboBox()
        self.priority_input.addItems(["High", "Medium", "Low"])

        self.status_input = QComboBox()
        self.status_input.addItems([
            "Not Started",
            "Pending",
            "In Progress",
            "Completed",
            "Overdue",
        ])

        self.due_input = QDateEdit()
        self.due_input.setCalendarPopup(True)
        self.due_input.setDisplayFormat("yyyy-MM-dd")
        self.due_input.setDate(QDate.currentDate().addDays(2))

        form.addRow("Task name *", self.name_input)
        form.addRow("Project *", self.project_input)
        form.addRow("Priority", self.priority_input)
        form.addRow("Status", self.status_input)
        form.addRow("Due date", self.due_input)
        layout.addLayout(form)

        layout.addWidget(QLabel("Dependencies (optional)"))

        self.dependencies_list = QListWidget()
        current_id = current_task["id"] if current_task else None
        current_dependencies = (
            set(current_task.get("dependencies", []))
            if current_task
            else set()
        )

        for task in tasks:
            if task["id"] == current_id:
                continue

            item = QListWidgetItem(task["name"])
            item.setData(Qt.ItemDataRole.UserRole, task["id"])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked
                if task["id"] in current_dependencies
                else Qt.CheckState.Unchecked
            )
            self.dependencies_list.addItem(item)

        layout.addWidget(self.dependencies_list)

        buttons = QHBoxLayout()
        buttons.addStretch()

        cancel_button = QPushButton("Cancel")
        save_button = QPushButton("Save")
        save_button.setDefault(True)

        cancel_button.clicked.connect(self.reject)
        save_button.clicked.connect(self.save_task)

        buttons.addWidget(cancel_button)
        buttons.addWidget(save_button)
        layout.addLayout(buttons)

        if current_task:
            self.name_input.setText(current_task["name"])
            self.project_input.setCurrentText(current_task["project"])
            self.priority_input.setCurrentText(current_task["priority"])
            self.status_input.setCurrentText(current_task["status"])

            task_date = QDate.fromString(current_task["due"], "yyyy-MM-dd")
            if task_date.isValid():
                self.due_input.setDate(task_date)

    def save_task(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self,
                "Missing task name",
                "Please enter a task name.",
            )
            return

        self.accept()

    def get_data(self):
        dependencies = []

        for index in range(self.dependencies_list.count()):
            item = self.dependencies_list.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                dependencies.append(
                    item.data(Qt.ItemDataRole.UserRole)
                )

        return {
            "name": self.name_input.text().strip(),
            "project": self.project_input.currentText(),
            "priority": self.priority_input.currentText(),
            "status": self.status_input.currentText(),
            "due": self.due_input.date().toString("yyyy-MM-dd"),
            "dependencies": dependencies,
        }


class ProjectsTasksScreen(QWidget):
    tasks_changed = pyqtSignal(list)

    def __init__(self, tasks=None, projects=None, parent=None):
        super().__init__(parent)

        self.tasks = tasks if tasks is not None else []
        self.projects = projects if projects else ["My Project"]

        self._build_ui()
        self.refresh_table()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        title = QLabel("Projects & Tasks")
        title.setStyleSheet("font-size: 22pt; font-weight: 700;")

        subtitle = QLabel(
            "Manage your projects and keep track of all tasks."
        )
        subtitle.setStyleSheet("color: #94A3B8;")

        heading = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        heading.addLayout(title_box)
        heading.addStretch()

        add_button = QPushButton("+  Add Task")
        add_button.clicked.connect(self.add_task)
        heading.addWidget(add_button)
        layout.addLayout(heading)

        filters = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by task or project...")
        self.search_input.textChanged.connect(self.refresh_table)

        self.project_filter = QComboBox()
        self.project_filter.addItems(["All Projects"] + self.projects)
        self.project_filter.currentTextChanged.connect(self.refresh_table)

        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "All Statuses",
            "Not Started",
            "Pending",
            "In Progress",
            "Completed",
            "Overdue",
        ])
        self.status_filter.currentTextChanged.connect(self.refresh_table)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_filters)

        filters.addWidget(self.search_input, 3)
        filters.addWidget(self.project_filter, 1)
        filters.addWidget(self.status_filter, 1)
        filters.addWidget(clear_button)
        layout.addLayout(filters)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Task Name",
            "Project",
            "Status",
            "Priority",
            "Due Date",
            "Dependencies",
            "Actions",
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout.addWidget(self.table, 1)

    def refresh_table(self):
        search = self.search_input.text().strip().lower()
        selected_project = self.project_filter.currentText()
        selected_status = self.status_filter.currentText()

        visible_tasks = []

        for task in self.tasks:
            if search and (
                search not in task["name"].lower()
                and search not in task["project"].lower()
            ):
                continue

            if (
                selected_project != "All Projects"
                and task["project"] != selected_project
            ):
                continue

            if (
                selected_status != "All Statuses"
                and task["status"] != selected_status
            ):
                continue

            visible_tasks.append(task)

        self.table.setRowCount(len(visible_tasks))

        for row, task in enumerate(visible_tasks):
            dependency_names = []

            for dependency_id in task.get("dependencies", []):
                dependency = next(
                    (
                        item for item in self.tasks
                        if item["id"] == dependency_id
                    ),
                    None,
                )
                if dependency:
                    dependency_names.append(dependency["name"])

            values = [
                task["name"],
                task["project"],
                task["status"],
                task["priority"],
                task["due"],
                ", ".join(dependency_names) if dependency_names else "—",
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))

                if column == 2:
                    item.setForeground(
                        QColor(STATUS_COLORS.get(task["status"], "#F1F5F9"))
                    )
                elif column == 3:
                    item.setForeground(
                        QColor(PRIORITY_COLORS.get(task["priority"], "#F1F5F9"))
                    )

                self.table.setItem(row, column, item)

            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(4, 2, 4, 2)

            complete_checkbox = QCheckBox()
            complete_checkbox.setToolTip("Mark task as completed")
            complete_checkbox.setChecked(task["status"] == "Completed")
            complete_checkbox.toggled.connect(
                lambda checked, task_id=task["id"]:
                    self.set_task_completed(task_id, checked)
            )

            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(
                lambda checked=False, task_id=task["id"]:
                    self.edit_task(task_id)
            )

            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(
                lambda checked=False, task_id=task["id"]:
                    self.delete_task(task_id)
            )

            actions_layout.addWidget(complete_checkbox)
            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)

            self.table.setCellWidget(row, 6, actions)

    def add_task(self):
        dialog = TaskFormDialog(
            self.projects,
            self.tasks,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            task = dialog.get_data()
            task["id"] = max(
                (item["id"] for item in self.tasks),
                default=0,
            ) + 1

            self.tasks.append(task)
            self._notify_tasks_changed()

    def edit_task(self, task_id):
        task = next(
            (item for item in self.tasks if item["id"] == task_id),
            None,
        )
        if not task:
            return

        dialog = TaskFormDialog(
            self.projects,
            self.tasks,
            current_task=task,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            task.update(dialog.get_data())
            self._notify_tasks_changed()

    def delete_task(self, task_id):
        task = next(
            (item for item in self.tasks if item["id"] == task_id),
            None,
        )
        if not task:
            return

        answer = QMessageBox.question(
            self,
            "Delete task",
            f"Are you sure you want to delete '{task['name']}'?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if answer == QMessageBox.StandardButton.Yes:
            self.tasks = [
                item for item in self.tasks
                if item["id"] != task_id
            ]

            for item in self.tasks:
                item["dependencies"] = [
                    dependency
                    for dependency in item.get("dependencies", [])
                    if dependency != task_id
                ]

            self._notify_tasks_changed()

    def set_task_completed(self, task_id, completed):
        task = next(
            (item for item in self.tasks if item["id"] == task_id),
            None,
        )
        if not task:
            return

        task["status"] = "Completed" if completed else "Not Started"
        self._notify_tasks_changed()

    def clear_filters(self):
        self.search_input.clear()
        self.project_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.refresh_table()

    def _notify_tasks_changed(self):
        self.refresh_table()
        self.tasks_changed.emit(self.tasks)