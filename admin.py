from admin_ui import *
from PyQt5.QtWidgets import *
import sys
import sqlite3

class Admin(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        # Database config
        self.conn = sqlite3.connect("washing_machines.db")
        self.curs = self.conn.cursor()
        #signals
        self.ui.machine_table.itemSelectionChanged.connect(self.machine_selected)
        self.ui.search_line.textChanged.connect(self.search)
        #buttons
        self.ui.add_btn.clicked.connect(self.add)
        self.ui.del_btn.clicked.connect(self.delete)
        self.ui.search_btn.clicked.connect(self.search)

        self.show_machines()
        self.show_bookings()

    def show_machines(self):
        try:
            query = "SELECT * from machines"
            self.curs.execute(query)
            machines = self.curs.fetchall()
            self.ui.machine_table.setRowCount(len(machines))
            self.ui.machine_table.setColumnCount(1)
            self.ui.machine_table.setHorizontalHeaderLabels(["Machines"])

            for row_index, (machine_id, machine_name) in enumerate(machines):
                self.ui.machine_table.setItem(row_index, 0, QTableWidgetItem(machine_name))
        except Exception as e:
            QMessageBox.critical(self, 'Database Error', f'Failed to retrieve data: {e}')

    def machine_selected(self):
        selected_row = self.ui.machine_table.currentRow()
        if selected_row != -1:
            selected_machine_name = self.ui.machine_table.item(selected_row, 0).text()
            self.ui.machine_line.setText(selected_machine_name)
            print(f"Selected Machine: {selected_machine_name}")

    def add(self):
        machine_name = self.ui.machine_line.text()
        query_check = "SELECT machine_id FROM machines WHERE name = ?"
        self.curs.execute(query_check, (machine_name,))
        result = self.curs.fetchone()
        if not result:
            query = "INSERT INTO machines (name) VALUES (?)"
            self.curs.execute(query, (machine_name,))
            self.conn.commit()
            QMessageBox.information(self, "Notice", "Machine added successfully")
        else:
            QMessageBox.warning(self, "Warning", "Machine already exists!")
        self.ui.machine_line.clear()
        self.show_machines()

    def delete(self):
        response = QMessageBox().question(self, "Notice", "Are you sure you want to delete the machine?",
                                          QMessageBox().Yes | QMessageBox().No)
        if response == QMessageBox().Yes:
            machine_name = self.ui.machine_line.text()
            query_check = "SELECT COUNT(*) FROM bookings WHERE machine_id = (SELECT machine_id FROM machines WHERE name = ?)"
            self.curs.execute(query_check, (machine_name,))
            booking_count = self.curs.fetchone()[0]

            if booking_count > 0:
                QMessageBox.warning(self, "Warning", "This machine has active bookings and cannot be deleted!")
            else:
                query = "DELETE FROM machines WHERE machine_id = (SELECT machine_id from machines WHERE name = ? )"
                self.curs.execute(query, (machine_name,))
                self.conn.commit()
                QMessageBox().information(self, "Notice", "Machine deleted successfully")
            self.ui.machine_line.clear()
            self.show_machines()

    def show_bookings(self, filtered_data = None):
        try:
            if filtered_data is None:
                self.curs.execute("DELETE FROM booking_data")
                query = "SELECT user_id, timeslot_id, machine_id, booking_date from bookings"
                self.curs.execute(query)
                bookings = self.curs.fetchall()

                for booking in bookings:
                    user_id, timeslot_id, machine_id, booking_date = booking
                    self.curs.execute("SELECT email, phone FROM users WHERE user_id = ?", (user_id,))
                    user_info = self.curs.fetchone()

                    self.curs.execute("SELECT start_time, end_time FROM time_slots WHERE timeslot_id = ?", (timeslot_id,))
                    time_info = self.curs.fetchone()

                    self.curs.execute("SELECT name FROM machines WHERE machine_id = ?", (machine_id,))
                    machine_info = self.curs.fetchone()

                    if user_info and time_info and machine_info:
                        query_add = "INSERT INTO booking_data (email, phone, start_time, end_time, machine, booking_date) VALUES (?,?,?,?,?,?)"
                        self.curs.execute(query_add, (user_info[0], user_info[1], time_info[0], time_info[1], machine_info[0], booking_date))
                        self.conn.commit()

                query_select = "SELECT * FROM booking_data"
                self.curs.execute(query_select)
                booking_data = self.curs.fetchall()
                print(booking_data)
            else:
                booking_data = filtered_data

            row_count = len(booking_data)
            self.ui.bookings_table.setRowCount(row_count)
            self.ui.bookings_table.setColumnCount(7)
            self.ui.bookings_table.setHorizontalHeaderLabels(
                ["Booking_data ID", "Email", "Phone", "Start Time", "End Time", "Machine", "Booking Date"])

            for row, booking in enumerate(booking_data):
                for col, data in enumerate(booking):
                    self.ui.bookings_table.setItem(row, col, QTableWidgetItem(str(data)))
        except Exception as e:
            QMessageBox.critical(self, 'Database Error', f'Failed to retrieve data: {e}')

    def search(self):
        search_term = self.ui.search_line.text()
        if not search_term:
            self.show_machines()
            return

        sql = "SELECT * FROM booking_data WHERE phone LIKE ? OR machine LIKE ? OR booking_date LIKE ?"
        search_pattern = '%' + search_term + '%'
        self.curs.execute(sql, (search_pattern, search_pattern, search_pattern))
        results = self.curs.fetchall()
        self.show_bookings(results)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Admin()
    window.show()
    sys.exit(app.exec_())