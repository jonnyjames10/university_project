from flask_admin.contrib.sqla import ModelView
import flask_login as login
from education.models import User, RoleMember

class AdminView(ModelView):
    def is_accessible(self):
        if login.current_user.is_authenticated:
            if login.current_user.get_id():
                user = User.query.get(login.current_user.get_id())
                # Search role_member for role_id value

                # Return that role
                return user.role
        return False