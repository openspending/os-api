import os

from sqlalchemy import create_engine

_connection_string = os.environ.get('OS_API_ENGINE')#,u'postgresql://osuser:1234@localhost/os')
_engine = None

def get_engine():
    """Return engine singleton"""
    global _engine
    if _engine is None:
        _engine = create_engine(_connection_string)
    return _engine

