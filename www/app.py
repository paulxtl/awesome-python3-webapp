#! /usr/bin/env/python3
# -*- coding: utf-8 -*-

__author__ = 'ylc'

"""
async web application
"""

import logging; logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime

from aiohttp import web
from jinja2 import Environment, FileSystemLoader

import orm
from Models import User, Blog, Comment
from coroweb import add_routes, add_static


def index(request):
    return web.Response(body=b'<h1>Awesome</h1>', content_type='text/html')


def init_jinja2(app, **kw):
    logging.info('init jinja2...')
    options = dict(
        autoescape=kw.get('autoescape', True),
        block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'),
        variable_start_string=kw.get('variable_start_string', '{{'),
        variable_end_string=kw.get('variable_end_string', '}}'),
        auto_reload=kw.get('auto_reload', True)
    )
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(os.path.dirname(os.abspath(__file__)), 'templates')
    logging.info('set jinja2 template path:%s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    app['__templating__'] = env


async def logger_factory(app, handler):
    async def logger(request):
        logging.info('Request: %s %s' % (request.method, request.path))
        #await asyncio.sleep(0.3)
        return (await handler(request))
    return logger 



# def init():
#     app = web.Application()
#     app.router.add_route('GET', '/', index)
#     web.run_app(app, host='127.0.0.1', port=9000)
#     logging.info('server started at http://127.0.0.1:9000...')

async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv


async def test(loop):
    await orm.create_pool(loop=loop, host='127.0.0.1', user='www-data', password='www-data', db='awesome')
    u = User(name='Test', email='test1@example.com', passwd='123456', image='about:blank')
    await u.save()


if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    # loop.run_until_complete(init(loop))
    loop.run_until_complete(test(loop))
    loop.run_forever()
    # init()