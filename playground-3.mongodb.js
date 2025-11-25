

use("book_database");




db.reviews.insertMany([
  {
    book_id: 3,
    user: "Fairooz",
    rating: 5,
    comment: "Excellent read!"
  },
  {
    book_id: 4,
    user: "Jane",
    rating: 4,
    comment: "Well-written and engaging."
  },
  {
    book_id: 5,
    user: "Paul",
    rating: 3,
    comment: "Interesting premise but a bit slow in parts."
  },
  {
    book_id: 6,
    user: "Alex",
    rating: 5,
    comment: "Loved the writing style and characters!"
  },
]);

