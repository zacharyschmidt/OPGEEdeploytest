
from flask_login import UserMixin

class User(UserMixin):
    pass


# @login_manager.user_loader
# def user_loader(username):
#     if username not in users:
#         return
#     user = User()
#     user.id = username
#     return user
