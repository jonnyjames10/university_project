from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '29080ff5cc25442bfe816387f7ffd9a54d2bded330d9f9b7'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://c2031619:Piano2002!@csmysql.cs.cf.ac.uk:3306/c2031619_education_portal'

db = SQLAlchemy(app)

from education import routes