import logging

from sentry.client.handlers import SentryHandler

class CustomLoggingHandler(SentryHandler):
    def __init__(self, *args, **kwargs):
        kwargs['level'] = logging.DEBUG
        SentryHandler.__init__(self, *args, **kwargs)
