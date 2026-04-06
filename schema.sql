-- Drop tables if they exist to ensure a clean slate
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS user;

-- User table to store login credentials
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

-- Post table to store bird sighting data
CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  location TEXT NOT NULL,
  time_obs TEXT NOT NULL,
  date_obs TEXT NOT NULL,
  bird_species TEXT NOT NULL,
  activity TEXT NOT NULL,
  duration_mins INTEGER NOT NULL,
  comments TEXT,
  image_filename TEXT,
  FOREIGN KEY (author_id) REFERENCES user (id)
);