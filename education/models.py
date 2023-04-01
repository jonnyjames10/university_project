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