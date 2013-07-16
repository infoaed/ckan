import os
import time
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Enable by adding following in environment.py
#     from ckan.lib.profiling import before_cursor_execute, after_cursor_execute

log = logging.getLogger("sql-profile")
log.setLevel(logging.DEBUG)

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement,
                        parameters, context, executemany):
    context._query_start_time = time.time()
    log.debug("Start Query: %s" % statement)

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement,
                        parameters, context, executemany):
    from pylons import request
    total = time.time() - context._query_start_time

    path = request.path if hasattr(request, "path") else "NOPATH"

    log.debug("Query Complete on %s!" % path)
    log.debug("Parameters: %s" % parameters)
    log.debug("Total Time: %.02fms" % (total*1000))
