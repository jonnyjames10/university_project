from datetime import datetime
from education import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_security import RoleMixin

users_roles = db.Table(
    'users_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class_teacher = db.Table(
    'class_teacher',
    db.Column('teacher_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('class_id', db.Integer, db.ForeignKey('teaching_class.id'))
)

class_student = db.Table(
    'class_student',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('class_id', db.Integer, db.ForeignKey('teaching_class.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    date_of_birth = db.Column(db.DateTime, nullable=False)
    school = db.Column(db.String(256), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    authenticated = db.Column(db.Boolean, default=False)
    role = db.relationship('Role', secondary=users_roles, backref=db.backref('user', lazy='dynamic'))
    class_teacher = db.relationship('TeachingClass', secondary=class_teacher, backref=db.backref('user_teacher', lazy='dynamic'))
    class_student = db.relationship('TeachingClass', secondary=class_student, backref=db.backref('user_student', lazy='dynamic'))
    homework_results = db.relationship('HomeworkResult', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.id}', {self.email}')"
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_anonymous(self):
        return False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Role(RoleMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False, unique=True)

class TeachingClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    homeworks = db.Relationship('Homework', backref='teaching_class', lazy=True)

class Homework(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    due_date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)
    class_id = db.Column(db.Integer, db.ForeignKey('teaching_class.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    results = db.relationship('HomeworkResult', backref='homework', lazy=True)

class HomeworkResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mark = db.Column(db.Integer, nullable=False)
    homework_id = db.Column(db.Integer, db.ForeignKey('homework.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    url_link = db.Column(db.String(200), nullable=False, unique=True)
    activity_type_id = db.Column(db.Integer, db.ForeignKey('activity_type.id'), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)
    homework = db.relationship('Homework', backref='activity', lazy=True)

class ActivityType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(20), nullable=False, unique=True)
    activities = db.Relationship('Activity', backref='activity_type', lazy=True)

class Level(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level_name = db.Column(db.String(20), nullable=False, unique=True)
    activities = db.Relationship('Activity', backref='level', lazy=True)