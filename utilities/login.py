from flask import render_template, request, redirect, url_for, session
from forms import LoginForm
from utilities.storage import load_users

def handle_login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        users = load_users()
        username = form.username.data
        password = form.password.data
        session.setdefault('cart', [])
        session.setdefault('wishlist', [])

        print(f"Input Username: {username}, Input Password: {password}")  # Debugging
        print(f"Users: {users}")  # Debugging

        # Validate username and password against the JSON file (dictionary values)
        for user in users.values():
            if user.get('username') == username:
                if user.get('password') == password:
                    # Successful login
                    session['user'] = user
                    session.setdefault('cart', [])
                    session.setdefault('wishlist', [])
                    return redirect(url_for('index'))
                else:
                    # Password mismatch
                    return "Invalid password. Please try again."

        return "Invalid credentials. Try again."
    return render_template('login.html', form=form)