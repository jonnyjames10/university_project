from flask import render_template, url_for, request, redirect, flash, session
from education import app, db, mail, cipher
from education.models import User, Role, TeachingClass, Activity, Homework, HomeworkResult, ActivityType, Question
from education.forms import RegistrationForm, LoginForm, PointsForm, NewClassForm, SetHomeworkForm, QuestionForm, EditProfileForm, VideoForm, TestForm
from education.email import send_mail
from education.authentication import generate_confirmation_token, verify_confirmation_token
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from flask_session import Session
import datetime
from datetime import datetime, timedelta
import random
from sqlalchemy import desc, or_
from sqlalchemy.sql.expression import func

# References:
#   PalletsProjects. [No date] Flask (Version 2.3) [Code Library] https://flask.palletsprojects.com/en/2.3.x/
#   Countryman, M. (2022) Flask-Login (Version 0.6.2) [Code Library] https://flask-login.readthedocs.io/en/latest/
#   Python (2023) datetime (Version 3.11.3) [Code Library] https://docs.python.org/3/library/datetime.html
#   Python. [No date]. random – Generate pseudo-random numbers. [Code Library]. https://docs.python.org/3/library/random.html/
#   SQLAlchemy. (2023) SQLAlchemy. (Version 2.0.11) [Code Library] https://www.sqlalchemy.org. 

