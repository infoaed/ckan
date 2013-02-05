import os
import time
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

logging.basicConfig()
logger = logging.getLogger("sql-profile")
logger.setLevel(logging.DEBUG)

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement,
                        parameters, context, executemany):
    context._query_start_time = time.time()
    logger.debug("Start Query:\n%s" % statement)


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement,
                        parameters, context, executemany):
    total = time.time() - context._query_start_time
    logger.debug("Query Complete!")
    logger.debug("Total Time: %.02fms" % (total*1000))
    logger.debug("")
