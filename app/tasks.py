from celery import Celery
from celery.task import periodic_task

from .settings import Settings

from redis_collections import Dict
from redis import StrictRedis
from redis.exceptions import ConnectionError

from datetime import timedelta


settings = Settings()
app = Celery('tasks', backend='amqp', broker=settings.AMQP_URL)


@app.task
def nodes_update_handler(name: str, timestamp: int, author: str):
    """
    task handler for update every node data
    """
    for redis_url in settings.REDIS_NODES_URL.split(','):
        update_data_nodes.delay(redis_url, name, timestamp, author)


@app.task(bind=True)
def update_data_nodes(
        self, redis_url: str, name: str, timestamp: int, author: str
):
    """
    task for update current node data
    """
    try:
        conn = StrictRedis.from_url(redis_url)
        data = Dict(key='data', redis=conn)
        if name in data:
            data[name] = data[name] + [
                {'timestamp': timestamp, 'author': author}
            ]
        else:
            data[name] = [{'timestamp': timestamp, 'author': author}]
    except ConnectionError:
        self.retry(countdown=5)


@app.task
def node_remove_handler(name: str):
    """
    task handler for remove every node data by name
    """
    for redis_url in settings.REDIS_NODES_URL.split(','):
        remove_data_nodes.delay(redis_url, name)


@app.task(bind=True)
def remove_data_nodes(self, redis_url: str, name: str):
    """
    task for remove current node data by name
    """
    try:
        conn = StrictRedis.from_url(redis_url)
        data = Dict(key='data', redis=conn)
        del data[name]
    except ConnectionError:
        self.retry(countdown=5)


@periodic_task(run_every=timedelta(minutes=5))
def update_new_nodes():
    """
    periodic task for update new node with data from existing nodes.
    Task check if we are added new redis service url and copy all data from
    existing nodes
    """
    conn = StrictRedis.from_url(settings.REDIS_URL)
    nodes_list = str(conn.get('nodes_list'))

    # all nodes are new
    if not nodes_list:
        conn.set('nodes_list', settings.REDIS_NODES_URL)
    # it seems we add new node
    elif nodes_list != settings.REDIS_NODES_URL:
        new_nodes = filter(
            lambda x: x not in nodes_list.split(','),
            settings.REDIS_NODES_URL.split(',')
        )

        for node_url in new_nodes:
            for redis_url in settings.REDIS_NODES_URL.split(','):
                try:
                    conn = StrictRedis.from_url(redis_url)
                    exiting_data = Dict(key='data', redis=conn)

                    conn = StrictRedis.from_url(node_url)
                    new_data = Dict(key='data', redis=conn)
                    new_data.update(exiting_data.copy())
                except ConnectionError:
                    pass

        conn.set('nodes_list', settings.REDIS_NODES_URL)
