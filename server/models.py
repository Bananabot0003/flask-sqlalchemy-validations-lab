import re

from flask import has_app_context
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates


db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    phone_number = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    @validates('name')
    def validate_name(self, key, name):
        if not isinstance(name, str) or not name.strip():
            raise ValueError('An author name is required.')

        if has_app_context():
            query = Author.query.filter_by(name=name)
            if self.id is not None:
                query = query.filter(Author.id != self.id)
            with db.session.no_autoflush:
                if query.first() is not None:
                    raise ValueError('That author name is already in use.')
        return name

    @validates('phone_number')
    def validate_phone_number(self, key, phone_number):
        if not isinstance(phone_number, str) or not re.fullmatch(r'[0-9]{10}', phone_number):
            raise ValueError('Phone number must contain exactly ten digits.')
        return phone_number

    def __repr__(self):
        return f'Author(id={self.id}, name={self.name})'


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String)
    category = db.Column(db.String)
    summary = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    @validates('title')
    def validate_title(self, key, title):
        phrases = ("Won't Believe", "Secret", "Top", "Guess")
        if not isinstance(title, str) or not any(phrase in title for phrase in phrases):
            raise ValueError("The title must contain Won't Believe, Secret, Top, or Guess.")
        return title

    @validates('content')
    def validate_content(self, key, content):
        if not isinstance(content, str) or len(content) < 250:
            raise ValueError('Post content must be at least 250 characters.')
        return content

    @validates('category')
    def validate_category(self, key, category):
        if category not in ('Fiction', 'Non-Fiction'):
            raise ValueError('Category must be Fiction or Non-Fiction.')
        return category

    @validates('summary')
    def validate_summary(self, key, summary):
        if summary is not None and (not isinstance(summary, str) or len(summary) > 250):
            raise ValueError('Post summary must contain at most 250 characters.')
        return summary

    def __repr__(self):
        return f'Post(id={self.id}, title={self.title} content={self.content}, summary={self.summary})'
