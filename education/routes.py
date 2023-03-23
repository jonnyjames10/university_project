from flask import render_template, url_for, request, redirect, flash
import json
from education import app, db
from education.models import User, users_roles, Role
from education.forms import RegistrationForm, LoginForm, PointsForm
from flask_login import login_user, logout_user, login_required, current_user

@app.route("/")
@app.route("/home")
def home():
    users = User.query.order_by(User.points.desc()).limit(5)
    authen = current_user.is_authenticated
    if authen == True:
        contains = current_user in users
        if contains != True:
            order = User.query.order_by(User.points.desc())
            pos = 1
            for user in order:
                if user.id == current_user.id:
                    position = pos
                    break
                else:
                    pos+=1
            return render_template('home.html', users=users, position=position)
    return render_template('home.html', users=users)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        student_role = Role.query.filter_by(name='student').first()
        user = User(first_name = form.first_name.data,
            last_name = form.last_name.data, email = form.email.data,
            password = form.password.data, date_of_birth = form.date_of_birth.data,
            school = form.school.data, points = '0', role=[student_role])
        
        db.session.add(user)
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

@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get_or_404(current_user.id)
    return render_template('profile.html', user=user)

@app.route("/primary_school")
def primary_school():
    return render_template('primary_school.html')

@app.route("/primary_school/cyberbullying")
@login_required
def cyberbullying():
    with open("education/static/notes/cyberbullying.txt", "r") as text:
        notes = text.read()
    return render_template('primary_school/cyberbullying.html', notes=notes)

@app.route("/primary_school/cyberbullying/pong", methods=['GET', 'POST'])
@login_required
def cyberbullying_pong():
    form = PointsForm()
    if form.validate_on_submit():
        user = User.query.get_or_404(current_user.id)
        user.points += int(form.dbPoints.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('cyberbullying'))
    return render_template('primary_school/games/pong.html', form=form)

@app.route("/primary_school/phishing")
@login_required
def phishing():
    return render_template('primary_school/phishing.html')

@app.route("/primary_school/suspicious_links")
@login_required
def suspicious_links():
    return render_template('primary_school/suspicious_links.html')

@app.route("/gcse")
def gcse():
    return render_template('gcse.html')

@app.route("/gcse/databases")
@login_required
def databases():
    with open("education/static/notes/databases.txt", "r") as text:
        notes = text.read()
    return render_template('gcse/databases.html', notes=notes)

@app.route("/a_level")
def a_level():
    return render_template('a_level.html')