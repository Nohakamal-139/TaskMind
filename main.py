"""TaskMind entry point: initialises the database and opens an empty main window.

Member 3 will replace the empty window with the real MainWindow and four screens.
"""
import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from app.database.connection import get_connection, init_db


def main() -> int:
    conn = get_connection()
    init_db(conn)  # creates the tables on first run

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("TaskMind")
    window.resize(1000, 650)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
