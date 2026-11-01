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

from app.services.mock_data_service import load_mock_data


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

BLOCKED_COLOR = "#7C3AED"


class TaskFormDialog(QDialog):
    """نافذة إضافة أو تعديل مهمة واختيار اعتمادياتها."""

    def __init__(self, projects, tasks, current_task=None, parent=None):
        super().__init__(parent)

        self.tasks = tasks
        self.current_task = current_task

        self.setWindowTitle("Edit Task" if current_task else "Add New Task")
        self.setMinimumWidth(430)

        layout = QVBoxLayout(self)

        title = QLabel("Edit Task" if current_task else "Add New Task")
        title.setStyleSheet("font-size: 18pt; font-weight: 700;")
        layout.addWidget(title)

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

        dependencies_title = QLabel("Dependencies (optional)")
        dependencies_title.setStyleSheet("font-weight: 700; margin-top: 8px;")
        layout.addWidget(dependencies_title)

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
        save_button.setObjectName("Primary")

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

            parsed_date = QDate.fromString(current_task["due"], "yyyy-MM-dd")
            if parsed_date.isValid():
                self.due_input.setDate(parsed_date)

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
                dependencies.append(item.data(Qt.ItemDataRole.UserRole))

        return {
            "name": self.name_input.text().strip(),
            "project": self.project_input.currentText(),
            "priority": self.priority_input.currentText(),
            "status": self.status_input.currentText(),
            "due": self.due_input.date().toString("yyyy-MM-dd"),
            "dependencies": dependencies,
        }


