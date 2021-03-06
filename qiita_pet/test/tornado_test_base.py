from mock import Mock
try:
    from urllib import urlencode
except ImportError:  # py3
    from urllib.parse import urlencode

from tornado.testing import AsyncHTTPTestCase
from qiita_pet.webserver import Application
from qiita_pet.handlers.base_handlers import BaseHandler
from qiita_db.sql_connection import SQLConnectionHandler
from qiita_db.environment_manager import (LAYOUT_FP, INITIALIZE_FP,
                                          POPULATE_FP)


class TestHandlerBase(AsyncHTTPTestCase):
    database = False

    def get_app(self):
        BaseHandler.get_current_user = Mock(return_value="test@foo.bar")
        self.app = Application()
        return self.app

    def setUp(self):
        if self.database:
            self.conn_handler = SQLConnectionHandler()
            # Drop the schema
            self.conn_handler.execute("DROP SCHEMA qiita CASCADE")
            # Create the schema
            with open(LAYOUT_FP, 'U') as f:
                self.conn_handler.execute(f.read())
            # Initialize the database
            with open(INITIALIZE_FP, 'U') as f:
                self.conn_handler.execute(f.read())
            # Populate the database
            with open(POPULATE_FP, 'U') as f:
                self.conn_handler.execute(f.read())
        super(TestHandlerBase, self).setUp()

    def tearDown(self):
        if self.database:
            del self.conn_handler

    # helpers from http://www.peterbe.com/plog/tricks-asynchttpclient-tornado
    def get(self, url, data=None, headers=None, doseq=True):
        if data is not None:
            if isinstance(data, dict):
                data = urlencode(data, doseq=doseq)
            if '?' in url:
                url += '&amp;%s' % data
            else:
                url += '?%s' % data
        return self._fetch(url, 'GET', headers=headers)

    def post(self, url, data, headers=None, doseq=True):
        if data is not None:
            if isinstance(data, dict):
                data = urlencode(data, doseq=doseq)
        return self._fetch(url, 'POST', data, headers)

    def _fetch(self, url, method, data=None, headers=None):
        self.http_client.fetch(self.get_url(url), self.stop, method=method,
                               body=data, headers=headers)
        return self.wait()
