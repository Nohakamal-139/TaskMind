import sys
import re
import hashlib
import hmac
import json
import secrets
from datetime import date, timedelta
from pathlib import Path
from app.services.task_service import TaskService
from app.ui.s1_dashboard import DashboardScreen  
from app.ui.s2_tasks import ProjectsTasksScreen         
from app.ui.s3_priority import PriorityPage
from app.ui.s4_analytics import AnalyticsPage

from PySide6.QtCore import Qt, QDate, QSettings, QStringListModel, QRectF
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QPen, QPainterPath


def load_mock_data():
    """Return starter projects and an empty task list for this prototype."""
    projects = [
        "AI Assistant",
        "Web Platform",
        "Mobile App",
        "Task Manager",
        "Final Project",
    ]
    return [], projects

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, QDialog,
    QFormLayout, QDateEdit, QListWidget, QListWidgetItem, QMessageBox, QCompleter, QMenu,
    QAbstractItemView, QSpacerItem, QSizePolicy, QCheckBox, QScrollArea
)




APP_STYLE = """
QMainWindow, QWidget {
    background-color: #071426;
    color: #F1F5F9;
    font-family: Segoe UI;
    font-size: 10pt;
}
QLabel {
    background-color: transparent;
}
QFrame#Sidebar {
    background-color: #06101F;
    border-right: 1px solid #12365A;
}
QFrame#Panel {
    background-color: #10243D;
    border: 2px solid #2C5B80;
    border-radius: 12px;
}
QFrame#KpiCard {
    background-color: #2C5B80;
    border: 2px solid #2C5B80;
    border-radius: 12px;
}
QFrame#KpiCard QLabel { background: transparent; }
QFrame#DoNextHeader {
    background-color: #2C5B80;
    border-radius: 8px;
}
QLabel#Logo {
    color: #20C9D8;
    font-size: 19pt;
    font-weight: 800;
}
QLabel#Muted {
    color: #94A3B8;
}
QLabel#PageTitle {
    font-size: 22pt;
    font-weight: 700;
    color: #F1F5F9;
}
QLabel#KpiNumber {
    font-size: 23pt;
    font-weight: 800;
    color: #F1F5F9;
}
QPushButton {
    background-color: #10243D;
    color: #DCEBFA;
    border: 2px solid #2C5B80;
    border-radius: 8px;
    padding: 9px 13px;
}
QPushButton:hover {
    background-color: #2C5B80;
    border-color: #20C9D8;
}
QPushButton#NavButton {
    text-align: left;
    padding: 12px;
    border: none;
    background: transparent;
    color: #B9CBE0;
}
QPushButton#NavButton:checked {
    background-color: #0B3765;
    color: #20C9D8;
    border: 1px solid #2583E8;
}
QPushButton#Primary {
    background-color: #2583E8;
    color: white;
    border: 1px solid #2583E8;
    font-weight: 700;
}
QPushButton#Primary:hover {
    background-color: #176CC5;
}
QLineEdit, QComboBox, QDateEdit {
    background-color: #081B31;
    color: #F1F5F9;
    border: 2px solid #2C5B80;
    border-radius: 7px;
    padding: 8px;
    min-height: 20px;
}
QComboBox QAbstractItemView {
    background-color: #10243D;
    color: #F1F5F9;
    selection-background-color: #2583E8;
}
QTableWidget {
    background-color: #081B31;
    alternate-background-color: #0B213A;
    color: #E7F0FA;
    border: 2px solid #2C5B80;
    border-radius: 9px;
    gridline-color: #2C5B80;
    selection-background-color: #164A78;
    selection-color: white;
}
QHeaderView::section {
    background-color: #10243D;
    color: #8FCBFF;
    border: none;
    border-bottom: 1px solid #2C5B80;
    padding: 10px 6px;
    font-weight: 700;
}
QListWidget {
    background-color: #081B31;
    border: 2px solid #2C5B80;
    border-radius: 7px;
    padding: 5px;
}
QDialog {
    background-color: #071426;
}
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator { width: 18px; height: 18px; }
"""


LIGHT_STYLE = APP_STYLE + """
QMainWindow, QWidget { background-color: #F3F6FB; color: #172033; }
QFrame#Sidebar { background-color: #FFFFFF; border-right: 1px solid #D9E2EF; }
QFrame#Panel { background-color: #FFFFFF; border-color: #DCE9F5; }
QFrame#KpiCard { background-color: #DCE9F5; border-color: #DCE9F5; }
QFrame#KpiCard QLabel { background: transparent; }
QFrame#DoNextHeader { background-color: #DCE9F5; border-radius: 8px; }
QLabel#Muted { color: #667085; }
QLabel#PageTitle, QLabel#KpiNumber { color: #1C2B44; }
QPushButton { background-color: #FFFFFF; color: #24344D; border-color: #DCE9F5; }
QPushButton:hover { background-color: #EAF3FF; border-color: #2583E8; }
QPushButton#NavButton { background: transparent; color: #41546E; }
QPushButton#NavButton:checked { background-color: #EAF3FF; color: #1478D4; border: 1px solid #2583E8; }
QLineEdit, QComboBox, QDateEdit { background-color: #FFFFFF; color: #1F2D3D; border-color: #DCE9F5; }
QComboBox QAbstractItemView { background-color: #FFFFFF; color: #1F2D3D; selection-background-color: #DCEEFF; }
QTableWidget { background-color: #FFFFFF; alternate-background-color: #F4F8FD; color: #24344D; border-color: #DCE9F5; gridline-color: #DCE9F5; selection-background-color: #DCEEFF; selection-color: #172033; }
QHeaderView::section { background-color: #EAF0F8; color: #1976D2; border-bottom: 1px solid #DCE9F5; }
QListWidget { background-color: #FFFFFF; border-color: #DCE9F5; }
QDialog { background-color: #F3F6FB; }
"""
STATUS_COLORS = {
    "Completed": "#16D6C1",
    "In Progress": "#2583E8",
    "Pending": "#F59E0B",
    "Overdue": "#EF4444",
    "Not Started": "#64748B",
}
PRIORITY_COLORS = {
    "High": "#EF4444",
    "Medium": "#F59E0B",
    "Low": "#16D6C1",
}



