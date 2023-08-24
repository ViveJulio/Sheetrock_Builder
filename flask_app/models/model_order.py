from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models.model_user import User
from flask_app.models.model_build import Build

db = "sheetrock_builder_schema"

class Order:

    def __init__(self, data):
        self.id = data['id']
        self.user_id = data['user_id']
        self.name = data['name']
        self.lw12 = data['lw12']
        self.lw5412 = data['lw5412']
        self.fc12 = data['fc12']
        self.fc5412 = data['fc5412']
        self.notes = data['notes']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

        self.user = None
        self.build = None


    @classmethod
    def new_order(cls, data):
        query = """
                INSERT INTO orders (name, lw12, lw5412, fc12, fc5412, notes, user_id)
                VALUES (%(name)s, %(lw12)s, %(lw5412)s, %(fc12)s, %(fc5412)s, %(notes)s, %(user_id)s)
                """
        results = connectToMySQL(db).query_db(query, data)
        return results

    @classmethod
    def update_order(cls, data, order_id):
        query =f"""
                UPDATE orders
                SET name = %(name)s, lw12 = %(lw12)s, lw5412 = %(lw5412)s, fc12 = %(fc12)s, fc5412 = %(fc5412)s, notes = %(notes)s, user_id = %(user_id)s
                WHERE id = {order_id};
                """
        results = connectToMySQL(db).query_db(query, data)
        return results

    @classmethod
    def delete_order(cls, order_id):
        query = """
                DELETE FROM orders
                WHERE id = %(id)s
                """
        results = connectToMySQL(db).query_db(query, {'id' : order_id})
        return results

    @classmethod
    def get_order_by_id(cls, order_id):
        query = """
                SELECT * FROM orders
                JOIN builds
                ON builds.order_id = orders.id
                WHERE orders.id = %(id)s
                """
        results = connectToMySQL(db).query_db(query, {'id' : order_id})
        order = cls(results[0])
        order_data = {
                'id' : results[0]['builds.id'],
                'name' : results[0]['name'],
                'lw5412' : results[0]['lw5412'],
                'fc5412' : results[0]['fc5412'],
                'lw12' : results[0]['lw12'],
                'fc12' : results[0]['fc12']
            }
        build_data = {
                'id' : results[0]['builds.id'],
                'order_id' : results[0]['order_id'],
                'lw5412p' : results[0]['lw5412p'],
                'lw5412r' : results[0]['lw5412r'],
                'fc5412p' : results[0]['fc5412p'],
                'fc5412r' : results[0]['fc5412r'],
                'lw12p' : results[0]['lw12p'],
                'lw12r' : results[0]['lw12r'],
                'fc12p' : results[0]['fc12p'],
                'fc12r' : results[0]['fc12r']
            }
        order.build = Build(build_data)
        order.build.remainder_pick = Build.build_truck(order_data)
        return order

    @classmethod
    def get_all_orders_with_user_id(cls, user_id):
        query = """
                SELECT * FROM orders
                JOIN builds
                ON builds.order_id = orders.id
                WHERE orders.user_id = %(id)s
                """
        results = connectToMySQL(db).query_db(query, user_id)
        all_orders = []
        for row in results:
            order = cls(row)
            order_data = {
                'id' : row['builds.id'],
                'name' : row['name'],
                'lw5412' : row['lw5412'],
                'fc5412' : row['fc5412'],
                'lw12' : row['lw12'],
                'fc12' : row['fc12']
            }
            build_data = {
                'id' : row['builds.id'],
                'order_id' : row['order_id'],
                'lw5412p' : row['lw5412p'],
                'lw5412r' : row['lw5412r'],
                'fc5412p' : row['fc5412p'],
                'fc5412r' : row['fc5412r'],
                'lw12p' : row['lw12p'],
                'lw12r' : row['lw12r'],
                'fc12p' : row['fc12p'],
                'fc12r' : row['fc12r']
            }
            build = Build(build_data)
            build.remainder_pick = build.build_truck(order_data)
            order.build = build
            all_orders.insert(0, order)
        return all_orders

    @classmethod
    def get_all_orders_with_user_and_build(cls):
        query = """
                SELECT * FROM orders
                JOIN users
                ON orders.user_id = users.id
                JOIN builds
                ON builds.order_id = orders.id
                """
        results = connectToMySQL(db).query_db(query)
        all_orders = []
        for row in results:
            order = cls(row)
            order_data = {
                'id' : row['builds.id'],
                'name' : row['name'],
                'lw5412' : row['lw5412'],
                'fc5412' : row['fc5412'],
                'lw12' : row['lw12'],
                'fc12' : row['fc12']
            }
            user_data = {
                'id' : row['users.id'],
                'first_name' : row['first_name'],
                'last_name' : row['last_name'],
                'yard' : row['yard'],
                'email' : row['email'],
                'password' : row['password'],
                'created_at' : row['users.created_at'],
                'updated_at' : row['users.updated_at']
            }
            build_data = {
                'id' : row['builds.id'],
                'order_id' : row['order_id'],
                'lw5412p' : row['lw5412p'],
                'lw5412r' : row['lw5412r'],
                'fc5412p' : row['fc5412p'],
                'fc5412r' : row['fc5412r'],
                'lw12p' : row['lw12p'],
                'lw12r' : row['lw12r'],
                'fc12p' : row['fc12p'],
                'fc12r' : row['fc12r']
            }
            user = User(user_data)
            build = Build(build_data)
            build.remainder_pick = build.build_truck(order_data)
            order.user = user
            order.build = build
            all_orders.insert(0, order)
        return all_orders

    @staticmethod
    def validate_order(order):
        is_valid = True
        if len(order['name']) < 1:
            flash('Name must not be blank')
            is_valid = False
        if order['lw12'] < 0:
            flash('quantity must not be negative')
            is_valid = False
        if order['lw5412'] < 0:
            flash('quantity must not be negative')
            is_valid = False
        if order['fc12'] < 0:
            flash('quantity must not be negative')
            is_valid = False
        if order['fc5412'] < 0:
            flash('quantity must not be negative')
            is_valid = False
        return is_valid