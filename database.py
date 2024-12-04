import sqlite3
import bcrypt
from datetime import datetime


def create_database():
    conn = sqlite3.connect('hotel_management.db')
    cursor = conn.cursor()

    # Drop the tables if they exist to avoid schema issues
    cursor.execute('DROP TABLE IF EXISTS rooms')
    cursor.execute('DROP TABLE IF EXISTS clients')
    cursor.execute('DROP TABLE IF EXISTS bookings')

    # Create rooms table
    cursor.execute(''' 
        CREATE TABLE rooms (
            room_id INTEGER PRIMARY KEY,
            room_type TEXT,
            price REAL,
            bed_count INTEGER,
            level INTEGER,
            availability BOOLEAN,
            category TEXT,
            description TEXT
        )
    ''')

    # Create clients table with password column
    cursor.execute(''' 
        CREATE TABLE clients (
            client_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create bookings table
    cursor.execute(''' 
        CREATE TABLE bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            status TEXT NOT NULL,
            payment_status TEXT NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients(client_id),
            FOREIGN KEY (room_id) REFERENCES rooms(room_id)
        );
    ''')

    # Check if rooms already exist before inserting
    cursor.execute('SELECT COUNT(*) FROM rooms')
    if cursor.fetchone()[0] == 0:
        rooms = [
            (1, 'Standard', 50, 'Standard Room', 'Basic room with 1 bed', 1, 'Standard Room', 'Basic room with 1 bed'),
            (2, 'Standard', 50, 'Standard Room', 'Basic room with 1 bed', 1, 'Standard Room', 'Basic room with 1 bed'),
            (3, 'Standard', 50, 'Standard Room', 'Basic room with 1 bed', 1, 'Standard Room', 'Basic room with 1 bed'),
            (4, 'Standard', 50, 'Standard Room', 'Basic room with 1 bed', 1, 'Standard Room', 'Basic room with 1 bed'),
            (5, 'Standard', 50, 'Standard Room', 'Basic room with 1 bed', 1, 'Standard Room', 'Basic room with 1 bed'),
            (6, '2-Bed', 70, '2-Bed Room', 'Room with 2 beds', 1, '2-Bed Room', 'Room with 2 beds'),
            (7, '2-Bed', 70, '2-Bed Room', 'Room with 2 beds', 1, '2-Bed Room', 'Room with 2 beds'),
            (8, '2-Bed', 70, '2-Bed Room', 'Room with 2 beds', 1, '2-Bed Room', 'Room with 2 beds'),
            (9, '2-Bed', 70, '2-Bed Room', 'Room with 2 beds', 1, '2-Bed Room', 'Room with 2 beds'),
            (10, '2-Bed', 70,'2-Bed Room', 'Room with 2 beds', 1, '2-Bed Room', 'Room with 2 beds'),
            (11, 'Modern', 110, 'Modern Room', 'Room with 2 beds, modern amenities', 1, 'Modern Room', 'Room with 2 beds, modern amenities'),
            (12, 'Modern', 110, 'Modern Room', 'Room with 2 beds, modern amenities', 1, 'Modern Room', 'Room with 2 beds, modern amenities'),
            (13, 'Modern', 110, 'Modern Room', 'Room with 2 beds, modern amenities', 1, 'Modern Room', 'Room with 2 beds, modern amenities'),
            (14, 'Modern', 110, 'Modern Room', 'Room with 2 beds, modern amenities', 1, 'Modern Room', 'Room with 2 beds, modern amenities'),
            (15, 'Luxury', 150, 'Luxury Room', 'Luxurious room with 2 beds and extra features', 1, 'Luxury Room', 'Luxurious room with 2 beds and extra features'),
            (16, 'Luxury', 150, 'Luxury Room', 'Luxurious room with 2 beds and extra features', 1, 'Luxury Room', 'Luxurious room with 2 beds and extra features')
        ]
        cursor.executemany(''' 
            INSERT INTO rooms (room_id, room_type, price, bed_count, level, availability, category, description) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', rooms)

    conn.commit()
    conn.close()

def sign_up_client(name, email, phone, password):
    conn = sqlite3.connect('hotel_management.db')
    cursor = conn.cursor()

    # Hash the password before storing
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute(''' 
            INSERT INTO clients (name, email, phone, password) 
            VALUES (?, ?, ?, ?)
        ''', (name, email, phone, hashed_password.decode('utf-8')))  # Decode bytes to string
        conn.commit()
        print("Client registered successfully.")
    except sqlite3.IntegrityError as e:
        print(f"Integrity Error: {e}. Ensure unique email and phone.")
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
    finally:
        conn.close()

