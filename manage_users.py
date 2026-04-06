import sys
import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = 'database.db'

def get_db_conn():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def set_user(username, password):
    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        # User exists, update password
        new_password_hash = generate_password_hash(password)
        cursor.execute("UPDATE user SET password = ? WHERE username = ?", (new_password_hash, username))
        print(f"Password for user '{username}' has been updated.")
    else:
        # User does not exist, create new user
        new_password_hash = generate_password_hash(password)
        cursor.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, new_password_hash))
        print(f"New user '{username}' created.")

    conn.commit()
    conn.close()

def delete_user(username):
    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user is None:
        print(f"User '{username}' not found.")
        conn.close()
        return

    user_id = user['id']

    # Delete user's posts first to maintain foreign key integrity
    cursor.execute("DELETE FROM post WHERE author_id = ?", (user_id,))
    print(f"Deleted posts for user '{username}'.")

    # Delete the user
    cursor.execute("DELETE FROM user WHERE id = ?", (user_id,))
    print(f"Deleted user '{username}'.")

    conn.commit()
    conn.close()

def set_user_id(username, new_id_str):
    try:
        new_id = int(new_id_str)
    except ValueError:
        print("Error: New ID must be an integer.")
        return
        
    conn = get_db_conn()
    cursor = conn.cursor()

    # Check if the target user exists
    cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user is None:
        print(f"User '{username}' not found.")
        conn.close()
        return
    old_id = user['id']

    if old_id == new_id:
        print(f"User '{username}' already has ID {new_id}.")
        conn.close()
        return

    # Check if the new_id is already in use by another user
    cursor.execute("SELECT id FROM user WHERE id = ?", (new_id,))
    target_id_user = cursor.fetchone()
    if target_id_user is not None:
        print(f"Error: User ID {new_id} is already taken.")
        conn.close()
        return

    # Temporarily disable foreign key constraints to change the ID
    try:
        cursor.execute("PRAGMA foreign_keys=off;")
        conn.commit() # commit the pragma

        # Start a transaction
        cursor.execute("BEGIN TRANSACTION;")

        # Create a temporary user with the new ID
        cursor.execute("INSERT INTO user (id, username, password) VALUES (?, ?, (SELECT password FROM user WHERE id = ?))", (new_id, username, old_id))
        
        # Update posts to point to the new user ID
        cursor.execute("UPDATE post SET author_id = ? WHERE author_id = ?", (new_id, old_id))
        
        # Delete the old user record
        cursor.execute("DELETE FROM user WHERE id = ?", (old_id,))
        
        # Commit the transaction
        conn.commit()

        print(f"Successfully changed user ID for '{username}' from {old_id} to {new_id}.")

    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys=on;")
        conn.commit()
        conn.close()

def list_users():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM user ORDER BY id")
    users = cursor.fetchall()
    conn.close()

    if not users:
        print("No users found in the database.")
        return

    # Determine column widths for formatting
    id_width = max(len(str(u['id'])) for u in users) if users else 2
    username_width = max(len(u['username']) for u in users) if users else 8
    password_width = max(len(u['password']) for u in users) if users else 13

    # Headers
    id_width = max(id_width, len("ID"))
    username_width = max(username_width, len("Username"))
    password_width = max(password_width, len("Password Hash"))

    header_format = f"| {{:<{id_width}}} | {{:<{username_width}}} | {{:<{password_width}}} |"
    row_format = f"| {{:<{id_width}}} | {{:<{username_width}}} | {{:<{password_width}}} |"
    divider = f"+{'-' * (id_width+2)}+{'-' * (username_width+2)}+{'-' * (password_width+2)}+"

    print(divider)
    print(header_format.format("ID", "Username", "Password Hash"))
    print(divider)

    for user in users:
        print(row_format.format(user['id'], user['username'], user['password']))
    print(divider)


def print_usage():
    print("Usage: python manage_users.py <command> [options]")
    print("\nCommands:")
    print("  list                        - List all user accounts.")
    print("  set <username> <password>   - Create a new user or update an existing user's password.")
    print("  del <username>              - Delete a user and all their posts.")
    print("  setid <username> <new_id>   - Change a user's ID. WARNING: This is a risky operation.")
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_usage()

    command = sys.argv[1].lower()
    
    if command == 'list' and len(sys.argv) == 2:
        list_users()
    elif command == 'set' and len(sys.argv) == 4:
        set_user(sys.argv[2], sys.argv[3])
    elif command == 'del' and len(sys.argv) == 3:
        delete_user(sys.argv[2])
    elif command == 'setid' and len(sys.argv) == 4:
        set_user_id(sys.argv[2], sys.argv[3])
    else:
        print_usage()
