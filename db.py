import sqlite3
import hashlib
from datetime import datetime


DATABASE_PATH = './fitness.db'

# Initialize the database
def init_db():
    """
    Create the database and `user_info`, `login` and `log` table if it doesn't exist.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            age INTEGER,
            weight REAL,
            height REAL,
            activity_level TEXT,
            goal TEXT,
            health TEXT,
            food TEXT,
            FOREIGN KEY(email) REFERENCES login(email)
        )
    ''')

    # Create login table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    ''')
    
    # Create log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            date DATE NOT NULL,
            time TIME NOT NULL,
            bp TEXT NOT NULL,
            food TEXT NOT NULL,
            FOREIGN KEY(email) REFERENCES login(email)
        )
    ''')

    conn.commit()
    conn.close()

from datetime import datetime

def insert_log(email, daily_bp, daily_food):
    """
    Insert user log data (daily_bp, daily_food) along with the current date, time, and user email into the `log` table.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Get the current date and time
        current_date = datetime.now().date()  # YYYY-MM-DD format
        current_time = datetime.now().strftime("%H:%M:%S")  # Convert time to HH:MM:SS string

        # Insert into the log table
        cursor.execute('''
            INSERT INTO log (email, date, time, bp, food)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, current_date, current_time, daily_bp, daily_food))
        conn.commit()
        return True, "Log inserted successfully!"
    except Exception as e:
        return False, f"Error inserting log: {e}"
    finally:
        conn.close()


def insert_login(data):
    """Insert user login data (email, password, and name) into the `login` table."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO login (name, email, password)
            VALUES (?, ?, ?)
        ''', (data['name'], data['email'], data['password']))

        conn.commit()
        conn.close()

    except sqlite3.IntegrityError as e:
        raise Exception(f"Error: User with email {data['email']} already exists.")
    except Exception as e:
        raise Exception(f"Database error: {e}")

def insert_user(data, email):
    """
    Insert user data into the `user_info` table.
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Make sure email exists in login table (foreign key constraint check)
        cursor.execute('''SELECT email FROM login WHERE email = ?''', (email,))
        if not cursor.fetchone():
            return False, "Email does not exist in the login table."

        cursor.execute('''
            INSERT INTO user_info (email, age, weight, height, activity_level, goal, health, food)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (email, data['age'], data['weight'], data['height'], data['activity_level'], data['goal'], data['health'], data['food']))

        conn.commit()
        conn.close()
        return True, "Profile created successfully."
    except sqlite3.IntegrityError as e:
        return False, f"IntegrityError: {e}"
    except Exception as e:
        return False, f"Database error: {e}"
    
def validate_login(email, password):
    """
    Validate the user's login credentials.
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM login WHERE email = ? AND password = ?
        ''', (email, hashlib.sha256(password.encode()).hexdigest()))  # Check hashed password

        user = cursor.fetchone()
        conn.close()
        if user:
            return True
        else:
            return False
    except Exception as e:
        raise Exception(f"Error validating login: {e}")
    
    
# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()

# # Retrieve a user by email
# def get_user_by_email(email):
#     """
#     Fetch a user from the `user_info` table by email.
#     :param email: Email address of the user to fetch.
#     :return: User row or None if not found.
#     """
#     conn = sqlite3.connect(DATABASE_PATH)
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM user_info WHERE email = ?', (email,))
#     user = cursor.fetchone()
#     conn.close()
#     return user

# def verify_login(email, password):
#     """Verify user login credentials (email and password) from the `login` table."""
#     try:
#         conn = sqlite3.connect(DATABASE_PATH)
#         cursor = conn.cursor()

#         # Query to check if the email and password match
#         cursor.execute('''
#             SELECT name FROM login WHERE email = ? AND password = ?
#         ''', (email, password))

#         result = cursor.fetchone()

#         conn.close()

#         if result:
#             return True, result[0]  # Return True and user's name if valid
#         else:
#             return False, None  # Return False if invalid

#     except Exception as e:
#         raise Exception(f"Database error: {e}")


# def register_user(email, password):
#     """
#     Register a new user in the login table.
#     """
#     conn = sqlite3.connect(DATABASE_PATH)
#     cursor = conn.cursor()
#     try:
#         # Insert email and hashed password into the login table
#         cursor.execute('''
#             INSERT INTO login (email, password)
#             VALUES (?, ?)
#         ''', (email, hash_password(password)))
#         conn.commit()
#         conn.close()
#         return True, "Signup successful! Proceed to the profile setup page."
#     except sqlite3.IntegrityError:
#         conn.close()
#         return False, "Email already registered."
#     except Exception as e:
#         conn.close()
#         return False, f"Database error: {e}"



# def authenticate_user(email, password):
#     """
#     Authenticate a user by checking email and password.
#     Also checks if the user has completed their profile.
#     """
#     conn = sqlite3.connect(DATABASE_PATH)
#     cursor = conn.cursor()

#     # Validate credentials
#     cursor.execute('SELECT password FROM login WHERE email = ?', (email,))
#     result = cursor.fetchone()

#     if result and result[0] == hash_password(password):
#         # Check if profile is complete
#         cursor.execute('SELECT name FROM user_info WHERE email = ?', (email,))
#         user = cursor.fetchone()
#         conn.close()
#         if user and user[0]:  # If the name is not empty, profile is complete
#             return True, "Login successful. Profile complete."
#         return True, "Login successful. Complete your profile."
#     conn.close()
#     return False, "Invalid email or password."