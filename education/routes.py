from flask import render_template, url_for, request, redirect, flash, session
from education import app, db, mail
from education.models import User, Role, TeachingClass, Activity, Homework, HomeworkResult, ActivityType
from education.forms import RegistrationForm, LoginForm, PointsForm, NewClassForm, SetHomeworkForm, CyberbullyingNotesForm
from education.email import send_mail
from education.authentication import generate_confirmation_token, verify_confirmation_token
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from flask_session import Session
import datetime
from datetime import datetime, timedelta
import random
import copy

@app.before_request
def before_request():
    if current_user.is_authenticated and not current_user.authenticated and \
        request.endpoint in ['cyberbullying', 'phishing', 'suspicious_links', 'databases', 'profile', 'teacher_home']:
        flash("Please verify your email first")
        return redirect(url_for('unconfirmed'))
    if not current_user.is_authenticated and request.endpoint in ['cyberbullying', 'phishing', 'suspicious_links', 'databases', 'profile', 'teacher_home']:
        flash("You must be logged in to view this page")
        return redirect(url_for('login'))
    if current_user.is_authenticated and "teacher" not in current_user.role and request.endpoint in ['teacher_home', 'view_class', 'new_class', 'set_homework']:
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
            session['homework'] = False
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

cb_notes_questions = {
    'Which is the correct answer?':['This one', 'Not this one', 'Nope', 'Nah']
}

def shuffle(q):
    selected_keys = []
    i = 0
    q_keys = list(q.keys())
    while i < len(q_keys):
        selection = random.choice(q_keys)
        if selection not in selected_keys:
            selected_keys.append(selection)
            i+=1
    return selected_keys

def set_answers(form, question, answers):
#    for i in range(0, len(question)):
    form.q1.choices = [(ans, ans) for ans in answers[question[0]]]
    form.q2.choices = [(ans, ans) for ans in answers[question[1]]]
    form.q3.choices = [(ans, ans) for ans in answers[question[2]]]
    form.q4.choices = [(ans, ans) for ans in answers[question[3]]]
    form.q5.choices = [(ans, ans) for ans in answers[question[4]]]

#def check_answers(form, questions, answers):


@app.route("/primary_school/cyberbullying", methods=['POST', 'GET'])
@login_required
def cyberbullying():
    with open("education/static/notes/cyberbullying.txt", "r") as text:
        notes = text.read()
    notes_form = CyberbullyingNotesForm()
    # video_form = VideoForm()
    # test_form = TestForm()
    cb_notes_copy_questions = copy.deepcopy(cb_notes_questions) # Copy the questions
    shuffled_notes_questions = shuffle(cb_notes_copy_questions) # Shuffle the keys of the questions
    for i in cb_notes_copy_questions.keys():
        random.shuffle(cb_notes_copy_questions[i]) # Shuffle the answers
    #set_answers(notes_form, (shuffled_notes_questions), cb_notes_copy_questions)
    notes_form.q1.choices = [(answer, answer) for answer in cb_notes_copy_questions[shuffled_notes_questions[0]]]
    if notes_form.validate_on_submit():
        correct = 0 # check_answers()
        if notes_form.q1.data == cb_notes_questions[shuffled_notes_questions[0]][0]:
            correct += 1
        flash("You got " + str(correct) + " correct")
        #TODO:
            # Allocate points
        if session['homework'] == True and notes_form.activity_id == session['activity_id']:
            flash("Homework complete")
            end_homework(correct, current_user.id)
        return redirect(url_for('cyberbullying'))
    return render_template('primary_school/cyberbullying.html', notes=notes, notes_questions=shuffled_notes_questions, 
                           notes_answers=cb_notes_copy_questions, notes_form=notes_form)

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
    
@app.route("/set_homework/<int:class_id>", methods=['GET', 'POST'])
@login_required
def set_homework(class_id):
    form = SetHomeworkForm()
    form.activities.choices = [(activity.id, activity.name) for activity in Activity.query.all()]
    if form.validate_on_submit():
        print(form.activities.data)
        homework = Homework(due_date = form.due_date.data, notes = form.notes.data, class_id = class_id, activity_id = form.activities.data)
        db.session.add(homework)
        db.session.commit()
        flash("Homework set successfully!")
        return redirect(url_for('home'))
    return render_template('set_homework.html', form=form)

def homework_helper(classes):
    homework_obj = []
    for cl in classes:
        homework_obj.append(cl.homeworks) # Add homework objects from class to list
    homeworks = []
    for h in homework_obj:
        for hw in range(0, len(h)+1):
            if h:
                homeworks.append(Homework.query.get(hw)) # Add homeworks from the object to a list
    activities = []
    for hw in homeworks:
        if hw:
            activities.append(Activity.query.get(hw.activity_id)) # Find the activities for each homework
    complete_hw = []
    i=0
    for hw in range(0, len(homeworks)):
        if Homework.query.get(hw):
            complete_hw.append([Homework.query.get(hw), activities[i]]) # Put them into a same list
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
        completed_id.append(i.id)
    date_today = datetime.today()
    date_tmrw = date_today.date() + timedelta(days=1)
    return render_template('homework.html', complete_hw=complete_hw, 
                           completed_id=completed_id, date_tmrw=date_tmrw)

@app.route("/completing_homework/<int:activity_id>/<int:homework_id>")
@login_required
def completing_homework(activity_id, homework_id):
    session['homework'] = True
    activity = Activity.query.get_or_404(activity_id)
    session['activity_id'] = activity.id
    # Get the activity type id and set to a variable
    act_type = ActivityType.query.get(activity.activity_type_id)
    session['activity_type'] = act_type.id
    session['homework_id'] = homework_id
    return redirect(url_for(activity.url_link))

def end_homework(mark, user_id):
    # Need to write values to homework_result table
    homework = HomeworkResult(mark=mark, homework_id=session['homework_id'], user_id=user_id)
    db.session.add(homework)
    db.session.commit()
    session.pop('activity_type', None)
    session.pop('homework', None)
    session['homework'] = False
    session.pop('homework_id', None)
    return redirect(url_for('home'))
