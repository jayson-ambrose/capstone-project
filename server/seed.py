#!/usr/bin/env python3

# Standard library imports
from random import randint, choice as rc
import datetime

# Remote library imports
from faker import Faker

# Local imports
from app import app
from models import db, User, Book, Review, Backlog

if __name__ == '__main__':
    fake = Faker()
    with app.app_context():

        print("Removing old data...")        
        User.query.delete()
        Book.query.delete()
        Review.query.delete()
        Backlog.query.delete()

        b1 = Book(title='Booktime', author='Dudman Jr', isbn='1357845638')
        b2 = Book(title='Tacos', author='Pooboot', isbn='1354843216')
        b3 = Book(title='Burritos', author='Durganisom Tomison', isbn='13545421')

        books = [b1, b2, b3]

        u1 = User(username='jayson', password='password')
        u2 = User(username='dillon', password='password')
        u3 = User(username='kelsey', password='password')
        u4 = User(username='zach', password='password')

        users = [u1, u2, u3, u4]

        r1 = Review(rating=7, review_text='Taco salad is delicious, so is this book', user_id=1, book_id=2)
        r2 = Review(rating=3, review_text='I dont know about this one', user_id=4, book_id=2)
        r3 = Review(rating=5, review_text='Im sure this one was okay', user_id=1, book_id=2)

        reviews = [r1, r2, r3]

        bl1 = Backlog(completed=1, user_id=3, book_id=2)
        bl2 = Backlog(completed=0, user_id=2, book_id=1)
        bl3 = Backlog(completed=1, user_id=1, book_id=3)

        backlogs = [bl1, bl2, bl3]

        db.session.add_all(books)
        db.session.add_all(users)
        db.session.commit()
        
        db.session.add_all(reviews)
        db.session.add_all(backlogs)
        db.session.commit()