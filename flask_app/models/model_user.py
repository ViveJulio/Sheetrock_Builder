from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re

db = "sheetrock_builder_schema"

class User:

    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.yard = data['yard']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']


    @classmethod
    def save(cls, data):
        query = """
                INSERT INTO users (first_name, last_name, yard, email, password)
                VALUES (%(first_name)s, %(last_name)s, %(yard)s, %(email)s, %(pw_hash)s)
                """
        results = connectToMySQL(db).query_db(query, data)
        return results

    @classmethod
    def get_user_by_id(cls, user_id):
        query = """
                SELECT * FROM users
                WHERE id = %(id)s;
                """
        results = connectToMySQL(db).query_db(query, user_id)
        return cls(results[0])

    @classmethod
    def get_user_by_email(cls, user_email):
        query = """
                SELECT * FROM users
                WHERE email = %(email)s;
                """
        results = connectToMySQL(db).query_db(query, user_email)
        if len(results) < 1:
            return False
        return cls(results[0])


    @staticmethod
    def validate_user(user):
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        is_valid = True
        if len(user['first_name']) < 2:
            flash("Name must be at least 2 characters", 'register')
            is_valid = False
        if len(user['last_name']) < 2:
            flash("Name must be at least 2 characters", 'register')
            is_valid = False
        if len(user['yard']) < 0:
            flash("yard must not be blank", "register")
            is_valid = False
        if not EMAIL_REGEX.match(user['email']):
            flash('Invalid email address', 'register')
            is_valid = False
        query = """
                SELECT * FROM users
                WHERE email = %(email)s
                """
        results = connectToMySQL(db).query_db(query, user)
        if len(results) != 0:
            flash('This email is already being used', 'register')
            is_valid = False
        if len(user['password']) < 8:
            flash("Password must be at least 8 characters", 'register')
            is_valid = False
        if user['password'] != user['confirm_password']:
            flash("Password does not match", 'register')
            is_valid = False
        return is_valid