from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin.contrib.sqla import ModelView
from flask_mail import Mail
from flask_simple_crypt import SimpleCrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = '29080ff5cc25442bfe816387f7ffd9a54d2bded330d9f9b7'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Piano2002@localhost/educationalportal'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'cybereducational@gmail.com'
app.config['MAIL_DEFAULT_SENDER'] = 'cybereducational@mail.com'
app.config['MAIL_PASSWORD'] = 'zlbkdfxwymejctga'
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

db = SQLAlchemy(app)

cipher = SimpleCrypt()
cipher.init_app(app)

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.init_app(app)

class UserView(ModelView):
    can_view_details = True
    form_columns = ['id', 'first_name', 'last_name', 'email', 'school', 'points', 'role']
    column_default_sort = ('id', False)
    column_filters = ['first_name', 'last_name', 'email', 'role.name']
    column_details_list = [
        'first_name', 'last_name', 'email', 'school', 'points', 'role'
    ]
    

from flask_admin import Admin
from education.views import AdminView
from education.models import User, Role, TeachingClass, Homework, HomeworkResult, Activity, ActivityType, Level, Question
admin = Admin(app, name='Admin panel', template_mode='bootstrap3')
admin.add_view(UserView(User, db.session))
admin.add_view(AdminView(Role, db.session))
admin.add_view(AdminView(TeachingClass, db.session))
admin.add_view(AdminView(Homework, db.session))
admin.add_view(AdminView(HomeworkResult, db.session))
admin.add_view(AdminView(Activity, db.session))
admin.add_view(AdminView(ActivityType, db.session))
admin.add_view(AdminView(Level, db.session))
admin.add_view(AdminView(Question, db.session))

from education import routes