class ProjectsTasksScreen(QWidget):
    """الشاشة الثانية: جدول المهام والبحث والفلاتر والإجراءات."""

    tasks_changed = pyqtSignal(list)

    def __init__(self, tasks=None, projects=None, parent=None):
        super().__init__(parent)

        if tasks is None or projects is None:
            mock_tasks, mock_projects = load_mock_data()
            tasks = mock_tasks if tasks is None else tasks
            projects = mock_projects if projects is None else projects

        self.tasks = tasks
        self.projects = projects

        self._build_ui()
        self.refresh_table()

    def _build_ui(self):
        self.setStyleSheet("""
            QWidget {
                color: #F1F5F9;
                font-family: Segoe UI;
                font-size: 10pt;
            }

            QLineEdit, QComboBox, QDateEdit {
                background: #081B31;
                color: #F1F5F9;
                border: 2px solid #2C5B80;
                border-radius: 7px;
                padding: 8px;
            }

            QPushButton {
                background: #10243D;
                color: #DCEBFA;
                border: 2px solid #2C5B80;
                border-radius: 8px;
                padding: 8px 12px;
            }

            QPushButton:hover {
                background: #2C5B80;
                border-color: #20C9D8;
            }

            QPushButton#Primary {
                background: #2583E8;
                color: white;
                border-color: #2583E8;
            }

            QTableWidget {
                background: #081B31;
                alternate-background-color: #0B213A;
                color: #E7F0FA;
                border: 2px solid #2C5B80;
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

            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        heading = QHBoxLayout()
        title_box = QVBoxLayout()

        title = QLabel("Projects & Tasks")
        title.setStyleSheet("font-size: 22pt; font-weight: 700;")

        subtitle = QLabel(
            "Manage your projects and keep track of all tasks."
        )
        subtitle.setStyleSheet("color: #94A3B8;")

        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        heading.addLayout(title_box)
        heading.addStretch()

        add_button = QPushButton("+  Add Task")
        add_button.setObjectName("Primary")
        add_button.clicked.connect(self.add_task)
        heading.addWidget(add_button)

        layout.addLayout(heading)

        filter_row = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by task or project..."
        )
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

        filter_row.addWidget(self.search_input, 3)
        filter_row.addWidget(self.project_filter, 1)
        filter_row.addWidget(self.status_filter, 1)
        filter_row.addWidget(clear_button)

        layout.addLayout(filter_row)

        self.tasks_table = QTableWidget(0, 8)
        self.tasks_table.setHorizontalHeaderLabels([
            "Task Name",
            "Project",
            "Status",
            "Priority",
            "Due Date",
            "Dependencies",
            "Dependency Status",
            "Actions",
        ])

        self.tasks_table.setAlternatingRowColors(True)
        self.tasks_table.setShowGrid(True)
        self.tasks_table.verticalHeader().setVisible(False)
        self.tasks_table.verticalHeader().setDefaultSectionSize(44)
        self.tasks_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tasks_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.tasks_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout.addWidget(self.tasks_table, 1)

    def get_blockers(self, task):
        if task["status"] == "Completed":
            return []

        tasks_by_id = {
            item["id"]: item
            for item in self.tasks
        }

        blockers = []

        for dependency_id in task.get("dependencies", []):
            dependency = tasks_by_id.get(dependency_id)

            if dependency is None:
                blockers.append(f"Missing task #{dependency_id}")
            elif dependency["status"] != "Completed":
                blockers.append(dependency["name"])

        return blockers

    def refresh_table(self):
        search = self.search_input.text().strip().casefold()
        selected_project = self.project_filter.currentText()
        selected_status = self.status_filter.currentText()

        visible_tasks = []

        for task in self.tasks:
            if search and (
                search not in task["name"].casefold()
                and search not in task["project"].casefold()
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

        self.tasks_table.setRowCount(len(visible_tasks))

        for row, task in enumerate(visible_tasks):
            tasks_by_id = {
                item["id"]: item
                for item in self.tasks
            }

            dependency_names = []

            for dependency_id in task.get("dependencies", []):
                dependency = tasks_by_id.get(dependency_id)
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

                self.tasks_table.setItem(row, column, item)

            blockers = self.get_blockers(task)

            badge = QTableWidgetItem("Blocked" if blockers else "—")
            badge.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if blockers:
                badge.setForeground(QColor("#FFFFFF"))
                badge.setBackground(QColor(BLOCKED_COLOR))
                badge.setToolTip(
                    "Blocked: waiting for " + ", ".join(blockers)
                )
            else:
                badge.setToolTip(
                    "This task has no unfinished dependencies."
                )

            self.tasks_table.setItem(row, 6, badge)

            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(3, 2, 3, 2)

            done_checkbox = QCheckBox()
            done_checkbox.setToolTip("Mark task as completed")
            done_checkbox.setChecked(task["status"] == "Completed")
            done_checkbox.toggled.connect(
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

            actions_layout.addWidget(done_checkbox)
            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)

            self.tasks_table.setCellWidget(row, 7, actions)

    def dependencies_create_cycle(self, task_id, proposed_dependencies):
        """يتحقق إذا كانت الاعتماديات الجديدة ستنشئ دورة."""
        graph = {
            task["id"]: list(task.get("dependencies", []))
            for task in self.tasks
        }
        graph[task_id] = list(proposed_dependencies)

        visiting = set()
        visited = set()

        def visit(node):
            if node in visiting:
                return True

            if node in visited:
                return False

            visiting.add(node)

            for dependency_id in graph.get(node, []):
                if dependency_id in graph and visit(dependency_id):
                    return True

            visiting.remove(node)
            visited.add(node)
            return False

        return any(
            visit(node)
            for node in graph
            if node not in visited
        )

    def add_task(self):
        dialog = TaskFormDialog(
            self.projects,
            self.tasks,
            parent=self,
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        data = dialog.get_data()
        data["id"] = max(
            (task["id"] for task in self.tasks),
            default=0,
        ) + 1

        if self.dependencies_create_cycle(
            data["id"],
            data["dependencies"],
        ):
            QMessageBox.warning(
                self,
                "Invalid dependencies",
                "These dependencies create a cycle. "
                "Please choose another dependency.",
            )
            return

        self.tasks.append(data)
        self._tasks_updated()

    def edit_task(self, task_id):
        task = next(
            (item for item in self.tasks if item["id"] == task_id),
            None,
        )
        if task is None:
            return

        dialog = TaskFormDialog(
            self.projects,
            self.tasks,
            current_task=task,
            parent=self,
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        data = dialog.get_data()

        if task_id in data["dependencies"]:
            QMessageBox.warning(
                self,
                "Invalid dependency",
                "A task cannot depend on itself.",
            )
            return

        if self.dependencies_create_cycle(
            task_id,
            data["dependencies"],
        ):
            QMessageBox.warning(
                self,
                "Invalid dependencies",
                "These dependencies create a cycle. "
                "Please choose another dependency.",
            )
            return

        task.update(data)
        self._tasks_updated()

    def set_task_completed(self, task_id, completed):
        task = next(
            (item for item in self.tasks if item["id"] == task_id),
            None,
        )
        if task is None:
            return

        task["status"] = "Completed" if completed else "Not Started"
        self._tasks_updated()

    def delete_task(self, task_id):
        task = next(
            (item for item in self.tasks if item["id"] == task_id),
            None,
        )
        if task is None:
            return

        answer = QMessageBox.question(
            self,
            "Delete task",
            f"Are you sure you want to delete '{task['name']}'?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        self.tasks = [
            item for item in self.tasks
            if item["id"] != task_id
        ]

        for item in self.tasks:
            item["dependencies"] = [
                dependency_id
                for dependency_id in item.get("dependencies", [])
                if dependency_id != task_id
            ]

        self._tasks_updated()

    def clear_filters(self):
        self.search_input.clear()
        self.project_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.refresh_table()

    def _tasks_updated(self):
        self.refresh_table()
        self.tasks_changed.emit(self.tasks)