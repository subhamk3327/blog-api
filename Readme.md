# Blog API
A REST API for a blog platform secured with JWT Authentication

## Features
- User Registration and Login with password hashing
- Full CRUD operations on posts, comments and likes
- JWT based authentication (15 minutes expiry)
- Unique likes per user enforced at database level
- Unique username enforcement on registration
- Timestamps on comments
- PostgreSQL for data storage

## Tech Stack
- FastAPI (Python)
- bcrypt (password hashing)
- python-jose (JWT authentication)
- PostgreSQL (database)
- psycopg2 (database driver)

## Setup

### Requirements
- Python 3.12 and above
- PostgreSQL installed and running

### Installation
1. Clone the repository:
```bash
git clone https://github.com/subhamk3327/blog-api.git
cd blog-api
```
(clones the code onto your pc and then switches the terminal to current code folder)

2. Install dependencies:
```bash
python -m pip install -r requirements.txt
```
(installs required dependencies to run the code)

3. Create a `.env` file with:
```
SECRET_KEY = insert_your_secret_key_here
DATABASE_URL = postgresql://postgres:your_password@localhost:5432/blogdb
```
(create a file with extension of .env and edit it with notepad/editor with the above lines. change the phrase according to your secret key and postgres password)

4. Create database tables with the following:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    CONSTRAINT unique_username UNIQUE(username)
);

CREATE TABLE post (
    id SERIAL PRIMARY KEY,
    heading TEXT NOT NULL,
    content TEXT NOT NULL,
    user_id INTEGER
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    comment TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    post_id INTEGER NOT NULL
);

CREATE TABLE likes (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    CONSTRAINT unique_like UNIQUE(post_id, user_id)
);
```
(sets up the database)

5. Run server with the following command:
```bash
python -m uvicorn blog:app --reload
```
(starts local server with the url - `http://127.0.0.1:8000`)