class TaskDialog(QDialog):

    def __init__(self, projects, tasks, current_task=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add / Edit Task")
        self.setMinimumWidth(430)
        self.tasks = tasks
        self.current_task = current_task

        root = QVBoxLayout(self)
        title = QLabel("Edit Task" if current_task else "Add New Task")
        title.setObjectName("PageTitle")
        root.addWidget(title)

        form = QFormLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter task name")
        self.project_input = QComboBox()
        self.project_input.addItems(projects)
        self.priority_input = QComboBox()
        self.priority_input.addItems(["High", "Medium", "Low"])
        self.status_input = QComboBox()
        self.status_input.addItems(
            ["Not Started", "Pending", "In Progress", "Completed", "Overdue"]
        )
        self.due_input = QDateEdit()
        self.due_input.setCalendarPopup(True)
        self.due_input.setDisplayFormat("yyyy-MM-dd")
        self.due_input.setDate(QDate.currentDate().addDays(2))

        form.addRow("Task name *", self.name_input)
        form.addRow("Project *", self.project_input)
        form.addRow("Priority", self.priority_input)
        form.addRow("Status", self.status_input)
        form.addRow("Due date", self.due_input)
        root.addLayout(form)

        dep_label = QLabel("Dependencies (optional)")
        dep_label.setStyleSheet("font-weight: 700; margin-top: 8px;")
        root.addWidget(dep_label)

        self.dependencies_list = QListWidget()
        current_id = current_task["id"] if current_task else None
        current_dependencies = set(current_task["dependencies"]) if current_task else set()

        for task in tasks:
            if task["id"] == current_id:
                continue
            item = QListWidgetItem(task["name"])
            item.setData(Qt.ItemDataRole.UserRole, task["id"])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked if task["id"] in current_dependencies
                else Qt.CheckState.Unchecked
            )
            self.dependencies_list.addItem(item)
        root.addWidget(self.dependencies_list)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Cancel")
        save = QPushButton("Save")
        save.setObjectName("Primary")
        cancel.clicked.connect(self.reject)
        save.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        root.addLayout(buttons)

        if current_task:
            self.name_input.setText(current_task["name"])
            self.project_input.setCurrentText(current_task["project"])
            self.priority_input.setCurrentText(current_task["priority"])
            self.status_input.setCurrentText(current_task["status"])
            parsed = QDate.fromString(current_task["due"], "yyyy-MM-dd")
            if parsed.isValid():
                self.due_input.setDate(parsed)

    def get_data(self):
        dependencies = []
        for i in range(self.dependencies_list.count()):
            item = self.dependencies_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                dependencies.append(item.data(Qt.ItemDataRole.UserRole))
        return {
            "name": self.name_input.text().strip(),
            "project": self.project_input.currentText(),
            "priority": self.priority_input.currentText(),
            "status": self.status_input.currentText(),
            "due": self.due_input.date().toString("yyyy-MM-dd"),
            "dependencies": dependencies
        }


class DonutChart(QWidget):
    

    COLORS = {
        "Completed": "#16D6C1",
        "In Progress": "#2583E8",
        "Pending": "#F59E0B",
        "Overdue": "#EF4444",
        "Not Started": "#64748B",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(220, 210)
        self.counts = {}
        self.total = 0
        self.light_theme = False

    def set_counts(self, counts):
        self.counts = {
            label: max(0, int(count or 0))
            for label, count in counts.items()
            if label in self.COLORS
        }
        self.total = sum(self.counts.values())
        self.update()

    def set_theme(self, theme):
        self.light_theme = theme == "light"
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        side = min(self.width(), self.height()) - 38
        rect = QRectF((self.width() - side) / 2, (self.height() - side) / 2,
                      side, side)
        track_color = "#DCE9F5" if self.light_theme else "#2C5B80"
        pen = QPen(QColor(track_color), 18)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)
        painter.drawArc(rect, 0, 360 * 16)

        if self.total:
            start = 90 * 16
            remaining_angle = 360 * 16
            visible_segments = [
                (label, count) for label, count in self.counts.items() if count
            ]
            for index, (label, count) in enumerate(visible_segments):
                if index == len(visible_segments) - 1:
                    span = remaining_angle
                else:
                    span = round(360 * 16 * count / self.total)
                    span = min(span, remaining_angle)
                pen.setColor(QColor(self.COLORS[label]))
                painter.setPen(pen)
                painter.drawArc(rect, start, -span)
                start -= span
                remaining_angle -= span

        completed = self.counts.get("Completed", 0)
        completion_rate = round(completed * 100 / self.total) if self.total else 0
        main_text = "#1C2B44" if self.light_theme else "#F1F5F9"
        muted_text = "#667085" if self.light_theme else "#94A3B8"
        painter.setPen(QColor(main_text))
        painter.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{completion_rate}%")
        painter.setPen(QColor(muted_text))
        painter.setFont(QFont("Segoe UI", 9))
        center = QRectF(0, self.height() / 2 + 20, self.width(), 25)
        painter.drawText(center, Qt.AlignmentFlag.AlignHCenter, "completed")


