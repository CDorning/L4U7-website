import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, g, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# --- Configuration ---
DATABASE = 'database.db'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
SECRET_KEY = 'a-super-secret-key-for-sessions' # In production, use a real, random key

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 1.2 * 1024 * 1024  # 1.2 MB max upload size

# --- Helper Functions ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        # LO3 AC 3.1: Reset the database with the updated schema
        print("Reading schema.sql and recreating tables...")
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        # LO3 3D1 Mitigation: VACUUM ensures the physical file size is reduced after dropping tables
        db.execute('VACUUM')
        db.commit()
        print("Database initialisation complete.")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Data for Forms ---
CENTRAL_REGIONS = ["Erean", "Brunad", "Bylyn", "Docia", "Marend", "Pryn", "Zord", "Yaean", "Frestin", "Stonyam", "Ryall", "Ruril", "Keivia", "Tallan", "Adohad", "Obelyn", "Holmer", "Vertwall"]
BIRD_SPECIES = ["Wood Pigeon", "House Sparrow", "Starling", "Blue Tit", "Blackbird", "Robin", "Goldfinch", "Magpie", "Other/Unknown"]
ACTIVITIES = ["Visit", "Feeding", "Nesting", "Other"]

# --- Hooks ---
@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute('SELECT id FROM user WHERE username = ?', (username,)).fetchone() is not None:
            error = f"User {username} is already registered."

        if error is None:
            # LO3 3M1: CRUD - Create (Registering a new user)
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

        flash(error, 'error')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # LO3 AC 3.1: Demonstrates processing of POSTed login credentials
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        # LO3 3M1: CRUD - Read (Authenticating a login)
        user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            flash('Login successful!', 'success')
            return redirect(url_for('posts'))

        flash(error, 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/posts')
def posts():
    db = get_db()
    all_posts = db.execute(
        'SELECT p.id, p.author_id, p.location, p.bird_species, p.time_obs, p.date_obs, p.activity, p.duration_mins, p.comments, p.image_filename, u.username '
        'FROM post p JOIN user u ON p.author_id = u.id ORDER BY p.created_at DESC'
    ).fetchall()
    return render_template('posts.html', posts=all_posts)

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form.get('search', '')
    db = get_db()
    query = """
        SELECT p.id, p.author_id, p.location, p.bird_species, p.time_obs, p.date_obs, p.activity, p.duration_mins, p.comments, p.image_filename, u.username
        FROM post p JOIN user u ON p.author_id = u.id
        WHERE p.bird_species LIKE ? OR p.location LIKE ? OR u.username LIKE ? OR p.comments LIKE ?
        ORDER BY p.created_at DESC
    """
    # LO3 3D1 Mitigation: Using parameterised queries to prevent SQL Injection
    like_pattern = f'%{search_term}%'
    results = db.execute(query, (like_pattern, like_pattern, like_pattern, like_pattern)).fetchall()
    # Return an HTML fragment for HTMX
    return render_template('_posts_list.html', posts=results)


@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    if g.user is None:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # LO3 3M1: CRUD - Create (Posting a new message)
        image_filename = None
        # LO3 AC 3.2: Demonstrates uploading an image
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                # LO3 3D1 Mitigation: Use secure_filename to prevent directory traversal
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename

        db = get_db()
        db.execute(
            """INSERT INTO post (location, time_obs, date_obs, bird_species, activity, duration_mins, comments, image_filename, author_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                request.form['location'], request.form['time_obs'], request.form['date_obs'],
                request.form['bird_species'], request.form['activity'], request.form['duration_mins'],
                request.form['comments'], image_filename, g.user['id']
            )
        )
        db.commit()
        flash('New sighting posted successfully!', 'success')
        return redirect(url_for('posts'))
        
    return render_template('new_post_form.html', regions=CENTRAL_REGIONS, birds=BIRD_SPECIES, activities=ACTIVITIES)

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if g.user is None:
        return redirect(url_for('login'))
    
    db = get_db()
    # Admins can edit any post; regular users can only edit their own
    if g.user['is_admin']:
        post = db.execute('SELECT * FROM post WHERE id = ?', (post_id,)).fetchone()
    else:
        post = db.execute('SELECT * FROM post WHERE id = ? AND author_id = ?', (post_id, g.user['id'])).fetchone()

    if post is None:
        flash('Post not found or you do not have permission to edit it.', 'error')
        return redirect(url_for('posts'))

    if request.method == 'POST':
        # LO3 3M1: CRUD - Update (Editing an existing message)
        db.execute(
            """UPDATE post SET location=?, time_obs=?, date_obs=?, bird_species=?, activity=?, duration_mins=?, comments=?
               WHERE id = ?""",
            (
                request.form['location'], request.form['time_obs'], request.form['date_obs'],
                request.form['bird_species'], request.form['activity'], request.form['duration_mins'],
                request.form['comments'], post_id
            )
        )
        db.commit()
        flash('Post updated successfully.', 'success')
        return redirect(url_for('posts'))
    
    return render_template('edit_post_form.html', post=post, regions=CENTRAL_REGIONS, birds=BIRD_SPECIES, activities=ACTIVITIES)

@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if g.user is None:
        return redirect(url_for('login'))

    db = get_db()
    # Admins can delete any post; regular users can only delete their own
    if g.user['is_admin']:
        post = db.execute('SELECT * FROM post WHERE id = ?', (post_id,)).fetchone()
    else:
        post = db.execute('SELECT * FROM post WHERE id = ? AND author_id = ?', (post_id, g.user['id'])).fetchone()
    
    if post:
        # LO3 3M1: CRUD - Delete (Deleting an existing message)
        if post['image_filename']:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post['image_filename']))
            except OSError as e:
                print(f"Error deleting file {post['image_filename']}: {e}")

        db.execute('DELETE FROM post WHERE id = ?', (post_id,))
        db.commit()
        flash('Post deleted successfully.', 'success')
    else:
        flash('Post not found or you do not have permission to delete it.', 'error')
    
    return redirect(url_for('posts'))


import click
from flask.cli import with_appcontext

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialised the database.')

app.cli.add_command(init_db_command)


if __name__ == '__main__':
    # init_db() # Run this once manually from the python shell to create the db
    # from app import init_db
    # init_db()
    app.run(debug=True)