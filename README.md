# Laundry-booking-system

This project is a PyQt5-based desktop application designed to manage laundry bookings for dormitory students with separate user roles (Students and Admins). It uses an SQLite3 database for storing users, bookings, machines, and timeslots. The system provides an intuitive interface for students to reserve washing machines and for admins to manage resources and monitor bookings.

🔑 Authentication & Roles

A login system verifies user credentials and assigns roles (Student or Admin).
Role-based access ensures users only see and use features they are authorized for.
Unauthorized actions trigger a clear “Access Denied” warning.

🎓 Student Features (Bookings Module)

Students can:
1.Select a valid date from the calendar (future dates, excluding Sundays).
2.View available timeslots stored in the database and choose one.
3.Browse available washing machines for the chosen date and timeslot (excluding already booked ones).
4.Review a booking summary (date, timeslot, machine) before confirming.
5.Confirm bookings, which are stored in the SQLite database.
6.Receive clear feedback via success, warning, or error dialogs.

🛠️ Admin Features (Admin Module)

Admins can:
1.View all registered machines in the system.
2.Add new machines to the database.
3.Delete machines (with safeguards preventing deletion if the machine has active bookings).
4.View all bookings with details including:
 -User email & phone number
 -Start & end time
 -Machine name
 -Booking date
5.Search bookings by phone number, machine, or booking date.
6.Monitor and manage system data through a consolidated booking overview table.

🖥️ Main Window

Built with QMainWindow (mainWindow_ui.py).
Role-based menu options (Student → Bookings, Admin → Admin panel).
Animated background (bubbles.gif) for a modern interface.
Log Out button returns users to the login screen.

⚙️ Tech Stack

Python 3
PyQt5 (GUI framework)
SQLite3 (lightweight database)
 
