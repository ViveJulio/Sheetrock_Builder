from flask_app import app
from flask import Flask, request, render_template, redirect, session, flash
from flask_app.models.model_user import User
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/login_page')
def login_page():
    return render_template('login.html')

# register
@app.route('/register', methods=['POST'])
def register():
    data = {
        'first_name' : request.form['first_name'],
        'last_name' : request.form['last_name'],
        'yard' : request.form['yard'],
        'email' : request.form['email'],
        'password' : request.form['password'],
        'confirm_password' : request.form['confirm_password']
    }
    if not User.validate_user(data):
        return redirect('/')

    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    print(pw_hash)
    data['pw_hash'] = pw_hash
    session['user_id'] = User.save(data)

    return redirect('/dashboard')
# end register

#login
@app.route('/login', methods=['POST'])
def login():
    user = User.get_user_by_email(request.form)

    if not user:
        flash('Invalid email or password', 'login')
        return redirect('/login_page')

    if not bcrypt.check_password_hash(user.password, request.form['password']):
        flash('Invalid email or password', 'login')
        return redirect('/login_page')

    session['user_id'] = user.id
    return redirect('/dashboard')
# end login


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/profile')
def profile():
    user_data = {
        'id' : session['user_id']
    }
    user = User.get_user_by_id(user_data)
    return render_template('profile.html', user= user)

@app.route('/edit_profile')
def edit_profile():
    user_data = {
        'id' : session['user_id']
    }
    user = User.get_user_by_id(user_data)
    return render_template('edit_profile.html', user = user)