from flask_app import app
from flask import session, request, redirect
from flask_app.models.model_order import Order
from flask_app.models.model_build import Build

@app.route('/build_truck', methods=['POST'])
def build_truck():
    data = {
        'name' : request.form['name'],
        'lw12' : int(request.form['lw12']),
        'lw5412' : int(request.form['lw5412']),
        'fc12' : int(request.form['fc12']),
        'fc5412' : int(request.form['fc5412']),
        'm1212' : int(request.form['m1212']),
        'notes' : request.form['notes'],
        'user_id' : session['user_id']
    }
    if not Order.validate_order(data):
        return redirect('/new_order')
    order = Order.new_order(data)
    data['order_id'] = order
    Build.build_truck(data)
    return redirect(f'/view/{order}')

@app.route('/update/<int:order_id>', methods=['POST'])
def update(order_id):
    data = {
        'name' : request.form['name'],
        'lw12' : int(request.form['lw12']),
        'lw5412' : int(request.form['lw5412']),
        'fc12' : int(request.form['fc12']),
        'fc5412' : int(request.form['fc5412']),
        'm1212' : int(request.form['m1212']),
        'notes' : request.form['notes'],
        'user_id' : session['user_id']
    }
    if not Order.validate_order(data):
        return redirect(f'/edit_order/{order_id}')
    Order.update_order(data, order_id)
    data['order_id'] = order_id
    Build.update_build(data, order_id)
    return redirect(f'/view/{order_id}')
