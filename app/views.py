from aiohttp import web

from .tasks import nodes_update_handler, node_remove_handler
from .settings import Settings

from redis_collections import Dict
from redis import StrictRedis
from redis.exceptions import ConnectionError

from json.decoder import JSONDecodeError
from operator import itemgetter


async def update(request):
    """
    view for insert/update data
    """
    try:
        data = await request.json()
    except JSONDecodeError:
        raise web.HTTPBadRequest

    try:
        name = str(data['name'])
        timestamp = int(data['timestamp'])
        author = str(data['author'])
    except KeyError:
        raise web.HTTPBadRequest

    nodes_update_handler.delay(name, timestamp, author)

    return web.json_response(
        {name: {'timestamp': timestamp, 'author': author}}
    )


async def get(request):
    """
    view for get data by name
    """
    name = request.rel_url.query.get('name')
    settings = Settings()

    if name is None or name == '':
        raise web.HTTPBadRequest

    for i, redis_url in enumerate(settings.REDIS_NODES_URL.split(',')):
        try:
            conn = StrictRedis.from_url(redis_url)
            value = Dict(key='data', redis=conn)[name]
            # sort by timestamp
            return web.json_response(
                sorted(value, key=itemgetter('timestamp'), reverse=True)[0]
            )
        except (ConnectionError, KeyError):
            pass

    return web.json_response(
        {'success': False, 'reason': 'It seems all nodes are down'}
    )


async def remove(request):
    """
    view for remove data by name
    """
    name = request.rel_url.query.get('name')

    if name is None or name == '':
        raise web.HTTPBadRequest

    node_remove_handler.delay(name)

    return web.json_response({'success': True}, status=204)


async def dump(request):
    """
    view for for render all dump data
    """
    settings = Settings()

    for redis_url in settings.REDIS_NODES_URL.split(','):
        try:
            conn = StrictRedis.from_url(redis_url)
            redis_data = Dict(key='data', redis=conn)

            return web.json_response(
                {name: value for name, value in redis_data.items()}
            )

        except ConnectionError:
            pass

    return web.json_response(
        {'success': False, 'reason': 'It seems all nodes are down'}
    )


async def get_history(request):
    """
    view for get data history by name
    """
    name = request.rel_url.query.get('name')
    settings = Settings()

    if name is None or name == '':
        raise web.HTTPBadRequest

    for redis_url in settings.REDIS_NODES_URL.split(','):
        try:
            conn = StrictRedis.from_url(redis_url)
            value = Dict(key='data', redis=conn)[name]
            # sort by timestamp
            return web.json_response(
                sorted(value, key=itemgetter('timestamp'), reverse=True)
            )

        except (ConnectionError, KeyError):
            pass

    return web.json_response(
        {'success': False, 'reason': 'It seems all nodes are down'}
    )