def authenticate_client(email, password):
    conn = sqlite3.connect('hotel_management.db')
    cursor = conn.cursor()

    try:
        cursor.execute(''' 
            SELECT client_id, name, email, phone, password 
            FROM clients 
            WHERE email = ? 
        ''', (email,))
        client = cursor.fetchone()

        if client:
            stored_password = client[4].encode('utf-8')  # Convert stored password to bytes
            # Check if the password matches
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                print(f"Login successful. Welcome {client[1]}!")
                return client  # Return client info if authentication is successful
            else:
                print("Incorrect password.")
        else:
            print("Client not found.")
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
    finally:
        conn.close()
    return None


# Booking functions
def view_available_rooms():
    conn = sqlite3.connect('hotel_management.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT room_id, room_type, price, description FROM rooms WHERE availability = 1''')
    rooms = cursor.fetchall()

    if rooms:
        print("Available Rooms:")
        for room in rooms:
            print(f"Room ID: {room[0]}, Type: {room[1]}, Price: ${room[2]}, Description: {room[3]}")
    else:
        print("No available rooms.")
    conn.close()


def book_room(client_id, room_id):
    conn = sqlite3.connect('hotel_management.db')
    cursor = conn.cursor()

    # Check if the room exists and is available
    cursor.execute('SELECT availability FROM rooms WHERE room_id = ?', (room_id,))
    room = cursor.fetchone()

    if room is None:
        print(f"Room with ID {room_id} does not exist.")
        conn.close()
        return

    if room[0] == 1:  # Room is available
        # Ensure all required values are present
        booking_date = datetime.now().strftime('%Y-%m-%d')

        if None in (client_id, room_id, booking_date):
            print("Error: Missing required values for booking.")
            conn.close()
            return

        try:
            print(f"client_id: {client_id}, room_id: {room_id}, booking_date: {booking_date}")
            
            # Insert booking (exclude booking_id from the insert as it is auto-incremented)
            cursor.execute(''' 
                INSERT INTO bookings (client_id, room_id, booking_date, status, payment_status) 
                VALUES (?, ?, ?, ?, ?) 
            ''', (client_id, room_id, booking_date, 'Booked', 'Pending'))

            # Mark the room as unavailable
            cursor.execute('UPDATE rooms SET availability = 0 WHERE room_id = ?', (room_id,))

            conn.commit()
            print(f"Room {room_id} booked successfully for client {client_id}.")
        except sqlite3.Error as e:
            print(f"Error occurred while booking the room: {e}")
    else:
        print(f"Room {room_id} is not available.")
    conn.close()





def view_bookings(client_id):
    conn = sqlite3.connect('hotel_management.db')
    cursor = conn.cursor()
    cursor.execute(''' 
        SELECT b.booking_id, r.room_type, b.booking_date, b.status, b.payment_status 
        FROM bookings b 
        JOIN rooms r ON b.room_id = r.room_id
        WHERE b.client_id = ? 
    ''', (client_id,))
    bookings = cursor.fetchall()

    if bookings:
        print(f"Bookings for Client {client_id}:")
        for booking in bookings:
            print(f"Booking ID: {booking[0]}, Room Type: {booking[1]}, Date: {booking[2]}, Status: {booking[3]}, Payment Status: {booking[4]}")
    else:
        print("No bookings found.")
    conn.close()


# Example usage:
if __name__ == '__main__':
    create_database()  # Create the necessary tables and insert rooms data

    # Step 1: Sign up a new client
    print("\nSigning up a client:")
    sign_up_client("John Doe", "johndoe@example.com", "1234567890", "SecurePass123")

    # Step 2: Authenticate the same client
    print("\nAuthenticating the client:")
    client_info = authenticate_client("johndoe@example.com", "SecurePass123")
    if client_info:
        print(f"Authenticated: {client_info}")
        client_id = client_info[0]  # Get the authenticated client ID
        
        # Step 3: View available rooms
        print("\nAvailable Rooms:")
        view_available_rooms()

        # Step 4: Book a room
        print("\nBooking a room:")
        book_room(client_id, 1)  # Book room with ID 1

        # Step 5: View client's bookings
        print("\nViewing bookings:")
        view_bookings(client_id)
    else:
        print("Authentication failed.")
