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

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    date_of_birth = db.Column(db.DateTime, nullable=False)
    school = db.Column(db.String(256), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    role = db.relationship('Role', secondary=users_roles, backref=db.backref('user', lazy='dynamic'))

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Role(RoleMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False, unique=True)
    #user_role = db.relationship('RoleMember', backref='role', lazy=True)

#class RoleMember(db.Model):
#    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
#    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), primary_key=True)
#    user = db.relationship('User', backref='rolemember', lazy=True)