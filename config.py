import datetime

class BaseConfig(object):
    DEBUG = False
    TESTING = False
    JWT_SECRET_KEY = 'j\x8e5R\x84\xb3^\xef\t\x8bm"g\x82\xd8ml\x81\x13\x91$.\x96|'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=60)
    DB_NAME = 'sportsflashes'
    DB_USER = 'postgres'
    DB_PASSWORD = 'postgres'
    DB_HOST = 'localhost'
    DB_PORT = 5432


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    JWT_SECRET_KEY = 'j\x8e5R\x84\xb3^\xef\t\x8bm"g\x82\xd8ml\x81\x13\x91$.\x96|'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=14)
    REDIS_HOST = 'redis-dev-posts.7tbdkg.0001.use2.cache.amazonaws.com'
    REDIS_PORT = 6379
    REDIS_DECODE_RESPONSES =True
    DB_NAME = 'sportsflashes'
    DB_USER = 'postgres'
    DB_PASSWORD = 'postgres'
    DB_HOST = 'db-livsco.cfrcolph1w1u.us-east-2.rds.amazonaws.com'
    DB_PORT = 5432

class TestConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    JWT_SECRET_KEY = 'secret key'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=5)
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DECODE_RESPONSES =True
    DB_NAME = 'sportsflashes'
    DB_USER = 'postgres'
    DB_PASSWORD = 'postgres'
    DB_HOST = 'localhost'
    DB_PORT = 5432

class LocalConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    JWT_SECRET_KEY = 'j\x8e5R\x84\xb3^\xef\t\x8bm"g\x82\xd8ml\x81\x13\x91$.\x96|'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=14)
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DECODE_RESPONSES =True
    DB_NAME = 'sportsflashes'
    DB_USER = 'postgres'
    DB_PASSWORD = 'postgres'
    DB_HOST = 'localhost'
    DB_PORT = 5432