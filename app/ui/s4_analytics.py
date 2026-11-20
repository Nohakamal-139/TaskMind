from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame
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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        side = min(self.width(), self.height()) - 38
        circle = QRectF(
            (self.width() - side) / 2,
            (self.height() - side) / 2,
            side,
            side,
        )

        track_color = "#DCE9F5" if self.light_theme else "#2C5B80"
        pen = QPen(QColor(track_color), 18)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)
        painter.drawArc(circle, 0, 360 * 16)

        if self.total:
            start_angle = 90 * 16
            remaining_angle = 360 * 16
            segments = [
                (name, count)
                for name, count in self.counts.items()
                if count > 0
            ]

            for index, (name, count) in enumerate(segments):
                if index == len(segments) - 1:
                    span = remaining_angle
                else:
                    span = round(360 * 16 * count / self.total)
                    span = min(span, remaining_angle)

                pen.setColor(QColor(self.COLORS[name]))
                painter.setPen(pen)
                painter.drawArc(circle, start_angle, -span)

                start_angle -= span
                remaining_angle -= span

        completed = self.counts.get("Completed", 0)
        percent = round(completed * 100 / self.total) if self.total else 0

        main_text = "#1C2B44" if self.light_theme else "#F1F5F9"
        muted_text = "#667085" if self.light_theme else "#94A3B8"

        painter.setPen(QColor(main_text))
        painter.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter,
            f"{percent}%",
        )

        painter.setPen(QColor(muted_text))
        painter.setFont(QFont("Segoe UI", 9))
        label_area = QRectF(
            0,
            self.height() / 2 + 20,
            self.width(),
            25,
        )
        painter.drawText(
            label_area,
            Qt.AlignmentFlag.AlignHCenter,
            "completed",
        )


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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        left, right, top, bottom = 42, 14, 18, 32
        plot = QRectF(
            left,
            top,
            max(1, self.width() - left - right),
            max(1, self.height() - top - bottom),
        )

        max_count = max([value for _day, value in self.daily] or [0])
        axis_max = max(5, max_count)
        tick_step = 1 if axis_max <= 8 else max(1, (axis_max + 4) // 5)
        ticks = list(range(0, axis_max + 1, tick_step))
        if ticks[-1] != axis_max:
            ticks.append(axis_max)

        grid_color = "#B8C8DB" if self.light_theme else "#2C5B80"
        axis_color = "#2583E8" if self.light_theme else "#8FCBFF"

        painter.setFont(QFont("Segoe UI", 9))

        for value in ticks:
            y = plot.bottom() - plot.height() * value / axis_max

            painter.setPen(
                QPen(
                    QColor(grid_color),
                    1,
                    Qt.PenStyle.DotLine,
                )
            )
            painter.drawLine(
                int(plot.left()),
                int(y),
                int(plot.right()),
                int(y),
            )

            painter.setPen(QColor(axis_color))
            painter.drawText(
                QRectF(0, y - 8, left - 8, 18),
                Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignVCenter,
                str(value),
            )

        points = []

        if self.daily:
            step = plot.width() / max(1, len(self.daily) - 1)

            for index, (_day, value) in enumerate(self.daily):
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

                painter.setPen(QPen(QColor("#20C9D8"), 3))
                painter.setBrush(Qt.BrushStyle.NoBrush)

                for first, second in zip(points, points[1:]):
                    painter.drawLine(
                        int(first[0]),
                        int(first[1]),
                        int(second[0]),
                        int(second[1]),
                    )

            painter.setPen(QPen(QColor("#20C9D8"), 2))
            painter.setBrush(QColor("#20C9D8"))

            for x, y in points:
                painter.drawEllipse(QRectF(x - 3, y - 3, 6, 6))

            date_color = "#667085" if self.light_theme else "#94A3B8"
            painter.setPen(QColor(date_color))

            for index, (day, _value) in enumerate(self.daily):
                x = points[index][0]
                painter.drawText(
                    QRectF(x - 23, plot.bottom() + 7, 46, 18),
                    Qt.AlignmentFlag.AlignHCenter,
                    day,
                )

        if not any(value for _day, value in self.daily):
            empty_color = "#667085" if self.light_theme else "#94A3B8"
            painter.setPen(QColor(empty_color))
            painter.drawText(
                plot,
                Qt.AlignmentFlag.AlignCenter,
                "Completed tasks will appear here",
            )
class AnalyticsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        title = QLabel("Progress Analytics")
        title.setObjectName("PageTitle")
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #F1F5F9;")
        layout.addWidget(title)

        charts_layout = QHBoxLayout()
        self.donut = DonutChart()
        self.trend = CompletionTrendChart()

        charts_layout.addWidget(self.donut)
        charts_layout.addWidget(self.trend)
        layout.addLayout(charts_layout)
        layout.addStretch()

    def set_tasks(self, tasks):
        pass
