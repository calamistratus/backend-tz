class SessionGetterException(Exception):
    """There was an error getting the session"""
    pass

class RedisPostgresException(Exception):
    """There was an error with uploading something from postgres to redis"""
    pass