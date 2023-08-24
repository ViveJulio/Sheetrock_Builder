from flask_app import app
from flask import render_template, redirect, g, session
from flask_app.models.model_order import Order
from flask_app.models.model_user import User

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id' : session['user_id']
    }
    user = User.get_user_by_id(data)
    all_orders = Order.get_all_orders_with_user_id(data)
    if len(all_orders) < 1:
        return render_template('dashboard.html', user = user, all_orders = all_orders)
    return render_template('dashboard.html', user = user, all_orders = all_orders, last_order = all_orders[0])

@app.route('/new_order')
def new_order():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id' : session['user_id']
    }
    user = User.get_user_by_id(data)
    return render_template('new_order.html', user = user)

@app.route('/all_orders')
def all_orders():
    if 'user_id' not in session:
        return redirect('/')
    user_data = {
        'id' : session['user_id']
    }
    user = User.get_user_by_id(user_data)
    all_orders = Order.get_all_orders_with_user_and_build()
    return render_template('community.html', user = user, all_orders = all_orders)

@app.route('/about')
def about():
    if 'user_id' not in session:
        return redirect('/')
    user_data = {
        'id' : session['user_id']
    }
    user = User.get_user_by_id(user_data)
    return render_template('about.html', user = user)


@app.route('/edit_order/<int:order_id>')
def edit_order(order_id):
    if 'user_id' not in session:
        return redirect('/')
    user_data = {
        'id' : session['user_id']
    }
    user = User.get_user_by_id(user_data)
    order = Order.get_order_by_id(order_id)
    return render_template('edit.html', order = order, user = user)

@app.route('/view/<int:order_id>')
def view(order_id):
    if 'user_id' not in session:
        return redirect('/')
    user_data = {
        'id' : session['user_id']
    }
    user = User.get_user_by_id(user_data)
    order = Order.get_order_by_id(order_id)
    return render_template('view.html', user = user, order = order)

@app.route('/delete_order/<int:order_id>')
def delete_order(order_id):
    Order.delete_order(order_id)
    return redirect('/dashboard')
