from flask import Flask, request, jsonify, render_template
from app import app, db
from model import Book, User, Transaction
from datetime import datetime
from sqlalchemy.orm import aliased

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/init', methods=['GET'])
def init_db():
    db.create_all()
    return "Database and tables initialized successfully!"

@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    try:
        # Ensure required fields are present
        if 'title' not in data or 'author' not in data:
            return jsonify({"error": "Title and author are required"}), 400

        # Create and add a new book
        new_book = Book(title=data['title'], author=data['author'], available=True)
        db.session.add(new_book)
        db.session.commit()

        # Log book details for debugging
        app.logger.info(f"Book added: ID={new_book.id}, Title={new_book.title}, Author={new_book.author}")

        return jsonify({
            "msg": "Book is added successfully!",
            "book": {
                "id": new_book.id,
                "title": new_book.title,
                "author": new_book.author,
                "available": new_book.available
            }
        }), 201
    except Exception as e:
        # Rollback and log errors
        db.session.rollback()
        app.logger.error(f"Error adding book: {e}")
        return jsonify({"error": "Failed to add book"}), 500


@app.route('/books', methods=['GET'])
def get_books():
    try:
        books = Book.query.all()
        return jsonify([{
            "id": b.id,
            "title": b.title,
            "author": b.author,
            "available": b.available
        } for b in books])

    except Exception as e:
        # Rollback and log errors
        db.session.rollback()
        app.logger.error(f"Error fetching books: {e}")
        return jsonify({"error": "Failed to fetch books"}), 500

@app.route('/issue_book', methods=['POST'])
def issue_book():
    data = request.json
    book_id = data.get('book_id')
    user_id = data.get('user_id')

    # Check if both book_id and user_id are provided
    if not book_id or not user_id:
        app.logger.error("book_id or user_id not provided")
        return jsonify({"error": "Both book_id and user_id are required"}), 400

    # Check if the book and user exist
    book = Book.query.get(book_id)
    user = User.query.get(user_id)

    if not book:
        app.logger.error(f"Book with ID {book_id} not found")
        return jsonify({"error": "Book not found"}), 404
    if not user:
        app.logger.error(f"User with ID {user_id} not found")
        return jsonify({"error": "User not found"}), 404

    # Check if the book is already issued (not available)
    if not book.available:
        app.logger.error(f"Book with ID {book_id} is already issued")
        return jsonify({"error": "Book is already issued to someone else"}), 400

    # Create a new transaction with the current time as the issue date
    transaction = Transaction(book_id=book_id, user_id=user_id, issue_date=datetime.utcnow())
    app.logger.info(f"Created transaction: {transaction}")

    # Update the book's availability status to False (issued)
    book.available = False
    app.logger.info(f"Book with ID {book_id} availability set to False")

    # Add the transaction and commit the changes to the database
    try:
        db.session.add(transaction)
        db.session.commit()
        app.logger.info(f"Transaction committed successfully: {transaction.id}")

        return jsonify({
            "msg": "Book issued successfully!",
            "transaction": {
                "id": transaction.id,
                "book_id": transaction.book_id,
                "user_id": transaction.user_id,
                "issue_date": transaction.issue_date,
                "return_date": transaction.return_date
            }
        }), 201
    except Exception as e:
        # Rollback and log errors
        db.session.rollback()
        app.logger.error(f"Error committing transaction: {e}")
        return jsonify({"error": "Failed to issue book"}), 500


@app.route('/transaction/return', methods=['POST'])
def return_book():
    data = request.json
    book_id = data.get('book_id')
    user_id = data.get('user_id')

    if not book_id or not user_id:
        return jsonify({"error": "Both book_id and user_id are required"}), 400

    transaction = Transaction.query.filter_by(book_id=book_id, user_id=user_id, return_date=None).first()
    if transaction:
        transaction.return_date = datetime.utcnow()
        book = Book.query.get(transaction.book_id)
        book.available = True
        db.session.commit()
        return jsonify({"message": "Book returned successfully!"})
    return jsonify({"error": "No such transaction found"}), 400

@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    if 'name' not in data or 'email' not in data:
        return jsonify({"error": "Name and email are required"}), 400
    
    # Check if email is already registered
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 400

    try:
        # Add the new user
        new_user = User(name=data['name'], email=data['email'])
        db.session.add(new_user)
        db.session.commit()

        # Log the new user ID for debugging
        app.logger.info(f"New user added with ID: {new_user.id}")

        return jsonify({
            "msg": "User added successfully!",
            "user": {
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email
            }
        }), 201
    except Exception as e:
        # Rollback on error
        db.session.rollback()
        app.logger.error(f"Error adding user: {e}")
        return jsonify({"error": "Failed to add user"}), 500


@app.route('/issued_books', methods=['GET'])
def get_issued_books():
    try:
        # Query the issued books, joining with users and books
        issued_books = db.session.query(
            Book.title.label("book_title"),
            Book.author.label("author"),
            Transaction.issue_date,
            Transaction.return_date,
            User.name.label("user_name")
        ).join(Transaction, Transaction.book_id == Book.id).join(User, User.id == Transaction.user_id).filter(
            Transaction.return_date.is_(None)  # Only currently issued books
        ).all()

        # Log the issued books for debugging
        app.logger.debug(f"Issued Books: {issued_books}")

        # Format the response
        return jsonify([{
            "book_title": book.book_title,
            "author": book.author,
            "issue_date": book.issue_date,
            "return_date": book.return_date,
            "user_name": book.user_name
        } for book in issued_books])

    except Exception as e:
        app.logger.error(f"Error fetching issued books: {e}")
        return jsonify({"error": "Failed to fetch issued books"}), 500


@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return jsonify([{
            "id": user.id,
            "name": user.name,
            "email": user.email
        } for user in users])

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error fetching users: {e}")
        return jsonify({"error": "Failed to fetch users"}), 500
