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

from education import routes