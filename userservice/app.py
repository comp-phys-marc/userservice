import bcrypt
import json
from models import User
from settings import Settings
from emulatorcommon.message_bus import MessageBus
from emulatorcommon.utilities import Utils
from emulatorcommon.database import Database

settings = Settings()
utils = Utils()

bus = MessageBus(settings)
conn = bus.connection

database = Database(settings)
db_session = database.session


@conn.task(name="user.tasks.login_user")
def login(name, password):

    if not name or not password:
        return {
            "message": "Invalid request.",
            "status": 400
        }

    user = User.query.filter_by(name=name).first()

    if user is not None:
        password = password.encode('utf-8')
        user_password = user.password.encode('utf-8')

        authenticated = bcrypt.checkpw(password, user_password)

        if authenticated:
            return {
                "message": "Login successful.",
                "data": utils.object_as_dict(user),
                "status": 200
            }

        else:
            return {
                "message": "Invalid password.",
                "status": 401
            }
    else:
        return {
            "message": f'User with name {name} not found.',
            "status": 404
        }


@conn.task(name="user.tasks.list_users")
def list_users(filter):
    users_array = []
    if filter is None:
        users = User.query.all()
        for user in users:
            users_array.extend(dict(user))
    else:
        users = User.query.filter_by(**filter)
        for user in users:
            users_array.append(utils.object_as_dict(user))
    if len(users_array) > 0:
        return {
            "message": "Users found.",
            "data": json.dumps(users_array),
            "status": 200
        }
    else:
        return {
            "message": "No matching users found.",
            "status": 404
        }


@conn.task(name="user.tasks.create_user")
def create_user(data):

    if 'password' not in data:
        return {
            "message": "User password not provided.",
            "status": 400
        }

    data['password'] = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    new_user = User(**data)
    db_session.add(new_user)

    return try_commit()


@conn.task(name="user.tasks.update_user")
def update_user(data):
    if data.id is not None:
        old_user = User.query.filter_by(id=data.id).first()
        if old_user:
            updated_user = old_user.update(data)
            db_session.add(updated_user)
            return try_commit()
        else:
            return {
                "message": "User not found.",
                "status": 404
            }
    else:
        return {
            "message": "User id not provided.",
            "status": 400
        }


@conn.task(name="user.tasks.get_user")
def get_user(id):
    user = User.query.filter_by(id=id).first()

    if user is None:
        return {
            "message": f'User with id {id} not found.',
            "status": 404
        }
    else:
        return {
            "message": "User found.",
            "data": json.dumps(user),
            "status": 200
        }


def try_commit():
    try:
        db_session.commit()
        return {
            "message": "Operation successful.",
            "status": 200
        }
    except Exception as e:
        error_message = str(e)
        return {
            "message": f'An error occurred: {error_message}',
            "status": 500
        }
