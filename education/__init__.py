from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '29080ff5cc25442bfe816387f7ffd9a54d2bded330d9f9b7'
# mysql://username:password@localhost/db_name
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Piano2002@localhost/educationalportal'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

from flask_admin import Admin
from education.views import AdminView
from education.models import User, Role
admin = Admin(app, name='Admin panel', template_mode='bootstrap3')
admin.add_view(AdminView(User, db.session))
admin.add_view(AdminView(Role, db.session))

from education import routes