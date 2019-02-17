from celery import Celery


class MessageBus:

    def __init__(self, settings):
        self._connection = None
        self.connection = settings

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, settings):
        rb_host = settings.rabbit_host
        rb_port = settings.rabbit_port
        rb_user = settings.rabbit_user
        rb_password = settings.rabbit_password

        self._connection = Celery("tasks", backend='rpc://',
                                  broker=f'amqp://{rb_user}:{rb_password}@{rb_host}:{rb_port}', queue="user")
