from database import db_session
from models import User
from celery import Celery
import json
from sqlalchemy import inspect


celery = Celery("tasks", backend='rpc://',
                    broker='amqp://guest:guest@localhost:5672', queue="user")

@celery.task(name="user.tasks.login_user")
def login(name, password):
    return json.dumps(object_as_dict(User.query.filter_by(name=name, password=password).first()))

@celery.task(name="user.tasks.list_users")
def list_users(filter):
    users_array = []
    if filter is None:
        users = User.query.all()
        for user in users:
            users_array.extend(dict(user))
        return json.dumps(users_array)
    else:
        users = User.query.filter_by(**filter)
        for user in users:
            users_array.append(object_as_dict(user))
        return json.dumps(users_array)


@celery.task(name="user.tasks.create_users")
def create_users(data):
    for user_data in data.dataList:
        new_user = User(**user_data)
        return add_commit(new_user)


@celery.task(name="user.tasks.update_users")
def update_users(data):
    for user_data in data.dataList:
        old_user = User.query.filter_by(id=user_data.id).first()
        if old_user:
            updated_user = old_user.update(user_data)
            return add_commit(updated_user)


@celery.task(name="user.tasks.get_user")
def get_user(id):
    return User.query.filter_by(id=id).first()


def add_commit(obj):
    db_session.add(obj)
    return db_session.commit(obj)

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}