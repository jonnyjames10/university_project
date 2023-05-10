from threading import Thread
from . import mail
from flask_mail import Message
from flask import current_app, render_template

# References:
#   Wright, M. [No date] Flask-Mail (Version 0.9.1) [Code library] https://pythonhosted.org/Flask-Mail/

def send_async_mail(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    message = Message(subject, sender='m3hran Team', recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    thread = Thread(target=send_async_mail, args=[app, message])
    thread.start()
    return thread
