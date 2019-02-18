#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ylc'

import asyncio, logging
import aiomysql


def log(sql, args=()):
    logging.info('SQL: %s', sql)


# create_pool method
async def create_pool(loop, **kw):
    logging.info('create database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get('hots', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )


# select method
async def select(sql, args, size=None):
    log(sql, args)
    # global __pool
    async with __pool.get() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql.replace('?', '%s'), args or ())
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
        # await cur.close()
        logging.info('rows returned: %s' % len(rs))
        return rs


# insert、update、delete methods
async def execute(sql, args, autocommit=True):
    log(sql, args)
    # global __pool
    async with __pool.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount
            if not autocommit:
                await conn.commit()
            # await cur.close()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise
        return affected


# create args string method
def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ','.join(L)


# Field
class Field(object):
    def __init__(self, name, column_type, primary_key, default):
        self.__name = name
        self.__column_type = column_type
        self.__primary_key = primary_key
        self.__default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.__column_type, self.__name)


# StringField
class StringField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)


# BooleanField
class BooleanField(Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, 'boolean', False, default)


# IntegerField
class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)


# FloatField
class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)


# TextField
class TextField(Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)


# ModelMetaclass
class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        # 排除Model类本身:
        if name == 'model':
            return type.__new__(cls, name, bases, attrs)
        # 获取table名称
        tableName = attrs.get('__table__', None) or name
        logging.info('found model: %s (table: %s)' % (name, tableName))
        mappings = dict()
        fields = []
        primarykey = None





# ORM
class Model(dict, metaclass=ModelMetaclass):

    def __init__(self, **kwargs):
        super(Model, self).__init__(**kwargs)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
        if field.default is not None:
            value = field.default if callable(field.default) else field.default
            logging.debug('using default value for %s: %s' % (key, str(value)))
            setattr(self, key, value)
        return value