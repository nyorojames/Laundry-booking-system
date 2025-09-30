from PyQt5.QtWidgets import *
from PyQt5.QtGui import QMovie
from mainWindow_ui import *
from bookings import Bookings
from admin import Admin
from authentication import Authenticate
import sys

class MainWindow(QMainWindow):
    def __init__(self, user_id, role):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.action_students.triggered.connect(self.booking)
        self.ui.action_admin.triggered.connect(self.admin)
        self.ui.log_out.clicked.connect(self.log_out)

        self.user_id = user_id
        self.role = role

        self.bubbles_movie = QMovie("bubbles.gif")
        self.ui.bubbles_label.setMovie(self.bubbles_movie)
        self.bubbles_movie.start()

    def booking(self):
        if self.role == "Student":
            self.booking = Bookings(user_id = self.user_id)
            self.booking.show()
        else:
            QMessageBox.warning(self, "Access Denied", "Only students can book.")

    def admin(self):
        if self.role == "Admin":
            self.admin = Admin()
            self.admin.show()
        else:
            QMessageBox.warning(self, "Access Denied", "Only admins have access.")

    def log_out(self):
        self.close()
        self.login_window = Authenticate()
        self.login_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = Authenticate()
    
    if login.exec_() == QDialog.Accepted:
        user_id = login.user_id
        role = login.role

        window = MainWindow(user_id = user_id,  role = role)
        window.show()
        sys.exit(app.exec_())