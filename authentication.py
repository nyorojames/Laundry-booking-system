from PyQt5.QtWidgets import *
from authentication_ui import *

import sys
import sqlite3

class Authenticate(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.stackedWidget.setCurrentIndex(0)
        #Database config
        self.conn = sqlite3.connect("washing_machines.db")
        self.curs = self.conn.cursor()
        #buttons
        self.ui.signup_btn.clicked.connect(self.sign_up)
        self.ui.login_btn.clicked.connect(self.log_in)
        self.ui.signup_btn2.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.update_btn_2.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.update_btn.clicked.connect(self.update)

        self.role = None
        self.user_id = None

    def log_in(self):
        email = self.ui.email.text()
        password = self.ui.password.text()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Please fill in all the fields.")
            return

        self.curs.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = self.curs.fetchone()

        if user:
            self.role = user[4]
            self.user_id = user[0]
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials. Try again.")

    def sign_up(self):
        email = self.ui.email_2.text()
        phone = self.ui.phone_no.text()
        password = self.ui.password_2.text()
        confirm_password = self.ui.confirm_password.text()
        role = self.ui.comboBox.currentText()

        if not email or not phone or not password or not confirm_password:
            QMessageBox.warning(self, 'Error', 'Please fill in all the fields.')
            return

        if password != confirm_password:
            QMessageBox.warning(self, 'Error', 'Passwords do not match.')
            return

        try:
            if self.verify_user(email, phone):
                QMessageBox.warning(self, 'Error', 'User with this email or phone already exists.')
                return
            sql = "INSERT INTO users (email, phone, password, role) VALUES (?, ?, ?, ?)"
            self.curs.execute(sql, (email, phone, password, role))
            self.conn.commit()
            QMessageBox.information(self, 'Success', 'Sign-up successful!')
            self.ui.stackedWidget.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.critical(self, 'Database Error', f'Failed to insert data: {e}')
        # checks if username already exists
    def verify_user(self, email, phone):
        self.curs.execute('SELECT * FROM users WHERE email = ? OR phone = ?', (email, phone))
        user = self.curs.fetchone()
        return user is not None

    def update(self):
        old_password = self.ui.old_password.text()
        new_password = self.ui.new_password.text()
        old_telephone = self.ui.old_telephone.text()
        new_telephone= self.ui.new_telephone.text()

        if not old_password or not old_telephone or not new_password or not new_telephone:
            QMessageBox.warning(self, 'Error', 'Please fill in all the fields.')
            return

        try:
            sql_check = "SELECT phone, password FROM users WHERE phone = ? AND password = ?"
            self.curs.execute(sql_check, (old_telephone, old_password))
            result = self.curs.fetchone()
            if not result:
                QMessageBox.warning(self, 'Error', 'Incorrect phone number or password.')
                return

            sql_update = "UPDATE users SET phone = ?, password = ? WHERE phone = ? AND password = ?"
            self.curs.execute(sql_update, (new_telephone, new_password, old_telephone, old_password))
            self.conn.commit()
            QMessageBox.information(self, 'Success', 'Update successful!')
            self.ui.stackedWidget.setCurrentIndex(0)
        except Exception as e:
            QMessageBox.critical(self, 'Database Error', f'Failed to update data: {e}')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Authenticate()
    window.show()
    sys.exit(app.exec_())