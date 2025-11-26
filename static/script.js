
const books = [];


function addBook() {
    const bookTitle = document.getElementById("bookTitle").value.trim();
    const author = document.getElementById("bookAuthor").value.trim();
    const publicationYear = document.getElementById("publicationYear").value.trim();
    const imageUrl = document.getElementById("bookImage").value.trim();

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

    fetch("/api/add_book", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(bookData)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        books.push(bookData);
        displayBooks();

        document.getElementById("bookTitle").value = "";
        document.getElementById("bookAuthor").value = "";
        document.getElementById("publicationYear").value = "";
        document.getElementById("bookImage").value = "";
    })
    .catch(error => console.error("Error adding book:", error));
}

function searchBooks() {
    const query = document.getElementById("searchQuery").value.trim();

    if (!query) {
        alert("Please enter a search term.");
        return;
    }

    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            const bookList = document.getElementById("bookShelf");
            bookList.innerHTML = "";

            if (!data.books || data.books.length === 0) {
                bookList.innerHTML = `<p>No results found for "${query}".</p>`;
                return;
            }

            data.books.forEach(book => {
                const bookCard = document.createElement("div");
                bookCard.classList.add("book-card");

                
                bookCard.innerHTML = `
                    <div onclick="window.location.href='/book/${book.book_id}'">
                        <img src="${book.image_url || "https://via.placeholder.com/150"}" alt="${escapeHtml(book.title)}">
                        <h3>${escapeHtml(book.title)}</h3>
                        <p><strong>Author:</strong> ${escapeHtml(book.author || "Unknown")}</p>
                        <p><strong>Year:</strong> ${escapeHtml(book.publication_year || "N/A")}</p>
                    </div>
                `;

                bookList.appendChild(bookCard);
            });
        })
        .catch(error => console.error("Error searching books:", error));
}


function displayBooks() {
    const bookList = document.getElementById("bookList");
    bookList.innerHTML = "";

    books.forEach(book => {
        const bookElement = document.createElement("div");
        bookElement.classList.add("book-card");

        const id = book.book_id || book.id || "";

        bookElement.innerHTML = `
            <div onclick="if('${id}') window.location.href='/book/${id}'">
                <img src="${book.image_url || 'https://via.placeholder.com/150'}" alt="${escapeHtml(book.title)}">
                <h3>${escapeHtml(book.title)}</h3>
                <p><strong>Author:</strong> ${escapeHtml(book.author || 'Unknown')}</p>
                <p><strong>Year:</strong> ${escapeHtml(book.publication_year || 'N/A')}</p>
            </div>
        `;
        bookList.appendChild(bookElement);
    });
}


function showAllBooks() {
    Promise.all([
        fetch("/api/books").then(res => res.json()),
        fetch("/api/reviews").then(res => res.json())
    ])
    .then(([bookData, reviewData]) => {
        const shelf = document.getElementById("bookShelf");
        shelf.innerHTML = "";

        const reviews = reviewData.reviews || [];

        
        const allBooks = Array.isArray(bookData.books) ? bookData.books : [];

        allBooks.forEach(book => {
            
            const bookReviews = reviews.filter(r => r.book_id === book.book_id);

            const card = document.createElement("div");
            card.classList.add("book-card");

            card.innerHTML = `
                <div class="book-click" onclick="window.location.href='/book/${book.book_id}'">
                    <img src="${book.image_url || "https://via.placeholder.com/150"}" alt="${escapeHtml(book.title)}">
                    <h3>${escapeHtml(book.title)}</h3>
                    <p><strong>Author:</strong> ${escapeHtml(book.author || "Unknown")}</p>
                    <p><strong>Year:</strong> ${escapeHtml(book.publication_year || "N/A")}</p>
                </div>

                <h4>Reviews</h4>
                <div class="reviews-box">
                    ${
                        bookReviews.length
                        ? bookReviews.map(r => `
                            <p><strong>${escapeHtml(r.user)}</strong> — ${escapeHtml(String(r.rating))}/5</p>
                            <p>${escapeHtml(r.comment)}</p>
                            <hr>
                        `).join("")
                        : "<p>No reviews yet.</p>"
                    }
                </div>

                <button class="review-btn" onclick="toggleReviewForm(${book.book_id})">Add Review</button>

                <div id="review-form-${book.book_id}" class="review-form" style="display:none; margin-top:8px;">
                    <input type="text" id="reviewUser-${book.book_id}" placeholder="Your Name">
                    <input type="number" id="reviewRating-${book.book_id}" placeholder="Rating (1–5)" min="1" max="5">
                    <textarea id="reviewComment-${book.book_id}" placeholder="Write your review"></textarea>
                    <button onclick="submitReview(${book.book_id})">Submit Review</button>
                </div>
            `;

            shelf.appendChild(card);
        });
    })
    .catch(error => console.error("Error loading books or reviews:", error));
}


function toggleReviewForm(bookId) {
    const form = document.getElementById(`review-form-${bookId}`);
    if (!form) return;
    form.style.display = form.style.display === "none" ? "block" : "none";
}


function submitReview(bookId) {
    const user = document.getElementById(`reviewUser-${bookId}`).value.trim();
    const ratingRaw = document.getElementById(`reviewRating-${bookId}`).value;
    const rating = Number(ratingRaw);
    const comment = document.getElementById(`reviewComment-${bookId}`).value.trim();

    if (!user || !rating || !comment) {
        alert("Please fill out all review fields.");
        return;
    }

    const reviewData = { book_id: bookId, user, rating, comment };

    
    fetch("/api/add_review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(reviewData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Error adding review: " + data.error);
            console.error(data);
            return;
        }
        // refresh UI
        showAllBooks();
    })
    .catch(error => {
        console.error("Error submitting review:", error);
        alert("Failed to submit review.");
    });
}


function escapeHtml(str) {
    if (!str && str !== 0) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


document.addEventListener("DOMContentLoaded", () => {
    
    if (document.getElementById("bookShelf")) {
        showAllBooks();
    }
});