class CompletionTrendChart(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(235)
        self.daily = []
        self.light_theme = False

    def set_daily(self, daily):
        self.daily = daily
        self.update()

    def set_theme(self, theme):
        self.light_theme = theme == "light"
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        left, right, top, bottom = 42, 14, 18, 32
        plot = QRectF(left, top, max(1, self.width() - left - right),
                      max(1, self.height() - top - bottom))
        max_count = max([value for _label, value in self.daily] or [0])
        axis_max = max(5, max_count)
        tick_step = 1 if axis_max <= 8 else max(1, (axis_max + 4) // 5)
        tick_values = list(range(0, axis_max + 1, tick_step))
        if tick_values[-1] != axis_max:
            tick_values.append(axis_max)

        painter.setFont(QFont("Segoe UI", 9))
        grid_color = "#B8C8DB" if self.light_theme else "#2C5B80"
        axis_text = "#2583E8" if self.light_theme else "#8FCBFF"
        for tick_value in tick_values:
            y = plot.bottom() - plot.height() * tick_value / axis_max
            painter.setPen(QPen(QColor(grid_color), 1, Qt.PenStyle.DotLine))
            painter.drawLine(int(plot.left()), int(y), int(plot.right()), int(y))
            painter.setPen(QColor(axis_text))
            painter.drawText(QRectF(0, y - 8, left - 8, 18),
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                             str(tick_value))

        points = []
        if self.daily:
            step = plot.width() / max(1, len(self.daily) - 1)
            for index, (_label, value) in enumerate(self.daily):
                x = plot.left() + index * step
                y = plot.bottom() - (value / axis_max) * plot.height()
                points.append((x, y))
            if len(points) > 1:
                area = QPainterPath()
                area.moveTo(points[0][0], plot.bottom())
                area.lineTo(points[0][0], points[0][1])
                for x, y in points[1:]:
                    area.lineTo(x, y)
                area.lineTo(points[-1][0], plot.bottom())
                area.closeSubpath()
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(37, 131, 232, 55))
                painter.drawPath(area)

                pen = QPen(QColor("#20C9D8"), 3)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                for first, second in zip(points, points[1:]):
                    painter.drawLine(int(first[0]), int(first[1]),
                                     int(second[0]), int(second[1]))
            painter.setPen(QPen(QColor("#20C9D8"), 2))
            painter.setBrush(QColor("#20C9D8"))
            for x, y in points:
                painter.drawEllipse(QRectF(x - 3, y - 3, 6, 6))
            date_text = "#667085" if self.light_theme else "#94A3B8"
            painter.setPen(QColor(date_text))
            for index, (label, _value) in enumerate(self.daily):
                x = points[index][0]
                painter.drawText(QRectF(x - 23, plot.bottom() + 7, 46, 18),
                                 Qt.AlignmentFlag.AlignHCenter, label)
        if not any(value for _label, value in self.daily):
            empty_text = "#667085" if self.light_theme else "#94A3B8"
            painter.setPen(QColor(empty_text))
            painter.drawText(plot, Qt.AlignmentFlag.AlignCenter,
                             "Completed tasks will appear here")


class TrendArrowIcon(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 18)
        self.color = QColor("#8FCBFF")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_theme(self, theme):
        self.color = QColor("#2583E8" if theme == "light" else "#8FCBFF")
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(self.color, 1.8, Qt.PenStyle.SolidLine,
                   Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        trend = QPainterPath()
        trend.moveTo(1, 16)
        trend.lineTo(5, 12)
        trend.lineTo(8, 14)
        trend.lineTo(12, 8)
        trend.lineTo(15, 10)
        trend.lineTo(18, 4)
        painter.drawPath(trend)
        painter.drawLine(18, 4, 14, 4)
        painter.drawLine(18, 4, 18, 8)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Mind")
        screen = QApplication.primaryScreen()
        available = screen.availableGeometry().size() if screen else None
        if available:
            self.setMinimumSize(min(900, available.width()), min(600, available.height()))
            self.resize(min(1380, available.width()), min(850, available.height()))
        else:
            self.resize(1380, 850)
            self.setMinimumSize(900, 600)
        self.settings = QSettings("TaskMind", "TaskMind")
        self.current_theme = self.settings.value("theme", "dark", type=str)
        try:
            self.accounts = json.loads(self.settings.value("accounts", "{}", type=str))
        except (TypeError, json.JSONDecodeError):
            self.accounts = {}
        saved_user = self.settings.value("active_user", "", type=str)
        self.current_user = saved_user if saved_user in self.accounts else None
        self.pending_add_after_login = False
        self.page_before_auth = 0
         #Backend 
        self.service = TaskService()
        self.projects = self.service.get_all_projects()
        self.tasks = self.service.get_all_tasks()
        self.next_id = max((task["id"] for task in self.tasks), default=0) + 1

        self.nav_buttons = []
        self.stack = QStackedWidget()
        self.workspace = QWidget()
        main_layout = QHBoxLayout(self.workspace)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.build_sidebar())
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(22, 18, 22, 20)
        content_layout.setSpacing(14)
        content_layout.addWidget(self.build_topbar())
        content_layout.addWidget(self.stack, 1)
        main_layout.addWidget(content, 1)

        self.dashboard_page = self.build_dashboard()
        self.tasks_page = self.build_tasks_page()
        self.priority_page = self.build_priority_page()
        self.analytics_page = self.build_analytics_page()
        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.tasks_page)
        self.stack.addWidget(self.priority_page)
        self.stack.addWidget(self.analytics_page)
        self.nav_buttons[0].setChecked(True)

        self.root_stack = QStackedWidget()
        self.auth_theme_buttons = []
        self.login_page = self.build_auth_page(register=False)
        self.register_page = self.build_auth_page(register=True)
        self.root_stack.addWidget(self.login_page)
        self.root_stack.addWidget(self.register_page)
        self.root_stack.addWidget(self.workspace)
        self.setCentralWidget(self.root_stack)
        self.update_profile_display()
        self.apply_theme()
        self.refresh_all()
        self.root_stack.setCurrentWidget(self.workspace)

    def build_auth_page(self, register=False):
        page = QWidget()
        outer = QVBoxLayout(page)
        theme_row = QHBoxLayout()
        theme_row.addStretch()
        auth_theme = QPushButton()
        auth_theme.setFixedSize(40, 40)
        auth_theme.clicked.connect(self.toggle_theme)
        self.auth_theme_buttons.append(auth_theme)
        theme_row.addWidget(auth_theme)
        outer.addLayout(theme_row)
        outer.addStretch()

        card = QFrame()
        card.setObjectName("Panel")
        card.setMaximumWidth(470)
        form_layout = QVBoxLayout(card)
        form_layout.setContentsMargins(30, 25, 30, 25)
        form_layout.setSpacing(13)
        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(str(Path(__file__).resolve().parent.parent / "assets" / "task_mind_logo-removebg-preview.png"))
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(190, 165, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            logo.setText("TASK MIND")
            logo.setObjectName("Logo")
        form_layout.addWidget(logo)
        title = QLabel("Create Your Account" if register else "Welcome Back")
        title.setObjectName("PageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle = QLabel("Create an account to start managing your tasks." if register else "Sign in to continue to your tasks.")
        subtitle.setObjectName("Muted")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if register:
            self.register_subtitle = subtitle
        else:
            self.login_subtitle = subtitle
        form_layout.addWidget(title)
        form_layout.addWidget(subtitle)

        if register:
            self.register_name = QLineEdit(); self.register_name.setPlaceholderText("Full name")
            self.register_email = QLineEdit(); self.register_email.setPlaceholderText("Email address")
            self.register_password = QLineEdit(); self.register_password.setPlaceholderText("Password (at least 8 characters)"); self.register_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.register_confirm = QLineEdit(); self.register_confirm.setPlaceholderText("Confirm password"); self.register_confirm.setEchoMode(QLineEdit.EchoMode.Password)
            self.register_confirm.returnPressed.connect(self.register_user)
            for field in [self.register_name, self.register_email, self.register_password, self.register_confirm]:
                form_layout.addWidget(field)
            submit = QPushButton("Create Account"); submit.setObjectName("Primary"); submit.clicked.connect(self.register_user)
            form_layout.addWidget(submit)
            back = QPushButton("Already have an account? Sign in")
            back.clicked.connect(lambda: self.root_stack.setCurrentWidget(self.login_page))
            form_layout.addWidget(back)
        else:
            self.login_email = QLineEdit(); self.login_email.setPlaceholderText("Email address")
            self.login_password = QLineEdit(); self.login_password.setPlaceholderText("Password"); self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.login_password.returnPressed.connect(self.login_user)
            form_layout.addWidget(self.login_email); form_layout.addWidget(self.login_password)
            submit = QPushButton("Sign In"); submit.setObjectName("Primary"); submit.clicked.connect(self.login_user)
            form_layout.addWidget(submit)
            create = QPushButton("New here? Create an account")
            create.clicked.connect(lambda: self.root_stack.setCurrentWidget(self.register_page))
            form_layout.addWidget(create)
            browse = QPushButton("Continue browsing without signing in")
            browse.clicked.connect(self.return_to_workspace)
            form_layout.addWidget(browse)
        note = QLabel("Accounts are stored locally in this prototype.")
        note.setObjectName("Muted"); note.setAlignment(Qt.AlignmentFlag.AlignCenter); form_layout.addWidget(note)
        outer.addWidget(card, 0, Qt.AlignmentFlag.AlignHCenter)
        outer.addStretch()
        return page

    def save_accounts(self):
        self.settings.setValue("accounts", json.dumps(self.accounts))
        self.settings.sync()

    def register_user(self):
        name = self.register_name.text().strip()
        email = self.register_email.text().strip().lower()
        password = self.register_password.text()
        if not name:
            QMessageBox.warning(self, "Name required", "Please enter your name."); return
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            QMessageBox.warning(self, "Invalid email", "Please enter a valid email address."); return
        if email in self.accounts:
            QMessageBox.warning(self, "Account already exists", "Sign in with this email instead."); return
        if len(password) < 8:
            QMessageBox.warning(self, "Password too short", "Use at least 8 characters."); return
        if password != self.register_confirm.text():
            QMessageBox.warning(self, "Passwords do not match", "Please enter the same password twice."); return
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000).hex()
        self.accounts[email] = {"name": name, "salt": salt.hex(), "password_hash": digest}
        self.save_accounts()
        self.login_success(email)

    def login_user(self):
        email = self.login_email.text().strip().lower()
        account = self.accounts.get(email)
        if not account:
            QMessageBox.warning(self, "Account not found", "Create an account first or check the email."); return
        salt = bytes.fromhex(account["salt"])
        supplied = hashlib.pbkdf2_hmac("sha256", self.login_password.text().encode("utf-8"), salt, 200_000).hex()
        if not hmac.compare_digest(supplied, account["password_hash"]):
            QMessageBox.warning(self, "Incorrect password", "Please check your password and try again."); return
        self.login_success(email)

    def login_success(self, email):
        self.current_user = email
        self.settings.setValue("active_user", email); self.settings.sync()
        self.update_profile_display()
        self.root_stack.setCurrentWidget(self.workspace)
        if self.pending_add_after_login:
            self.pending_add_after_login = False
            self.change_page(1)
            self.add_task()
        else:
            self.change_page(self.page_before_auth)

    def profile_initial(self):
        account = self.accounts.get(self.current_user, {}) if self.current_user else {}
        name = account.get("name", "")
        return name.strip()[0].upper() if name.strip() else "👤"

    def update_profile_display(self):
        account = self.accounts.get(self.current_user, {}) if self.current_user else {}
        name = account.get("name", "")

        if hasattr(self, "user_button"):
            self.user_button.setText(self.profile_initial())
            if self.current_user:
                self.user_button.setToolTip(f"{name} ({self.current_user}) — Account options")
            else:
                self.user_button.setToolTip("Create an account or sign in")

        if hasattr(self, "welcome_label"):
            greeting = f"☀   Good Morning, {name}!" if name else "☀   Good Morning!"
            self.welcome_label.setText(greeting + "\n      Stay focused. Get things done.")

    def show_account_menu(self):
        if not self.current_user:
            self.page_before_auth = self.stack.currentIndex()
            if self.accounts:
                self.login_subtitle.setText("Sign in or create an account to manage your profile.")
                self.root_stack.setCurrentWidget(self.login_page)
            else:
                self.register_subtitle.setText("Create your first account to manage your profile.")
                self.root_stack.setCurrentWidget(self.register_page)
            return

        account = self.accounts[self.current_user]
        menu = QMenu(self)
        identity = menu.addAction(f"{account['name']} · {self.current_user}")
        identity.setEnabled(False)
        menu.addSeparator()
        menu.addAction("Sign Out").triggered.connect(self.logout_user)
        menu.exec(self.user_button.mapToGlobal(self.user_button.rect().bottomLeft()))

    def logout_user(self):
        self.current_user = None
        self.settings.remove("active_user")
        self.settings.sync()
        self.login_password.clear()
        self.root_stack.setCurrentWidget(self.workspace)
        self.update_profile_display()

    def return_to_workspace(self):
        self.pending_add_after_login = False
        self.root_stack.setCurrentWidget(self.workspace)
        self.change_page(self.page_before_auth)
    def apply_theme(self):
        app = QApplication.instance()
        if app:
            app.setStyleSheet(LIGHT_STYLE if self.current_theme == "light" else APP_STYLE)
        buttons = list(getattr(self, "auth_theme_buttons", []))
        if hasattr(self, "theme_button"):
            buttons.append(self.theme_button)
        for button in buttons:
            button.setText("☾" if self.current_theme == "light" else "☀")
            button.setToolTip("Switch to Night Mode" if self.current_theme == "light" else "Switch to Day Mode")
        if hasattr(self, "tagline_arrow"):
            self.tagline_arrow.set_theme(self.current_theme)
        if hasattr(self, "analytics_donut"):
            self.refresh_analytics()

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.settings.setValue("theme", self.current_theme); self.settings.sync()
        self.apply_theme()
    def build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(215)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 22, 14, 18)
        layout.setSpacing(12)

        logo_icon = QLabel()
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_icon.setFixedHeight(165)
        logo_path = Path(__file__).resolve().parent.parent / "assets" / "task_mind_logo-removebg-preview.png"
        
        from PySide6.QtGui import QImage, QColor
        image = QImage(str(logo_path)).convertToFormat(QImage.Format.Format_ARGB32)
        for x in range(image.width()):
            for y in range(image.height()):
                color = QColor(image.pixel(x, y))
                if color.red() > 240 and color.green() > 240 and color.blue() > 240:
                    image.setPixelColor(x, y, QColor(0, 0, 0, 0)) # شفاف
        
        logo_pixmap = QPixmap.fromImage(image)
        if not logo_pixmap.isNull():
            logo_icon.setPixmap(logo_pixmap.scaled(
                185, 160, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            logo_icon.setText("TASK MIND")
            logo_icon.setObjectName("Logo")
        layout.addWidget(logo_icon)
        layout.addSpacing(20)

        labels = [
            ("⌂   Dashboard", 0),
            ("▤   Projects & Tasks", 1),
            ("◎   Priority Board", 2),
            ("▥   Progress Analytics", 3),
        ]
        for label, index in labels:
            button = QPushButton(label)
            button.setObjectName("NavButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked, i=index: self.change_page(i))
            self.nav_buttons.append(button)
            layout.addWidget(button)

        layout.addStretch()
        tagline_row = QWidget()
        tagline_layout = QHBoxLayout(tagline_row)
        tagline_layout.setContentsMargins(2, 0, 0, 0)
        tagline_layout.setSpacing(3)
        arrow = TrendArrowIcon()
        self.tagline_arrow = arrow
        tagline = QLabel("Smarter Tasks\nBrighter Future")
        tagline.setObjectName("Muted")
        tagline_layout.addWidget(arrow, 0, Qt.AlignmentFlag.AlignTop)
        tagline_layout.addWidget(tagline, 0, Qt.AlignmentFlag.AlignTop)
        tagline_layout.addStretch()
        layout.addWidget(tagline_row)
        return sidebar

    def build_topbar(self):
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        self.global_search = QLineEdit()
        self.global_search.setPlaceholderText("Search all tasks and projects...")
        self.global_search.setMaximumWidth(320)
        self.global_search.setClearButtonEnabled(True)
        self.search_model = QStringListModel(self)
        self.search_completer = QCompleter(self.search_model, self)
        self.search_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.search_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.global_search.setCompleter(self.search_completer)
        self.global_search.returnPressed.connect(self.search_everywhere)
        self.search_completer.activated[str].connect(self.search_everywhere)
        layout.addWidget(self.global_search)
        self.theme_button = QPushButton()
        self.theme_button.setFixedSize(40, 40)
        self.theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_button)
        bell = QLabel("  ♧  ")
        bell.setStyleSheet("color: #8FCBFF; font-size: 16pt;")
        layout.addWidget(bell)
        self.user_button = QPushButton("👤")
        self.user_button.setFixedSize(40, 40)
        self.user_button.setStyleSheet(
            "background:#2583E8; border-radius:20px; font-weight:700; color:white;"
        )
        self.user_button.clicked.connect(self.show_account_menu)
        layout.addWidget(self.user_button)
        return bar

    def build_dashboard(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        self.welcome_label = QLabel("☀   Good Morning!\n      Stay focused. Get things done.")
        self.welcome_label.setStyleSheet("font-size: 16pt; font-weight:700; padding: 7px;")
        layout.addWidget(self.welcome_label)

        cards_layout = QGridLayout()
        cards_layout.setSpacing(12)
        self.kpi_values = {}
        kpis = [
            ("Total Tasks", "total", "#2583E8"),
            ("Completed Tasks", "completed", "#16D6C1"),
            ("Overdue Tasks", "overdue", "#EF4444"),
            ("Due This Week", "week", "#F59E0B"),
        ]
        for col, (title, key, color) in enumerate(kpis):
            card = QFrame()
            card.setObjectName("KpiCard")
            card_layout = QVBoxLayout(card)
            name = QLabel(title)
            name.setStyleSheet(f"color:{color}; font-weight:700;")
            value = QLabel("0")
            value.setObjectName("KpiNumber")
            subtitle = QLabel("Task Mind overview")
            subtitle.setObjectName("Muted")
            card_layout.addWidget(name)
            card_layout.addWidget(value)
            card_layout.addWidget(subtitle)
            cards_layout.addWidget(card, 0, col)
            self.kpi_values[key] = value
        layout.addLayout(cards_layout)

        panel = QFrame()
        panel.setObjectName("Panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setSpacing(0)
        header_frame = QFrame()
        header_frame.setObjectName("DoNextHeader")
        heading_row = QHBoxLayout(header_frame)
        heading_row.setContentsMargins(10, 5, 10, 5)
        heading_icon = QLabel("☑")
        heading_icon.setStyleSheet("font-size:22pt; color:#20C9D8; font-weight:700; background:transparent; border:none;")
        heading_row.addWidget(heading_icon)
        heading = QLabel("Do Next")
        heading.setStyleSheet("font-size:16pt; font-weight:700; background:transparent; border:none; text-decoration:none;")
        helper = QLabel("Top 5 tasks you can start now")
        helper.setObjectName("Muted")
        helper.setStyleSheet("background:transparent; border:none;")
        heading_row.addWidget(heading)
        heading_row.addStretch()
        heading_row.addWidget(helper)
        panel_layout.addWidget(header_frame)

        self.do_next_table = QTableWidget(0, 4)
        self.do_next_table.setHorizontalHeaderLabels(
            ["Task Name", "Project", "Priority", "Due Date"]
        )
        self.style_table(self.do_next_table)
        self.do_next_table.setStyleSheet("border-top: none;")
        self.do_next_table.setMaximumHeight(300)
        panel_layout.addWidget(self.do_next_table)
        layout.addWidget(panel)
        layout.addStretch()
        return page

    def build_tasks_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        heading_row = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Projects & Tasks")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Manage your projects and keep track of all tasks.")
        subtitle.setObjectName("Muted")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        heading_row.addLayout(title_box)
        heading_row.addStretch()
        add_button = QPushButton("+  Add Task")
        add_button.setObjectName("Primary")
        add_button.clicked.connect(self.add_task)
        heading_row.addWidget(add_button)
        layout.addLayout(heading_row)

        filter_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter this task list...")
        self.search_input.textChanged.connect(self.refresh_tasks_table)
        self.project_filter = QComboBox()
        self.project_filter.addItems(["All Projects"] + self.projects)
        self.project_filter.currentTextChanged.connect(self.refresh_tasks_table)
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "All Statuses", "Not Started", "Pending", "In Progress", "Completed", "Overdue"
        ])
        self.status_filter.currentTextChanged.connect(self.refresh_tasks_table)
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_filters)
        filter_row.addWidget(self.search_input, 3)
        filter_row.addWidget(self.project_filter, 1)
        filter_row.addWidget(self.status_filter, 1)
        filter_row.addWidget(clear_button)
        layout.addLayout(filter_row)

        self.tasks_table = QTableWidget(0, 8)
        self.tasks_table.setHorizontalHeaderLabels([
            "Task Name", "Project", "Status", "Priority",
            "Due Date", "Dependencies", "Dependency Status", "Actions"
        ])
        self.style_table(self.tasks_table)
        layout.addWidget(self.tasks_table, 1)
        return page

    def build_priority_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
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
        self.priority_columns = {}
        self.priority_counts = {}
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
        return page

    def build_analytics_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        heading_row = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Progress Analytics")
        title.setObjectName("PageTitle")
        subtitle = QLabel("Understand task status and completion activity.")
        subtitle.setObjectName("Muted")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        heading_row.addLayout(title_box)
        heading_row.addStretch()
        self.analytics_period = QLabel("Last 7 days")
        self.analytics_period.setObjectName("Muted")
        heading_row.addWidget(self.analytics_period, 0, Qt.AlignmentFlag.AlignBottom)
        layout.addLayout(heading_row)

        charts = QGridLayout()
        charts.setSpacing(14)
        status_panel = QFrame()
        status_panel.setObjectName("Panel")
        status_layout = QVBoxLayout(status_panel)
        status_layout.setContentsMargins(16, 14, 16, 16)
        status_title = QLabel("Project Progress")
        status_title.setStyleSheet("font-size:13pt; font-weight:700;")
        status_layout.addWidget(status_title)
        status_content = QHBoxLayout()
        status_content.setSpacing(12)
        self.analytics_donut = DonutChart()
        status_content.addWidget(self.analytics_donut, 2)
        self.analytics_legend = QVBoxLayout()
        self.analytics_legend.setSpacing(11)
        status_content.addLayout(self.analytics_legend, 1)
        status_layout.addLayout(status_content, 1)

        trend_panel = QFrame()
        trend_panel.setObjectName("Panel")
        trend_layout = QVBoxLayout(trend_panel)
        trend_layout.setContentsMargins(16, 14, 16, 16)
        trend_title = QLabel("Tasks Completed Over Time")
        trend_title.setStyleSheet("font-size:13pt; font-weight:700;")
        trend_hint = QLabel("Daily completed tasks over the last 7 days")
        trend_hint.setObjectName("Muted")
        self.analytics_trend = CompletionTrendChart()
        trend_layout.addWidget(trend_title)
        trend_layout.addWidget(trend_hint)
        trend_layout.addWidget(self.analytics_trend, 1)
        charts.addWidget(status_panel, 0, 0)
        charts.addWidget(trend_panel, 0, 1)
        charts.setColumnStretch(0, 4)
        charts.setColumnStretch(1, 6)
        self.analytics_charts = charts
        self.analytics_status_panel = status_panel
        self.analytics_trend_panel = trend_panel
        self._analytics_compact_layout = None
        layout.addLayout(charts, 1)
        self._arrange_analytics_panels()
        return page

    def _arrange_analytics_panels(self):
        if not hasattr(self, "analytics_charts"):
            return
        compact = self.width() < 1050
        if compact == self._analytics_compact_layout:
            return
        self._analytics_compact_layout = compact
        self.analytics_charts.removeWidget(self.analytics_status_panel)
        self.analytics_charts.removeWidget(self.analytics_trend_panel)
        if compact:
            self.analytics_charts.addWidget(self.analytics_status_panel, 0, 0)
            self.analytics_charts.addWidget(self.analytics_trend_panel, 1, 0)
            self.analytics_charts.setColumnStretch(0, 1)
            self.analytics_charts.setRowStretch(0, 1)
            self.analytics_charts.setRowStretch(1, 1)
        else:
            self.analytics_charts.addWidget(self.analytics_status_panel, 0, 0)
            self.analytics_charts.addWidget(self.analytics_trend_panel, 0, 1)
            self.analytics_charts.setColumnStretch(0, 4)
            self.analytics_charts.setColumnStretch(1, 6)
            self.analytics_charts.setRowStretch(0, 1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._arrange_analytics_panels()

    def refresh_priority_board(self):
        if not hasattr(self, "priority_columns"):
            return
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
            tasks.sort(key=lambda task: (
                1 if task.get("status") == "Completed" else 0,
                task.get("due", "9999-12-31"),
                task.get("name", "").casefold(),
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
                edit_button.clicked.connect(
                    lambda checked=False, task_id=task["id"]: self.edit_task(task_id)
                )
                bottom.addWidget(due_label)
                bottom.addStretch()
                bottom.addWidget(edit_button)
                card_layout.addWidget(task_name)
                card_layout.addWidget(project)
                card_layout.addLayout(bottom)
                column.insertWidget(column.count(), card)
            column.addStretch()

    def _analytics_status_counts(self):
        counts = {"Completed": 0, "In Progress": 0, "Pending": 0,
                  "Overdue": 0, "Not Started": 0}
        today = date.today()
        for task in self.tasks:
            status = task.get("status", "Not Started")
            try:
                is_late = date.fromisoformat(task.get("due", "")) < today
            except (TypeError, ValueError):
                is_late = False
            if status == "Completed":
                counts["Completed"] += 1
            elif status == "Overdue" or is_late:
                counts["Overdue"] += 1
            elif status == "In Progress":
                counts["In Progress"] += 1
            elif status == "Pending":
                counts["Pending"] += 1
            else:
                counts["Not Started"] += 1
        return counts

    def refresh_analytics(self):
        if not hasattr(self, "analytics_donut"):
            return
        counts = self._analytics_status_counts()
        light_theme = self.current_theme == "light"
        self.analytics_donut.set_theme(self.current_theme)
        self.analytics_trend.set_theme(self.current_theme)
        self.analytics_donut.set_counts(counts)
        while self.analytics_legend.count():
            item = self.analytics_legend.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        for status in counts:
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(2, 3, 2, 3)
            marker = QLabel()
            marker.setFixedSize(10, 10)
            marker.setStyleSheet(
                f"background-color:{DonutChart.COLORS[status]}; border-radius:5px;"
            )
            name = QLabel(status)
            name_color = "#24344D" if light_theme else "#E7F0FA"
            name.setStyleSheet(f"color:{name_color}; font-weight:600;")
            row.addWidget(marker)
            row.addWidget(name)
            row.addStretch()
            self.analytics_legend.addWidget(row_widget)
        self.analytics_legend.addStretch()

        today = date.today()
        start = today - timedelta(days=6)
        daily_counts = {start + timedelta(days=index): 0 for index in range(7)}
        for task in self.tasks:
            if task.get("status") != "Completed":
                continue
            try:
                completed_on = date.fromisoformat(task.get("completed_on", ""))
            except (TypeError, ValueError):
                continue
            if completed_on in daily_counts:
                daily_counts[completed_on] += 1
        self.analytics_trend.set_daily([
            (day.strftime("%a"), count) for day, count in daily_counts.items()
        ])

    def build_placeholder(self, title_text, message):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addStretch()
        title = QLabel(title_text)
        title.setObjectName("PageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note = QLabel(message)
        note.setObjectName("Muted")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(note)
        layout.addStretch()
        return page

    def style_table(self, table):
        table.setAlternatingRowColors(True)
        table.setShowGrid(True)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setDefaultSectionSize(42)

    def refresh_search_suggestions(self):
        suggestions = set(self.projects)
        suggestions.update(task["name"] for task in self.tasks)
        self.search_model.setStringList(sorted(suggestions, key=str.casefold))

    def search_everywhere(self, selected_text=None):
        query = (selected_text or self.global_search.text()).strip()
        if not query:
            self.search_input.clear()
            self.project_filter.setCurrentIndex(0)
            self.status_filter.setCurrentIndex(0)
            self.change_page(1)
            return
        self.global_search.setText(query)
        self.project_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.search_input.setText(query)
        self.change_page(1)
        self.tasks_table.setFocus()
    def change_page(self, index):
        self.stack.setCurrentIndex(index)
        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == index)
        if index == 1:
            self.refresh_tasks_table()
        elif index == 2:
            self.refresh_priority_board()
        elif index == 3:
            self.refresh_analytics()

    def refresh_all(self):
        self.refresh_kpis()
        self.refresh_do_next()
        self.refresh_tasks_table()
        self.refresh_search_suggestions()
        self.refresh_priority_board()
        self.refresh_analytics()

    def refresh_kpis(self):
        today = date.today()
        week_end = today + timedelta(days=7)
        total = len(self.tasks)
        completed = sum(t["status"] == "Completed" for t in self.tasks)
        overdue = sum(
            t["status"] == "Overdue" or
            (t["status"] != "Completed" and date.fromisoformat(t["due"]) < today)
            for t in self.tasks
        )
        due_week = sum(
            today <= date.fromisoformat(t["due"]) <= week_end and t["status"] != "Completed"
            for t in self.tasks
        )
        self.kpi_values["total"].setText(str(total))
        self.kpi_values["completed"].setText(str(completed))
        self.kpi_values["overdue"].setText(str(overdue))
        self.kpi_values["week"].setText(str(due_week))

    def get_unblocked_tasks(self):
        completed_ids = {t["id"] for t in self.tasks if t["status"] == "Completed"}
        available = []
        for task in self.tasks:
            if task["status"] in ("Completed", "Overdue"):
                continue
            if all(dep in completed_ids for dep in task["dependencies"]):
                available.append(task)
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        available.sort(key=lambda t: (priority_order[t["priority"]], t["due"]))
        return available[:5]

    def refresh_do_next(self):
        items = self.get_unblocked_tasks()
        self.do_next_table.setRowCount(len(items))
        for row, task in enumerate(items):
            values = [
                task["name"], task["project"], task["priority"], task["due"]
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col == 2:
                    item.setForeground(Qt.GlobalColor.white)
                    item.setBackground(__import__("PySide6.QtGui", fromlist=["QColor"]).QColor(
                        PRIORITY_COLORS.get(task["priority"], "#2583E8")
                    ))
                self.do_next_table.setItem(row, col, item)

    def get_blocking_dependencies(self, task):
        """Return dependency tasks that have not been completed yet."""
        task_by_id = {item["id"]: item for item in self.tasks}
        blockers = []
        for dependency_id in task.get("dependencies", []):
            dependency = task_by_id.get(dependency_id)
            if dependency is None:
                blockers.append(f"Missing task #{dependency_id}")
            elif dependency["status"] != "Completed":
                blockers.append(dependency["name"])
        return blockers

    def refresh_tasks_table(self):
        if not hasattr(self, "tasks_table"):
            return
        search = self.search_input.text().strip().lower()
        project = self.project_filter.currentText()
        status = self.status_filter.currentText()

        filtered = []
        for task in self.tasks:
            if search and search not in task["name"].lower() and search not in task["project"].lower():
                continue
            if project != "All Projects" and task["project"] != project:
                continue
            if status != "All Statuses" and task["status"] != status:
                continue
            filtered.append(task)

        self.tasks_table.setRowCount(len(filtered))
        for row, task in enumerate(filtered):
            dep_names = []
            for dep_id in task["dependencies"]:
                dep_task = next((t for t in self.tasks if t["id"] == dep_id), None)
                if dep_task:
                    dep_names.append(dep_task["name"])
            values = [
                task["name"], task["project"], task["status"],
                task["priority"], task["due"],
                ", ".join(dep_names) if dep_names else "—"
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col == 2:
                    item.setForeground(
                        __import__("PySide6.QtGui", fromlist=["QColor"]).QColor(
                            STATUS_COLORS.get(task["status"], "#F1F5F9")
                        )
                    )
                elif col == 3:
                    item.setForeground(
                        __import__("PySide6.QtGui", fromlist=["QColor"]).QColor(
                            PRIORITY_COLORS.get(task["priority"], "#F1F5F9")
                        )
                    )
                self.tasks_table.setItem(row, col, item)

            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            completion_checkbox = QCheckBox()
            completion_checkbox.setChecked(task["status"] == "Completed")
            completion_checkbox.setToolTip("Mark task as completed")
            completion_checkbox.toggled.connect(
                lambda checked, task_id=task["id"]: self.set_task_completed(task_id, checked)
            )
            edit_button = QPushButton("Edit")
            delete_button = QPushButton("Delete")
            edit_button.clicked.connect(lambda checked=False, task_id=task["id"]: self.edit_task(task_id))
            delete_button.clicked.connect(lambda checked=False, task_id=task["id"]: self.delete_task(task_id))
            actions_layout.addWidget(completion_checkbox, 0, Qt.AlignmentFlag.AlignCenter)
            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)
            blockers = self.get_blocking_dependencies(task)
            blocker_item = QTableWidgetItem("Blocked" if blockers else "—")
            blocker_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if blockers:
                blocker_item.setForeground(__import__("PySide6.QtGui", fromlist=["QColor"]).QColor("#FFFFFF"))
                blocker_item.setBackground(__import__("PySide6.QtGui", fromlist=["QColor"]).QColor("#7C3AED"))
                blocker_item.setToolTip("Blocked: waiting for " + ", ".join(blockers))
            else:
                blocker_item.setToolTip("This task has no unfinished dependencies.")
            self.tasks_table.setItem(row, 6, blocker_item)
            self.tasks_table.setCellWidget(row, 7, actions)

    def set_task_completed(self, task_id, completed):
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            return
        task["status"] = "Completed" if completed else "Not Started"
        task["completed_on"] = date.today().isoformat() if completed else ""
        self.refresh_all()
    def clear_filters(self):
        self.search_input.clear()
        self.project_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.refresh_tasks_table()

    def dependencies_create_cycle(self, task_id, proposed_dependencies):
        """يرجع True لو الاعتماديات الجديدة ستنشئ دورة."""
        graph = {t["id"]: list(t.get("dependencies", [])) for t in self.tasks}
        graph[task_id] = list(proposed_dependencies)

        visiting = set()
        visited = set()

        def visit(node):
            if node in visiting:
                return True
            if node in visited:
                return False
            visiting.add(node)
            for dep in graph.get(node, []):
                if dep in graph and visit(dep):
                    return True
            visiting.remove(node)
            visited.add(node)
            return False

        return any(visit(node) for node in graph if node not in visited)

    def add_task(self):
        dialog = TaskDialog(self.projects, self.tasks, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data["name"]:
                QMessageBox.warning(self, "Missing task name", "Please enter a task name.")
                return

            success, error_msg = self.service.add_task_with_cycle_check(
                title=data["name"],
                project_name=data["project"],
                due_date=date.fromisoformat(data["due"]),
                importance=3, 
                effort=3,      
                dependencies=data["dependencies"]
            )

            if not success:
                QMessageBox.warning(self, "Invalid Dependencies", error_msg)
                return

            self.tasks = self.service.get_all_tasks()
            self.refresh_all()

    def edit_task(self, task_id):
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            return
        dialog = TaskDialog(self.projects, self.tasks, current_task=task, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data["name"]:
                QMessageBox.warning(self, "Missing task name", "Please enter a task name.")
                return
            if task_id in data["dependencies"]:
                QMessageBox.warning(self, "Invalid dependency", "A task cannot depend on itself.")
                return
            if self.dependencies_create_cycle(task_id, data["dependencies"]):
                QMessageBox.warning(
                    self, "Invalid dependencies",
                    "These dependencies create a cycle. Please choose another dependency."
                )
                return
            if data["status"] == "Completed":
                data["completed_on"] = task.get("completed_on") or date.today().isoformat()
            else:
                data["completed_on"] = ""
            task.update(data)
            self.refresh_all()

    def delete_task(self, task_id):
        task = next((t for t in self.tasks if t["id"] == task_id), None)
        if not task:
            return
        answer = QMessageBox.question(
            self, "Delete task",
            f"Are you sure you want to delete '{task['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.tasks = [t for t in self.tasks if t["id"] != task_id]
            for t in self.tasks:
                t["dependencies"] = [d for d in t["dependencies"] if d != task_id]
            self.refresh_all()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