@app.before_request
def before_request():
    # If user is logged in but hasn't verified their email
    if current_user.is_authenticated and not current_user.authenticated and \
        request.endpoint in ['cyberbullying', 'phishing', 'suspicious_links', 'databases', 'profile', 'homework', 'completing_homework']:
        flash("Please verify your email first")
        return redirect(url_for('unconfirmed'))
    # If user is not logged in
    if not current_user.is_authenticated and request.endpoint in ['cyberbullying', 'phishing', 'suspicious_links', 'databases', 'profile', 'homework', 
                                                                  'completing_homework']:
        flash("You must be logged in to view this page")
        return redirect(url_for('login'))
    # If user is logged in and doesn't have the 'teacher' role
    if current_user.is_authenticated and "teacher" not in current_user.role and request.endpoint in ['teacher_home', 'view_class', 'new_class', 'set_homework', 
                                                                                                     'view_homework']:
        flash("You must be a teacher to view this page")
        return redirect(url_for('home'))
    # If user is not authenticated or have the 'admin' user and tries to access admin pages
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
        db.session.add(user)
        db.session.commit()
        flash('Registration succesful!')
        flash('Check your inbox to verify your email (Check your spam folder)')
        login_user(user)
        resend_confirmation_email()
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
    send_mail(current_user.email, 'Confirm your account', '/mail/verify', user=current_user, token=token)
    return redirect(url_for('unconfirmed'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            session['homework'] = False
            return redirect(url_for('home'))
        elif user is not None:
            flash("Please re-enter your password")
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    session.pop('activity_type', None)
    session.pop('homework', None)
    session['homework'] = False
    session.pop('homework_id', None)
    logout_user()
    return redirect(url_for('home'))

@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get_or_404(current_user.id)
    return render_template('profile.html', user=user)

@app.route("/edit_profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    user = User.query.get_or_404(current_user.id)
    if form.validate_on_submit():
        if form.email.data != user.email:
            confirmation_token = generate_confirmation_token(user.id)
            user.authenticated = 0
            send_mail(form.email.data, 'Confirm your email', '/mail/test', user=user, token=confirmation_token)
            flash('Check your inbox to verify your email (Check your spam folder)')
        user.first_name = form.first_name.data
        user.last_name=form.last_name.data
        user.email=form.email.data
        user.school = form.school.data
        user.date_of_birth = form.date_of_birth.data
        db.session.commit()
        flash("Details changed succesfully!")
        return redirect(url_for('profile'))
    form.first_name.data = user.first_name
    form.last_name.data = user.last_name
    form.email.data = user.email
    form.school.data = user.school
    form.date_of_birth.data = user.date_of_birth
    return render_template('edit_profile.html', form=form)

def assign_points(user_id, points):
    user = User.query.get_or_404(user_id)
    user.points += int(points)
    db.session.add(user)
    db.session.commit()

@app.route("/primary_school")
def primary_school():
    return render_template('primary_school.html')

def shuffle(questions):
    order = []
    selected = []
    i = 0
    q_ids = [qu.id for qu in questions]
    while i < len(q_ids):
        selection = random.choice(q_ids)
        if selection not in selected:
            for qs in questions:
                if qs.id == selection:
                    order.append(qs)
                    selected.append(selection)
            i+=1
    return order

def set_answers(form, questions):
    answers = []
    for field, question in zip(form, questions):
        field.choices = [(question.a, question.a), (question.b, question.b), (question.c, question.c), (question.d, question.d)]
        field.id = question.id
        random.shuffle(field.choices)
        field.label = question.title
        answers.append(question.answer)
    return questions, answers

def results(correct, points):
    flash("You got " + str(correct) + " correct")
    flash("You got " + str(points) + " points")
    user = User.query.get_or_404(current_user.id)
    assign_points(user.id, points)

def process_answers(form):
    user_answered = []
    for i in form:
        if i != "csrf_token":
            if i != "submit":
                user_answered.append(form[i])
    return user_answered

@app.route("/test/<url_link>")
@login_required
def test(url_link):
    activity = Activity.query.filter_by(url_link=url_link).filter_by(activity_type_id=4).first()
    notes = Activity.query.filter_by(url_link=url_link).filter_by(activity_type_id=1).first()
    video = Activity.query.filter_by(url_link=url_link).filter_by(activity_type_id=2).first()
    form = TestForm()
    questions = Question.query.filter(or_(Question.activity_id==notes.id, Question.activity_id==video.id)).order_by(func.rand()).limit(8).all()
    questions = shuffle(questions)
    global test_answers
    questions, test_answers = set_answers(form, questions)
    return render_template('test.html', activity=activity, form=form)

@app.route("/primary_school/cyberbullying", methods=['POST', 'GET'])
@login_required
def cyberbullying():
    with open("education/static/notes/cyberbullying.txt", "r") as text:
        notes = text.read()

    notes_form = QuestionForm()
    video_form = VideoForm()
    activity = Activity.query.filter_by(name="Cyberbullying Notes").first()
    video = Activity.query.filter_by(name="Cyberbullying Video").first()
    global notes_answers
    global video_answers
    notes_questions = Question.query.filter_by(activity_id=activity.id).order_by(func.rand()).limit(5).all()
    video_questions = Question.query.filter_by(activity_id=video.id).order_by(func.rand()).limit(5).all()
    notes_questions = shuffle(notes_questions)
    video_questions = shuffle(video_questions)
    notes_questions, notes_answers = set_answers(notes_form, notes_questions)
    video_questions, video_answers = set_answers(video_form, video_questions)

    return render_template('primary_school/cyberbullying.html', notes=notes, notes_form=notes_form, notes_questions=notes_questions, 
                           video_form=video_form, video_questions=video_questions, url_link=activity.url_link)

@app.route("/check_answers", methods=['POST'])
def check_answers():
    correct = 0
    form = request.form
    #answers = request.args.getlist('answers')
    activity_type_id = request.args.get('activity_type_id', type=int)
    activity_id = request.args.get('activity_id', type=int)
    if activity_type_id == 1:
        answers = notes_answers
    elif activity_type_id == 2:
        answers = video_answers
    elif activity_type_id == 4:
        answers = test_answers
    activity = Activity.query.get(activity_id)
    user_answered = process_answers(form)
    print(user_answered)
    print(answers)
    for i, j in zip(user_answered, answers):
        if i == j:
            correct += 1
    if activity_type_id == 4:
        results(correct, int(correct*20))
    else:
        results(correct, int(correct*10))
    if session['homework'] == True and session['activity_id'] == activity_id:
        end_homework(int(correct), current_user.id)
    return redirect(url_for(activity.url_link))

@app.route("/primary_school/cyberbullying/pong", methods=['GET', 'POST'])
@login_required
def cyberbullying_pong():
    form = PointsForm()
    form.activity_id.data = 3
    user = User.query.get_or_404(current_user.id)
    if form.validate_on_submit():
        results(form.marks.data, int(form.dbPoints.data))
        if session['homework'] == True and session['activity_id'] == form.activity_id.data:
            end_homework(int(form.marks.data), current_user.id)
        return redirect(url_for('cyberbullying'))
    return render_template('primary_school/games/pong.html', form=form, user=user)

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
    query = db.session.query(Homework)
    t_class = TeachingClass.query.get_or_404(class_id)
    if current_user.id != t_class.teacher_user:
        flash("You must be the teacher of this class to access this page")
        return redirect(url_for('home'))
    students = User.query.filter(User.classes.any(id=class_id)).all()
    query = query.order_by(Homework.due_date.desc())
    query = query.filter(Homework.class_id == t_class.id)
    homeworks = query
    return render_template('view_class.html', t_class=t_class, students=students, homeworks=homeworks)
    
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
        return redirect(url_for('view_class', class_id=class_add.id))
    return render_template('new_class.html', pupils=pupils, form=form)
    
@app.route("/set_homework/<int:class_id>", methods=['GET', 'POST'])
@login_required
def set_homework(class_id):
    form = SetHomeworkForm()
    form.activities.choices = [(activity.id, activity.name) for activity in Activity.query.all()]
    if form.validate_on_submit():
        homework = Homework(title=form.title.data, due_date = form.due_date.data, notes = form.notes.data, class_id = class_id, activity_id = form.activities.data)
        db.session.add(homework)
        db.session.commit()
        flash("Homework set successfully!")
        return redirect(url_for('view_class', class_id=class_id))
    return render_template('set_homework.html', form=form)

def homework_helper(classes):
    homework_obj = []
    for cl in classes:
        homework_obj.append(cl.homeworks) # Add homework objects from class to list
    homeworks = []
    for h in homework_obj:
        if h:
            for hw in h:
                homeworks.append(Homework.query.get(hw.id)) # Add homeworks from the object to a list
    activities = []
    for hw in homeworks:
        if hw:
            activities.append(Activity.query.get(hw.activity_id)) # Find the activities for each homework
    complete_hw = []
    i=0
    for hw in homeworks:
        if Homework.query.get(hw.id):
            hwork = Homework.query.get(hw.id)
            complete_hw.append([hwork, Activity.query.get(hwork.activity_id)]) # Put them into a same list
            i+=1
    return complete_hw

@app.route("/homework")
@login_required
def homework():
    user = User.query.get_or_404(current_user.id) #User ID
    classes = user.classes #Get user's classes
    complete_hw = homework_helper(classes)
    hw_completed = []
    completed_id = []
    for i in user.homework_results:
        if i:
            hw_completed.append(HomeworkResult.query.get(i.id))
    for i in hw_completed:
        completed_id.append(i.homework_id)
    date_today = datetime.today()
    date_tmrw = date_today.date() + timedelta(days=1)
    return render_template('homework.html', complete_hw=complete_hw, 
                           completed_id=completed_id, date_tmrw=date_tmrw)

@app.route("/view_homework/<int:homework_id>")
@login_required
def view_homework(homework_id):
    homework = Homework.query.get_or_404(homework_id)
    homework_results = HomeworkResult.query.filter(HomeworkResult.homework_id == homework.id)
    activity = Activity.query.get_or_404(homework.activity_id)
    students = []
    for hw in homework_results:
        students.append(User.query.get_or_404(hw.user_id))
    return render_template('view_homework.html', homework=homework, homework_results=homework_results, students=students, activity=activity)

@app.route("/completing_homework/<int:activity_id>/<int:homework_id>")
@login_required
def completing_homework(activity_id, homework_id):
    session['homework'] = True
    activity = Activity.query.get_or_404(activity_id)
    session['activity_id'] = activity.id
    act_type = ActivityType.query.get(activity.activity_type_id)
    session['activity_type'] = act_type.id
    session['homework_id'] = homework_id
    return redirect(url_for(activity.url_link))

def end_homework(mark, user_id):
    homework = HomeworkResult(mark=mark, homework_id=session['homework_id'], user_id=user_id)
    db.session.add(homework)
    db.session.commit()
    session.pop('activity_type', None)
    session.pop('activity_id', None)
    session.pop('homework', None)
    session['homework'] = False
    session.pop('homework_id', None)
    flash("Homework completed!")
    return redirect(url_for('home'))
