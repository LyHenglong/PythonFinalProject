import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor


class AdminApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Hotel Management - Admin')
        self.setGeometry(100, 100, 800, 600)

        # Apply custom styles
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f5;
                font-family: Arial, sans-serif;
            }
            QPushButton {
                background-color: #4caf50;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #388e3c;
            }
            QTableWidget {
                background-color: white;
                gridline-color: #ddd;
                selection-background-color: #cce7ff;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 5px;
                height: 30px;
            }
        """)

        self.layout = QVBoxLayout()

        # Action buttons
        self.action_layout = QHBoxLayout()
        self.view_rooms_button = QPushButton('View Rooms', self)
        self.view_rooms_button.clicked.connect(self.view_rooms)
        self.action_layout.addWidget(self.view_rooms_button)

        self.view_bookings_button = QPushButton('View Bookings', self)
        self.view_bookings_button.clicked.connect(self.view_bookings)
        self.action_layout.addWidget(self.view_bookings_button)

        self.view_clients_button = QPushButton('View Clients', self)
        self.view_clients_button.clicked.connect(self.view_clients)
        self.action_layout.addWidget(self.view_clients_button)

        self.reset_booking_button = QPushButton('Reset Booking', self)
        self.reset_booking_button.clicked.connect(self.reset_booking)
        self.action_layout.addWidget(self.reset_booking_button)

        self.layout.addLayout(self.action_layout)

        # Table to display data
        self.table = QTableWidget(self)
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

    def configure_table(self, column_count):
        """Configures table for equal column and row sizes."""
        self.table.setColumnCount(column_count)
        self.table.setRowCount(0)  # Reset the table
        self.table.horizontalHeader().setStretchLastSection(False)
        for col in range(column_count):
            self.table.horizontalHeader().setSectionResizeMode(col, 1)
        self.table.verticalHeader().setDefaultSectionSize(30)  # Row height
        self.table.horizontalHeader().setDefaultSectionSize(100)  # Column width

    # View rooms function
    def view_rooms(self):
        conn = sqlite3.connect('hotel_management.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM rooms''')
        rooms = cursor.fetchall()
        conn.close()

        column_count = 6
        self.configure_table(column_count)
        self.table.setHorizontalHeaderLabels(['Room ID', 'Type', 'Price', 'Category', 'Description', 'Availability'])

        self.table.setRowCount(len(rooms))
        for row, room in enumerate(rooms):
            for col, value in enumerate(room):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

    # View bookings function
    def view_bookings(self):
        try:
            conn = sqlite3.connect('hotel_management.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT bookings.booking_id, clients.name, rooms.room_type, bookings.booking_date, bookings.status, bookings.payment_status, bookings.room_id
                FROM bookings
                JOIN clients ON bookings.client_id = clients.client_id
                JOIN rooms ON bookings.room_id = rooms.room_id
            ''')
            bookings = cursor.fetchall()
            conn.close()

            column_count = 7
            self.configure_table(column_count)
            self.table.setHorizontalHeaderLabels(['Booking ID', 'Client', 'Room Type', 'Date', 'Status', 'Payment', 'Room ID'])

            self.table.setRowCount(len(bookings))
            for row, booking in enumerate(bookings):
                for col, value in enumerate(booking):
                    self.table.setItem(row, col, QTableWidgetItem(str(value)))
                    
        except sqlite3.Error as e:
            print(f"An error occurred while accessing the database: {e}")

    # View clients function
    def view_clients(self):
        conn = sqlite3.connect('hotel_management.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM clients''')
        clients = cursor.fetchall()
        conn.close()

        column_count = 4
        self.configure_table(column_count)
        self.table.setHorizontalHeaderLabels(['Client ID', 'Name', 'Email', 'Phone'])

        self.table.setRowCount(len(clients))
        for row, client in enumerate(clients):
            for col, value in enumerate(client):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

    # Reset booking function
    def reset_booking(self):
        booking_id, ok = self.get_booking_id()
        if ok:
            conn = sqlite3.connect('hotel_management.db')
            cursor = conn.cursor()
            cursor.execute('''SELECT room_id FROM bookings WHERE booking_id = ?''', (booking_id,))
            room = cursor.fetchone()

            if room:
                room_id = room[0]
                cursor.execute('''DELETE FROM bookings WHERE booking_id = ?''', (booking_id,))
                cursor.execute('''UPDATE rooms SET availability = 1 WHERE room_id = ?''', (room_id,))
                conn.commit()
                conn.close()
                self.show_message('Success', f"Booking {booking_id} has been reset.")
            else:
                self.show_message('Error', 'No booking found with this ID.')

    # Helper method to get booking ID input
    def get_booking_id(self):
        booking_id, ok = QInputDialog.getInt(self, 'Reset Booking', 'Enter booking ID to reset:')
        return booking_id, ok

    # Function to show messages
    def show_message(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    admin_window = AdminApp()
    admin_window.showMaximized()  # Start maximized
    sys.exit(app.exec_())
 