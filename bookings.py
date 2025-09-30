from PyQt5.QtWidgets import *
from bookings_ui import *
from PyQt5.QtCore import QDate
import sys
import sqlite3

class Bookings(QDialog):
    def __init__(self, user_id):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.stackedWidget.setCurrentIndex(0)
        # Database config
        self.conn = sqlite3.connect("washing_machines.db")
        self.curs = self.conn.cursor()
        #user selections
        self.selected_date = None
        self.selected_timeslot_id = None
        self.selected_machine_name = None
        self.user_id = user_id

        # Disable all buttons
        for button in self.findChildren(QPushButton):
            button.setEnabled(False)
        # Connect signals
        self.ui.calendarWidget.selectionChanged.connect(self.date_selected)
        self.ui.times_table.itemSelectionChanged.connect(self.time_selected)
        self.ui.machines_table.itemSelectionChanged.connect(self.machine_selected)
        # Navigation buttons
        self.ui.next_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.back_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.next_btn_2.clicked.connect(self.go_to_machines)
        self.ui.back_btn_2.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.next_btn_3.clicked.connect(self.go_to_confirmation)
        self.ui.confrim_btn.clicked.connect(self.confirm_booking)
        self.ui.back_btn_3.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2) )

        self.show_timeslots()

    def date_selected(self):
        selected_date = self.ui.calendarWidget.selectedDate()
        today = QDate.currentDate()
        if selected_date < today or selected_date.dayOfWeek() == 7:
            self.ui.date_label.setText("Please select a valid date.")
        else:
            self.ui.date_label.setText(f"Selected Date: {selected_date.toString('dddd, MMMM d, yyyy')}")
            self.ui.next_btn.setEnabled(True)
            self.selected_date = selected_date.toString()

    def show_timeslots(self):
        query = "SELECT * FROM time_slots"
        result = list(self.curs.execute(query))

        self.ui.times_table.setRowCount(len(result))
        self.ui.times_table.setColumnCount(2)
        self.ui.times_table.setHorizontalHeaderLabels(["Start Time", "End Time"])
        for row_index, row_data in enumerate(result):
            self.ui.times_table.setItem(row_index, 0, QTableWidgetItem(row_data[1]))
            self.ui.times_table.setItem(row_index, 1, QTableWidgetItem(row_data[2]))

        self.ui.times_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.ui.times_table.setSelectionMode(QTableWidget.SingleSelection)

    def time_selected(self):
        selected_row = self.ui.times_table.currentRow()
        if selected_row != -1:
            start_time = self.ui.times_table.item(selected_row, 0).text()
            end_time = self.ui.times_table.item(selected_row, 1).text()

            sql = "SELECT timeslot_id FROM time_slots WHERE start_time = ? AND end_time = ?"
            self.curs.execute(sql, (start_time, end_time))
            result = self.curs.fetchone()

            if result:
                self.selected_timeslot_id = result[0]
                self.ui.back_btn.setEnabled(True)
                self.ui.next_btn_2.setEnabled(True)
                print(f"Selected Time Slot: {start_time} - {end_time}")

    def go_to_machines(self):
        self.ui.stackedWidget.setCurrentIndex(2)
        self.show_machines()

    def show_machines(self):
        try:
            query = """SELECT name FROM machines WHERE machine_id NOT IN 
                       (   SELECT machine_id FROM bookings 
                           WHERE booking_date = ? AND timeslot_id = ? AND machine_id IS NOT NULL
                       )"""
            self.curs.execute(query, (self.selected_date, self.selected_timeslot_id))
            available_machines = list(self.curs.fetchall())
            if not available_machines:
                QMessageBox.warning(self, "Info", "No available machines for this time slot.")
                self.ui.machines_table.setRowCount(0)
                return

            self.ui.machines_table.setRowCount(len(available_machines))
            self.ui.machines_table.setColumnCount(1)
            self.ui.machines_table.setHorizontalHeaderLabels(["Available Machines"])

            for row_index, (machine_name,) in enumerate(available_machines):
                self.ui.machines_table.setItem(row_index, 0, QTableWidgetItem(machine_name))
        except Exception as e:
            QMessageBox.critical(self, 'Database Error', f'Failed to retrieve data: {e}')

    def machine_selected(self):
        selected_row = self.ui.machines_table.currentRow()
        if selected_row != -1:
            self.selected_machine_name = self.ui.machines_table.item(selected_row, 0).text()
            print(f"Selected Machine: {self.selected_machine_name}")
        self.ui.back_btn_2.setEnabled(True)
        self.ui.next_btn_3.setEnabled(True)

    def go_to_confirmation(self):
        self.ui.stackedWidget.setCurrentIndex(3)
        self.show_booking_summary()
        self.ui.confrim_btn.setEnabled(True)
        self.ui.back_btn_3.setEnabled(True)

    def show_booking_summary(self):
        query = "SELECT start_time, end_time from time_slots where timeslot_id = ?"
        self.curs.execute(query, (self.selected_timeslot_id,))
        selected_time = self.curs.fetchall()
        formatted_time = f"{selected_time[0][0]} - {selected_time[0][1]}"
        summary = f"Date: {self.selected_date}\nMachine: {self.selected_machine_name}\nTime: {formatted_time}"
        print(f"Booking Summary:\n{summary}")

        self.ui.bookings_table.setRowCount(1)
        self.ui.bookings_table.setColumnCount(3)
        self.ui.bookings_table.setHorizontalHeaderLabels(["Date", "Machine", "Time"])
        self.ui.bookings_table.setItem(0, 0, QTableWidgetItem(self.selected_date))
        self.ui.bookings_table.setItem(0, 1, QTableWidgetItem(self.selected_machine_name))
        self.ui.bookings_table.setItem(0, 2, QTableWidgetItem(formatted_time))

    def confirm_booking(self):
        try:
            sql = "SELECT machine_id FROM machines WHERE name = ?"
            self.curs.execute(sql, (self.selected_machine_name,))
            result = self.curs.fetchone()
            if not result:
                QMessageBox.warning(self, "Error", "Machine not found!")
                return
            machine_id = result[0]
            query = "INSERT INTO bookings (booking_date, timeslot_id, machine_id, user_id) VALUES (?,?,?,?)"
            self.curs.execute(query, (self.selected_date, self.selected_timeslot_id, machine_id, self.user_id))
            self.conn.commit()
            QMessageBox.information(self, 'Success', 'Booking confirmed')

            self.selected_date = None
            self.selected_timeslot_id = None
            self.selected_machine_name = None
            self.ui.stackedWidget.setCurrentIndex(0)
        except Exception as e:
                QMessageBox.critical(self, 'Database Error', f'Failed to save booking: {e}')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Bookings(user_id=4)
    window.show()
    sys.exit(app.exec_())