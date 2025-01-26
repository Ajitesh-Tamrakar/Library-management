from app import app, db  # Replace with your actual app and db import
from sqlalchemy import text

# Create a function to run the query
def run_query():
    with app.app_context():
        # Here you can write the SQL query
        query = text("""
            SELECT book.title AS book_title, book.author AS author,
                   "transaction".issue_date AS transaction_issue_date,
                   "transaction".return_date AS transaction_return_date,
                   user.name AS user_name
            FROM book 
            JOIN "transaction" ON "transaction".book_id = book.id 
            JOIN user ON user.id = "transaction".user_id
            WHERE "transaction".return_date IS NULL;
        """)

        # Execute the query
        result = db.session.execute(query)

        # Fetch and print the results
        rows = result.fetchall()
        for row in rows:
            print(dict(row))  # This will print each row as a dictionary

        # Close the session after the query execution
        db.session.close()

# Run the query
if __name__ == '__main__':
    run_query()
