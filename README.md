# Centrala Trust for Ornithology (CTO) - Bird Sighting Message Board

This project is a web-based bird study application developed for the Centrala Trust for Ornithology (CTO) to assist the Centrala Environmental Agency (CEA) in urban planning. It allows residents to post sightings and upload pictures of birds within the Centrala municipality.

This application fulfills the requirements for the **ATHE Level 4 Extended Diploma in Computing, Unit 7: Web Design and Programming**.

## Features

### User Management
- **Registration**: New users can create an account to join the CTO message board.
- **Authentication**: Secure login using password hashing (`werkzeug.security`).
- **CLI Management**: A `manage_users.py` script is provided for administrative tasks like listing, creating, or deleting users.

### Bird Sighting Records (CRUD)
- **Create**: Log new sightings with details including location, time, date, species, activity, and duration.
- **Read**: View a chronological feed of all bird sightings.
- **Update**: Authors can edit their own posts to correct details or add comments.
- **Delete**: Authors can remove their own sightings and associated images.

### Advanced Functionality
- **Image Uploads**: Users can upload photographic evidence of sightings (supports `.jpg`, `.jpeg`, `.png` up to 1.2MB).
- **Dynamic Search**: Real-time keyword search implemented using HTMX to filter sightings by species, location, or comments without a full page reload.

## Technical Implementation & Learning Outcomes (LO)

The codebase includes specific annotations mapping to the assignment criteria:

- **LO3 AC 3.1 (Processing POST data)**: Demonstrated in the `/login` and `/register` routes in `app.py`.
- **LO3 AC 3.2 (Image Uploading)**: Implemented in the `/new_post` route with file type and size validation.
- **LO3 3M1 (CRUD Operations)**: Fully implemented for the `post` entity (Create, Read, Update, Delete).
- **LO3 3D1 (Security Mitigations)**:
    - **SQL Injection**: Prevented using parameterized queries in all database interactions.
    - **Path Traversal**: Prevented using `werkzeug.utils.secure_filename` for all uploaded files.

## Tech Stack

- **Backend**: Python 3.x with Flask
- **Frontend**: HTML5, CSS3, JavaScript, HTMX
- **Database**: SQLite3
- **Authentication**: Werkzeug Security (PBKDF2 with SHA256)

## Installation & Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Set up a virtual environment**:
    ```bash
    python -m venv .pyvenv
    source .pyvenv/bin/activate  # On Windows: .pyvenv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the database**:
    ```bash
    flask init-db
    ```

5.  **Run the application**:
    ```bash
    python app.py
    ```
    The application will be available at `http://127.0.0.1:5000`.

## Project Structure

- `app.py`: Main Flask application containing routes and logic.
- `schema.sql`: Database schema definition.
- `manage_users.py`: CLI tool for user account management.
- `static/`: Contains CSS, JavaScript, and uploaded images.
- `templates/`: Jinja2 templates for the frontend.
- `requirements.txt`: Python package dependencies.
