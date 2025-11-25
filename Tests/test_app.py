import os
import sys
import sqlite3
import tempfile
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app


@pytest.fixture
def client():
    """Setup a temporary SQLite DB file that persists for both Flask and the test."""
    app.config['TESTING'] = True

    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    app.config['DATABASE'] = db_path
    client = app.test_client()

  
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS Authors (
            author_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Books (
            book_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            publication_year INTEGER,
            image_url TEXT
        );

        CREATE TABLE IF NOT EXISTS book_author (
            book_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            PRIMARY KEY (book_id, author_id),
            FOREIGN KEY (book_id) REFERENCES Books (book_id),
            FOREIGN KEY (author_id) REFERENCES Authors (author_id)
        );
    """)
    conn.commit()
    conn.close()

    yield client  


    os.close(db_fd)
    os.remove(db_path)


def test_add_book_integration(client):
    book_data = {
        "title": "Suffs",
        "author": "Shaina Taub",
        "publication_year": 2022,
        "image_url": "https://example.com/test_image.jpg"
    }

    response = client.post('/api/add_book', json=book_data)
    assert response.status_code in (200, 201)
    data = response.get_json()
    assert "message" in data
    assert "added" in data["message"].lower()


    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("SELECT title, publication_year, image_url FROM Books")
    stored_book = cursor.fetchone()
    cursor.execute("SELECT name FROM Authors")
    stored_author = cursor.fetchone()
    conn.close()

    assert stored_book is not None
    assert stored_author is not None
    assert stored_book[0] == "Suffs"
    assert stored_book[1] == 2022
    assert stored_book[2].startswith("https://")
    assert stored_author[0] == "Shaina Taub"


def test_get_books(client):
    client.post('/api/add_book', json={
        "title": "Suffs",
        "author": "Shaina Taub",
        "publication_year": 2022,
        "image_url": "https://example.com/test_image.jpg"
    })

    response = client.get('/api/books')
    assert response.status_code == 200
    data = response.get_json()
    assert "books" in data
    assert len(data["books"]) > 0
    book = data["books"][0]
    assert book["title"] == "Suffs"
    assert book["author"] == "Shaina Taub"
    assert book["publication_year"] == 2022
    assert book["image_url"].startswith("https://")


def test_search_books(client):
    client.post('/api/add_book', json={
        "title": "Suffs",
        "author": "Shaina Taub",
        "publication_year": 2022,
        "image_url": "https://example.com/test_image.jpg"
    })

   
    response = client.get('/api/search?q=Suffs')
    data = response.get_json()
    assert len(data["books"]) >= 1
    assert any(book["title"] == "Suffs" for book in data["books"])

   
    response = client.get('/api/search?q=Shaina')
    data = response.get_json()
    assert len(data["books"]) >= 1
    assert any(book["author"] == "Shaina Taub" for book in data["books"])

    # Edge case: Search for non-existent book
    response = client.get('/api/search?q=NonExistent')
    data = response.get_json()
    assert len(data["books"]) == 0
