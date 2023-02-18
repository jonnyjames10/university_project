from datetime import datetime
from education import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hah = db.Column(db.String(128))
    date_of_birth = db.Column(db.DateTime, nullable=False)
    role = db.Column(db.String(10), nullable=False, default='stu')

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