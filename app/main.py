from pathlib import Path

from aiohttp import web

from .settings import Settings
from .views import update, get, remove, dump, get_history


THIS_DIR = Path(__file__).parent
BASE_DIR = THIS_DIR.parent


def setup_routes(app):
    app.router.add_post('/update', update, name='update')
    app.router.add_get('/get', get, name='get')
    app.router.add_get('/remove', remove, name='remove')
    app.router.add_get('/dump', dump, name='dump')
    app.router.add_get('/getHistory', get_history, name='get_history')


def create_app(loop):
    app = web.Application(loop=loop)
    settings = Settings()
    app.update(
        name='app',
        settings=settings
    )

    setup_routes(app)
    return app
