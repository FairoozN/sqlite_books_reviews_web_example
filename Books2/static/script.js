
const books = [];


function addBook() {
    const bookTitle = document.getElementById('bookTitle').value.trim();
    const author = document.getElementById('bookAuthor').value.trim();
    const publicationYear = document.getElementById('publicationYear').value.trim();
    const imageUrl = document.getElementById('bookImage').value.trim();

    // Validation
    if (!bookTitle || !author) {
        alert("Please enter both a title and an author.");
        return;
    }

    const bookData = {
        title: bookTitle,
        author: author,
        publication_year: publicationYear,
        image_url: imageUrl
    };

    
    fetch('/api/add_book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bookData)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        books.push(bookData);
        displayBooks();

        // Clear form fields
        document.getElementById('bookTitle').value = '';
        document.getElementById('bookAuthor').value = '';
        document.getElementById('publicationYear').value = '';
        document.getElementById('bookImage').value = '';
    })
    .catch(error => {
        console.error('Error adding book:', error);
    });
}

function searchBooks() {
    const query = document.getElementById('searchQuery').value.trim();

    if (!query) {
        alert("Please enter a search term.");
        return;
    }

    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            console.log("Search results:", data); 
            const bookList = document.getElementById('bookShelf');
            bookList.innerHTML = ''; 

            if (!data.books) {
                bookList.innerHTML = `<p>No books field found in response. Check backend.</p>`;
                return;
            }

            if (data.books.length === 0) {
                bookList.innerHTML = `<p>No results found for "${query}".</p>`;
                return;
            }

            data.books.forEach(book => {
                const bookCard = document.createElement('div');
                bookCard.classList.add('book-card');
                bookCard.innerHTML = `
                    <img src="${book.image_url || 'https://via.placeholder.com/150'}" alt="${book.title}">
                    <h3>${book.title}</h3>
                    <p><strong>Author:</strong> ${book.author || 'Unknown'}</p>
                    <p><strong>Year:</strong> ${book.publication_year || 'N/A'}</p>
                `;
                bookList.appendChild(bookCard);
            });
        })
        .catch(error => {
            console.error('Error searching books:', error);
        });
}


function displayBooks() {
    const bookList = document.getElementById('bookList');
    bookList.innerHTML = '';

    books.forEach(book => {
        const bookElement = document.createElement('div');
        bookElement.classList.add('book-card');
        bookElement.innerHTML = `
            <img src="${book.image_url || 'https://via.placeholder.com/150'}" alt="${book.title}">
            <h3>${book.title}</h3>
            <p><strong>Author:</strong> ${book.author || 'Unknown'}</p>
            <p><strong>Year:</strong> ${book.publication_year || 'N/A'}</p>
        `;
        bookList.appendChild(bookElement);
    });
}


function showAllBooks() {
    fetch('/api/books')
        .then(response => response.json())
        .then(data => {
            const shelf = document.getElementById('bookShelf');
            shelf.innerHTML = ''; 
            console.log(data);

            data.books.forEach(book => {
                const card = document.createElement('div');
                card.classList.add('book-card');
                card.innerHTML = `
                    <img src="${book.image_url || 'https://via.placeholder.com/150'}" alt="${book.title}">
                    <h3>${book.title}</h3>
                    <p><strong>Author:</strong> ${book.author || 'Unknown'}</p>
                    <p><strong>Year:</strong> ${book.publication_year || 'N/A'}</p>
                `;
                shelf.appendChild(card);
            });
        })
        .catch(error => {
            console.error('Error fetching all books:', error);
        });
}
