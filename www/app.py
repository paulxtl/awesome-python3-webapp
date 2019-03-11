#! /usr/bin/env/python3
# -*- coding: utf-8 -*-

__author__ = 'ylc'

import logging; logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime

from aiohttp import web

import orm
from Models import User, Blog, Comment


def index(request):
    return web.Response(body=b'<h1>Awesome</h1>', content_type='text/html')


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