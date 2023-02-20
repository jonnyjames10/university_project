from flask import render_template, url_for, request, redirect, flash
from education import app, db
from education.models import User, RoleMember
from education.forms import RegistrationForm, LoginForm
from flask_login import login_user, logout_user, login_required, current_user

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        user = User(first_name = form.first_name.data,
            last_name = form.last_name.data, email = form.email.data,
            password = form.password.data, date_of_birth = form.date_of_birth.data)
        db.session.add(user)
        db.session.commit()

        user = User.query.filter_by(email=form.email.data).first()
        role = RoleMember(user_id = user.id, role_id = 1) # Automatically sets role of the user to a student
        db.session.add(role)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('register.html', title='Register',
        form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/primary_school")
def primary_school():
    return render_template('primary_school.html')

@app.route("/gcse")
def gcse():
    return render_template('gcse.html')

@app.route("/a_level")
def a_level():
    return render_template('a_level.html')