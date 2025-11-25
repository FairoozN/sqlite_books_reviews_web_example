from flask import Flask, jsonify, render_template, request
import sqlite3

app = Flask(__name__)

# Define the path to your SQLite database file
DATABASE = 'db/books.db'

@app.route('/api/books', methods=['GET'])
def get_all_books():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT B.book_id, B.title, B.publication_year, A.name, B.image_url
            FROM Books B
            LEFT JOIN book_author BA ON B.book_id = BA.book_id
            LEFT JOIN Authors A ON BA.author_id = A.author_id
        ''')
        books = cursor.fetchall()
        conn.close()

        # Convert the list of tuples into a list of dictionaries
        book_list = []
        for book in books:
            book_dict = {
                'book_id': book[0],
                'title': book[1],
                'publication_year': book[2],
                'author': book[3],
                'image_url': book[4]
            }

            # Add other attributes here as needed
            book_list.append(book_dict)

        return jsonify({'books': book_list})
    except Exception as e:
        return jsonify({'error': str(e)})


# API to get all authors
@app.route('/api/authors', methods=['GET'])
def get_all_authors():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Authors")
        authors = cursor.fetchall()
        conn.close()
        return jsonify(authors)
    except Exception as e:
        return jsonify({'error': str(e)})

# API to get all reviews
@app.route('/api/reviews', methods=['GET'])
def get_all_reviews():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Reviews")
        reviews = cursor.fetchall()
        conn.close()
        return jsonify(reviews)
    except Exception as e:
        return jsonify({'error': str(e)})

# API to add a book to the database
@app.route('/api/add_book', methods=['POST'])
def add_book():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Get book details from the request
        data = request.get_json()
        title = data.get('title')
        publication_year = data.get('publication_year')
        author_name = data.get('author')
        image_url = data.get('image_url')

        # Insert the book into the database
        cursor.execute("INSERT INTO Books (title, publication_year, image_url) VALUES (?, ?, ?)", (title, publication_year, image_url))
        book_id = cursor.lastrowid

        cursor.execute("SELECT author_id FROM Authors WHERE name = ?", (author_name,))
        row = cursor.fetchone()
        if row:
            author_id = row[0]
        else:
            cursor.execute("INSERT INTO Authors (name) VALUES (?)", (author_name,))
            author_id = cursor.lastrowid

        # Link book and author
        cursor.execute("INSERT INTO book_author (book_id, author_id) VALUES (?, ?)", (book_id, author_id))

        conn.commit()
        conn.close()


        return jsonify({'message': 'Book and Author added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

# Route to render the index.html page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print("Running on port 5001")
    app.run(debug=True, host="0.0.0.0", port=5001)
