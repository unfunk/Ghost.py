# -*- coding: utf-8 -*-
import threading
import logging
import time
import os
from unittest import TestCase
from wsgiref.simple_server import make_server
from ghost import Ghost


class ServerThread(threading.Thread):
    """Starts a Tornado HTTPServer from given WSGI application.

    :param app: The WSGI application to run.
    :param port: The port to run on.
    """
    def __init__(self, app, port=5000):
        self.app = app
        self.port = port
        super(ServerThread, self).__init__()

    def run(self):
        self.http_server = make_server('', self.port, self.app)
        self.http_server.serve_forever()

    def join(self, timeout=None):
        if hasattr(self, 'http_server'):
            self.http_server.shutdown()
            del self.http_server


class ProxyServerThread(threading.Thread):
    """Starts a Proxy Server
    """
    def __init__(self, app, port=5001, portRedirect=5000):
        self.app = app
        self.port = port
        self.portRedirect = portRedirect
        super(ProxyServerThread, self).__init__()
        
    def run(self):
        self.app(self.port, self.portRedirect, True)

class BaseGhostTestCase(TestCase):
    display = False
    wait_timeout = 5
    viewport_size = (800, 600)
    log_level = logging.INFO

    def __new__(cls, *args, **kwargs):
        """Creates Ghost instance."""
        if not hasattr(cls, 'ghost'):
            cls.ghost = Ghost(display=cls.display,
                wait_timeout=cls.wait_timeout,
                viewport_size=cls.viewport_size,
                log_level=cls.log_level,
                cache_dir="/tmp/ghost.py",
                cache_size=10)
            cls.page, name = cls.ghost.create_page()
            
            cls.ghost_prevent_download = Ghost(display=cls.display,
                wait_timeout=cls.wait_timeout,
                viewport_size=cls.viewport_size,
                log_level=cls.log_level,
                cache_dir="/tmp/ghost.py",
                cache_size=10)
            cls.ghost_prevent_download_page, name = \
                cls.ghost_prevent_download.create_page(prevent_download=["jpg"])
            
        return super(BaseGhostTestCase, cls).__new__(cls, *args, **kwargs)

    def __call__(self, result=None):
        """Does the required setup, doing it here
        means you don't have to call super.setUp
        in subclasses.
        """
        self._pre_setup()
        super(BaseGhostTestCase, self).__call__(result)
        self._post_teardown()

    def _post_teardown(self):
        """Deletes ghost cookies, cache and hide UI if needed."""
        self.page.delete_cookies()
        self.page.delete_cache()
        self.ghost_prevent_download_page.delete_cookies()
        self.ghost_prevent_download_page.delete_cache()
        self.page.network_manager.removeProxy()
        self.page.release_last_resources()
        if self.display:
            self.ghost.hide()

    def _pre_setup(self):
        """Shows UI if needed.
        """
        if self.display:
            self.ghost.show()


class GhostTestCase(BaseGhostTestCase):
    """TestCase that provides a ghost instance and manage
    an HTTPServer running a WSGI application.
    """
    port = 5000
    port_proxy = 5001
    
    def create_app(self):
        """Returns your WSGI application for testing.
        """
        raise NotImplementedError
    
    def create_proxy_server(self):
        """Returns your proxy server for testing.
        """
        raise NotImplementedError
    
    @classmethod
    def tearDownClass(cls):
        """Stops HTTPServer instance."""
        cls.server_thread.join()
        super(GhostTestCase, cls).tearDownClass()

    @classmethod
    def setUpClass(cls):
        """Starts HTTPServer instance from WSGI application.
        """
        cls.server_thread = ServerThread(cls.create_app(), cls.port)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        while not hasattr(cls.server_thread, 'http_server'):
            time.sleep(0.01)
        cls.proxy_server = ProxyServerThread(cls.create_proxy_server(),
                                cls.port_proxy, cls.port)
        cls.proxy_server.daemon = True
        cls.proxy_server.start()
        
        super(GhostTestCase, cls).setUpClass()
