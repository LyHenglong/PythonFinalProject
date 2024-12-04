import sys
import sqlite3
import bcrypt
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QSizePolicy, QHeaderView
)
import re  # Import regex module for email and phone validation

class UserApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Hotel Management - User')
        self.setGeometry(100, 100, 600, 500)

        # Apply custom styles (similar to the AdminApp design)
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
            QLineEdit {
                padding: 5px;
                margin-bottom: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
        """)

        self.layout = QVBoxLayout()

        # Input fields for user details
        self.name_input = QLineEdit(self)
        self.email_input = QLineEdit(self)
        self.phone_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)  # Hide password input

        self.layout.addWidget(QLabel("Name"))
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(QLabel("Email"))
        self.layout.addWidget(self.email_input)
        self.layout.addWidget(QLabel("Phone"))
        self.layout.addWidget(self.phone_input)
        self.layout.addWidget(QLabel("Password"))
        self.layout.addWidget(self.password_input)

        # Action buttons (Sign Up, Login, View Rooms)
        self.sign_up_button = QPushButton('Sign Up', self)
        self.sign_up_button.clicked.connect(self.sign_up_client)
        self.layout.addWidget(self.sign_up_button)

        self.login_button = QPushButton('Log In', self)
        self.login_button.clicked.connect(self.login_client)
        self.layout.addWidget(self.login_button)

        self.view_rooms_button = QPushButton('View Available Rooms', self)
        self.view_rooms_button.clicked.connect(self.view_rooms)
        self.layout.addWidget(self.view_rooms_button)

        self.setLayout(self.layout)

        # Initialize room table widget (initially empty)
        self.room_table = None
        self.client_id = None  

    def connect_db(self):
        """Connect to the database."""
        return sqlite3.connect('hotel_management.db')

    def hash_password(self, password):
        """Hash the password for secure storage."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def verify_password(self, password, hashed_password):
        """Verify the provided password against the hashed password."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

    def sign_up_client(self):
        """Register a new client."""
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        password = self.password_input.text().strip()

        if not self.evaluate_user_input(name, email, phone, password):
            return

        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute('''SELECT client_id FROM clients WHERE email = ?''', (email,))
            existing_client = cursor.fetchone()

            if existing_client:
                self.show_message('Sign Up Error', 'Email is already registered. Please log in.')
            else:
                hashed_password = self.hash_password(password)
                cursor.execute('''INSERT INTO clients (name, email, phone, password) VALUES (?, ?, ?, ?)''', 
                               (name, email, phone, hashed_password))
                conn.commit()
                client_id = cursor.lastrowid
                self.show_message('Sign Up Success', f'{name}, you have been successfully registered! Your Client ID is {client_id}.')
        except sqlite3.Error as e:
            self.show_message('Database Error', f'Error: {e}')
        finally:
            conn.close()

    def login_client(self):
        """Authenticate a client for login."""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not (email and password):
            self.show_message('Input Error', 'Email and password are required for login.')
            return

        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute('''SELECT client_id, name, password FROM clients WHERE email = ?''', (email,))
            client = cursor.fetchone()

            if client and self.verify_password(password, client[2]):
                self.client_id = client[0]  # Store client ID after successful login
                self.show_message('Login Success', f'Welcome back {client[1]}!')
                self.view_rooms()  # Show rooms upon successful login
            else:
                self.show_message('Login Failed', 'Invalid email or password.')
        except sqlite3.Error as e:
            self.show_message('Database Error', f'Error: {e}')
        finally:
            conn.close()

    def view_rooms(self):
        """View available rooms."""
        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute('''SELECT room_id, room_type, price, category, description, availability FROM rooms WHERE availability = 1''')
            rooms = cursor.fetchall()

            if rooms:
                self.show_rooms_table(rooms)
            else:
                self.show_message('No Available Rooms', 'There are no available rooms.')
        except sqlite3.Error as e:
            self.show_message('Database Error', f'Error: {e}')
        finally:
            conn.close()

    def show_rooms_table(self, rooms):
        """Show available rooms in a table format with a 'Book' button."""
        if self.room_table:
            self.room_table.setParent(None)  # Remove existing table

        self.room_table = QTableWidget()
        self.room_table.setRowCount(len(rooms))
        self.room_table.setColumnCount(7)
        self.room_table.setHorizontalHeaderLabels(['Room ID', 'Type', 'Price', 'Category', 'Description', 'Availability', 'Action'])

        for row, room in enumerate(rooms):
            for col, value in enumerate(room):
                self.room_table.setItem(row, col, QTableWidgetItem(str(value)))

            # Add a 'Book' button for each room
            book_button = QPushButton('Book')
            book_button.clicked.connect(lambda checked, room_id=room[0]: self.book_room(room_id))
            self.room_table.setCellWidget(row, 6, book_button)

        # Ensure all columns have equal width
        header = self.room_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.layout.addWidget(self.room_table)

    def book_room(self, room_id):
        """Allow client to book a room."""
        if not self.client_id:
            self.show_message('Login Required', 'You need to log in to book a room.')
            return

        conn = self.connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute('''SELECT availability FROM rooms WHERE room_id = ?''', (room_id,))
            room = cursor.fetchone()

            if room and room[0] == 1:  # Room is available
                # Get the current date and time for booking_date
                booking_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Book the room (update availability)
                cursor.execute('''UPDATE rooms SET availability = 0 WHERE room_id = ?''', (room_id,))

                # Create a booking record with booking_date
                cursor.execute('''INSERT INTO bookings (client_id, room_id, booking_date, status, payment_status) 
                                VALUES (?, ?, ?, ?, ?)''', 
                            (self.client_id, room_id, booking_date, 'Booked', 'Pending'))

                conn.commit()
                self.show_message('Booking Success', f'Room {room_id} has been successfully booked on {booking_date}!')
            else:
                self.show_message('Booking Failed', 'This room is no longer available.')

        except sqlite3.Error as e:
            self.show_message('Database Error', f'Error: {e}')
        finally:
            conn.close()

    def show_message(self, title, message):
        """Show a message box with a title and message."""
        QMessageBox.information(self, title, message)

    def evaluate_user_input(self, name, email, phone, password):
        """Validate user input."""
        if not name or not email or not phone or not password:
            self.show_message('Input Error', 'All fields are required.')
            return False

        # Email validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            self.show_message('Input Error', 'Please enter a valid email address.')
            return False

        # Phone number validation
        phone_regex = r'^\d{10}$'  # Assuming phone numbers must be 10 digits
        if not re.match(phone_regex, phone):
            self.show_message('Input Error', 'Phone number must be 10 digits long.')
            return False

        # Password validation (e.g., minimum length of 6 characters)
        if len(password) < 6:
            self.show_message('Input Error', 'Password must be at least 6 characters long.')
            return False

        return True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    user_app = UserApp()
    user_app.show()
    sys.exit(app.exec_())
