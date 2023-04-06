from flask import render_template, url_for, request, redirect, flash
from education import app, db, mail
from education.models import User, users_roles, Role, TeachingClass, class_student, Activity
from education.forms import RegistrationForm, LoginForm, PointsForm, NewClassForm, SetHomeworkForm
from education.email import send_mail
from education.authentication import generate_confirmation_token, verify_confirmation_token
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message

@app.before_request
def before_request():
    if current_user.is_authenticated and not current_user.authenticated and \
        request.endpoint in ['cyberbullying', 'phishing', 'suspicious_links', 'databases', 'profile', 'teacher_home']:
        flash("Please verify your email first")
        return redirect(url_for('unconfirmed'))
    if not current_user.is_authenticated and request.endpoint in ['cyberbullying', 'phishing', 'suspicious_links', 'databases', 'profile', 'teacher_home']:
        flash("You must be logged in to view this page")
        return redirect(url_for('login'))
    if "teacher" not in current_user.role and request.endpoint in ['teacher_home', 'view_class', 'new_class', 'set_homework']:
        flash("You must be a teacher to view this page")
        return redirect(url_for('home'))
    if request.path.startswith('/admin/'):
        if not current_user.is_authenticated or "admin" not in current_user.role:
            flash("You must be an admin to view this page")
            return redirect(url_for('home'))

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
        confirmation_token = generate_confirmation_token(user.id)
        send_mail(user.email, 'Confirm your email', '/mail/test', user=user, token=confirmation_token)
        db.session.add(user)
        db.session.commit()
        flash('Registration succesful!')
        flash('Check your inbox to verify your email (Check your spam folder)')
        login_user(user)
        return redirect(url_for('home'))
    return render_template('register.html', title='Register',
        form=form)

@app.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.authenticated:
        return redirect(url_for('home'))
    key = verify_confirmation_token(token)
    if key:
        if key.get('confirm') == current_user.id:
            current_user.authenticated = 1
            db.session.add(current_user)
            db.session.commit()
            flash('You have confirmed your account!')
            return redirect(url_for('home'))
    return redirect(url_for('home'))

@app.route('/unconfirmed', methods=['POST', 'GET'])
@login_required
def unconfirmed():
    if current_user.authenticated:
        return redirect(url_for('home'))
    return render_template('unconfirmed.html')

@app.route('/resend_confirmation_email', methods=['POST', 'GET'])
@login_required
def resend_confirmation_email():
    if current_user.authenticated:
        return redirect(url_for('home'))
    token = generate_confirmation_token(current_user.id)
    flash("A new confirmation link has been sent to your email")
    send_mail(current_user.email, 'Confirm your account', '/mail/test', user=current_user, token=token)
    return redirect(url_for('unconfirmed'))

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

@app.route("/teacher_home")
@login_required
def teacher_home():
    classes = TeachingClass.query.filter_by(teacher_user=current_user.id)
    return render_template('teacher_home.html', classes=classes)
    
@app.route("/view_class/<int:class_id>")
@login_required
def view_class(class_id):
    t_class = TeachingClass.query.get_or_404(class_id)
    if current_user.id != t_class.teacher_user:
        flash("You must be the teacher of this class to access this page")
        return redirect(url_for('home'))
    students = User.query.filter(User.classes.any(id=class_id)).all()
    return render_template('view_class.html', t_class=t_class, students=students)
    
@app.route("/new_class", methods=['GET', 'POST'])
@login_required
def new_class():
    school = current_user.school
    pupils = User.query.filter(User.school == school) # User goes to the same school and has the role 'student'
    form = NewClassForm()
    form.students.choices = [(user.id, user.first_name + " " + user.last_name) for user in User.query.filter(User.school == school)]
    if form.validate_on_submit():
        class_add = TeachingClass(name = form.name.data, teacher_user = current_user.id)
        db.session.add(class_add)
        db.session.commit()
        for i in range(0, len(form.students.data)):
            user = User.query.get_or_404(form.students.data[i])
            user.classes.append(class_add)
            db.session.commit()
        return redirect(url_for('home'))
    return render_template('new_class.html', pupils=pupils, form=form)
    
@app.route("/set_homework", methods=['GET', 'POST'])
@login_required
def set_homework():
    form = SetHomeworkForm()
    form.activities.choices = [(activity.id, activity.name) for activity in Activity.query.all()]
    return render_template('set_homework.html', form=form)
