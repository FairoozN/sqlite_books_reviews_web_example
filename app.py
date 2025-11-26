from flask import Flask, jsonify, render_template, request, redirect, url_for
import sqlite3
import pymongo
import mysql.connector
import time
import os

app = Flask(__name__)

DATABASE = 'db/books.db'
app.config['DATABASE'] = DATABASE

import certifi

MONGO_URI = "mongodb+srv://coolismebro_db_user:ifV2xR3bKu6VkcsH@cluster0.avxrasj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = pymongo.MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where()
)

mongo_db = client["book_database"]
reviews_collection = mongo_db["reviews"]





def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="NewPassword123!",
        database="books"
    )


def log_to_mysql(function_name, status, execution_time=None, error_message=None):
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO logs (function_name, status, execution_time, error_message)
            VALUES (%s, %s, %s, %s)
        """, (function_name, status, execution_time, error_message))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as log_err:
        print(f"Logging error: {log_err}")


# ---------------------------
# SQLITE
# ---------------------------
def get_db_connection():
    db_path = app.config.get('DATABASE', DATABASE)
    return sqlite3.connect(db_path)


# ---------------------------
# API ROUTES
# ---------------------------

@app.route('/api/books', methods=['GET'])
def get_all_books():
    start = time.time()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT B.book_id, B.title, B.publication_year, A.name, B.image_url
            FROM Books B
            LEFT JOIN book_author BA ON B.book_id = BA.book_id
            LEFT JOIN Authors A ON BA.author_id = A.author_id
        ''')
        books = cursor.fetchall()
        conn.close()

        book_list = [{
            'book_id': b[0],
            'title': b[1],
            'publication_year': b[2],
            'author': b[3],
            'image_url': b[4]
        } for b in books]

        exec_time = time.time() - start
        log_to_mysql('get_all_books', 'success', exec_time)
        return jsonify({'books': book_list})
    except Exception as e:
        log_to_mysql('get_all_books', 'error', None, str(e))
        return jsonify({'error': str(e)})


@app.route('/api/reviews', methods=['GET'])
def get_all_reviews():
    start = time.time()
    try:
        reviews = list(reviews_collection.find({}, {"_id": 0}))
        exec_time = time.time() - start
        log_to_mysql('get_all_reviews', 'success', exec_time)
        return jsonify({'reviews': reviews})
    except Exception as e:
        log_to_mysql('get_all_reviews', 'error', None, str(e))
        return jsonify({'error': str(e)})


@app.route('/api/add_review', methods=['POST'])
def add_review_api():
    start = time.time()
    try:
        data = request.get_json()
        review = {
            'book_id': data.get('book_id'),
            'user': data.get('user'),
            'rating': data.get('rating'),
            'comment': data.get('comment')
        }
        reviews_collection.insert_one(review)

        exec_time = time.time() - start
        log_to_mysql('add_review', 'success', exec_time)
        return jsonify({'message': 'Review added successfully'})
    except Exception as e:
        log_to_mysql('add_review', 'error', None, str(e))
        return jsonify({'error': str(e)})


@app.route('/api/add_book', methods=['POST'])
def add_book():
    start = time.time()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        data = request.get_json()
        title = data.get('title')
        publication_year = data.get('publication_year')
        author_name = data.get('author')
        image_url = data.get('image_url')

        if not title or not author_name:
            return jsonify({'error': 'Title and Author are required fields.'}), 400

        cursor.execute(
            "INSERT INTO Books (title, publication_year, image_url) VALUES (?, ?, ?)",
            (title, publication_year, image_url)
        )
        book_id = cursor.lastrowid

        cursor.execute("SELECT author_id FROM Authors WHERE name = ?", (author_name,))
        row = cursor.fetchone()
        if row:
            author_id = row[0]
        else:
            cursor.execute("INSERT INTO Authors (name) VALUES (?)", (author_name,))
            author_id = cursor.lastrowid

        cursor.execute("INSERT INTO book_author (book_id, author_id) VALUES (?, ?)", 
                       (book_id, author_id))
        conn.commit()
        conn.close()

        exec_time = time.time() - start
        log_to_mysql('add_book', 'success', exec_time)
        return jsonify({'message': 'Book and Author added successfully'})
    except Exception as e:
        log_to_mysql('add_book', 'error', None, str(e))
        return jsonify({'error': str(e)})



@app.route('/book/<int:book_id>')
def book_details(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT book_id, title, publication_year, image_url
        FROM Books WHERE book_id = ?
    """, (book_id,))
    book = cursor.fetchone()
    conn.close()

    reviews = list(reviews_collection.find({"book_id": book_id}))

    return render_template("book_details.html", book=book, reviews=reviews)


@app.route('/add_review/<int:book_id>', methods=['POST'])
def add_review_form(book_id):
    user = request.form["user"]
    rating = int(request.form["rating"])
    comment = request.form["comment"]

    reviews_collection.insert_one({
        "book_id": book_id,
        "user": user,
        "rating": rating,
        "comment": comment
    })

    return redirect(url_for("book_details", book_id=book_id))


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    print("Running on port 5001")
    app.run(debug=True, host="0.0.0.0", port=5001)


