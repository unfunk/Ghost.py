# -*- coding: utf-8 -*-

try:
    import sip
    sip.setapi('QVariant', 2)
    
    from PyQt4.QtCore import QUrl
    from PyQt4.QtNetwork import QNetworkRequest, QNetworkAccessManager,\
                                QNetworkDiskCache, QNetworkProxy
except ImportError:
    try:
        from PyQt4.QtCore import QUrl
        from PySide.QtNetwork import QNetworkRequest, QNetworkAccessManager,\
                                QNetworkDiskCache, QNetworkProxy
    except ImportError:
        raise Exception("Ghost.py requires PySide or PyQt")

from NetworkMonitoring import NetworkMonitoring

class NetworkAccessManager(QNetworkAccessManager):
    """NetworkAccessManager manages a QNetworkAccessManager. It's
    crate a internal cache and manage all the request.
    
    :param cache_dir: a directory where Ghost is going to put the cache
    :param cache_size: the Size of the cache in MB. If it's 0 the
        cache it's automatically disabled.
    :param prevent_download: A List of extensions of the files that you want
        to prevent from downloading
    
    """
    _auth = ("dummy", "dummy2")
    _authIntent = 0
    _authProxy = ("dummy", "dummy2")
    
    def __init__(self, *args, **kwargs):
        cache_dir = kwargs.pop("cache_dir", "/tmp/ghost.py")
        cache_size = kwargs.pop("cache_size", 0)
        self._prevent_download = kwargs.pop("prevent_download", [])
        
        super(NetworkAccessManager, self).__init__(*args, **kwargs)
    
        cache = QNetworkDiskCache()
        cache.setCacheDirectory(cache_dir)
        cache.setMaximumCacheSize(cache_size * 1024 * 1024)
        self.setCache(cache)
        
        self.networkMonitoring = NetworkMonitoring()
        # Manages the authentication for the proxy
        self.proxyAuthenticationRequired.connect(self._authenticateProxy)
        self.authenticationRequired.connect(self._authenticate)
        
        self.finished.connect(self._add_resource_finished)
        
    def configureProxy(self, host, port, user=None, password=None):
        """Add a proxy configuration for the Network Requests.
        
        :param host: the proxy host
        :param port: the proxy port
        :param user: if the proxy has authentication this param sets
            the user to be used. It should be None if it's not required to
            access with a user
        :param password: if the proxy has authentication this param sets
            the password to be used. It should be None if it's not required to
            access with a password
        """
        proxy = QNetworkProxy()
        proxy.setType(QNetworkProxy.HttpProxy)
        proxy.setHostName(host)
        proxy.setPort(port)
        
        if user is not None:
            proxy.setUser(user)
            
        if password is not None:
            proxy.setPassword(password)
        
        self._proxyAuth = (user, password)
        self.setProxy(proxy)
    
    def setAuthCredentials(self, user, password):
        """Sets or update the auth credentials.
        
        :param user: the username used for the authentication
        :param password: the password used for the authentication
        """
        self._authIntent = 0
        self._auth = (user, password)
    
    def _authenticateProxy(self, mix, authenticator):
        username, password = self._proxyAuth
        authenticator.setUser(username)
        authenticator.setPassword(password)
        
    def _authenticate(self, mix, authenticator):
        # TODO: verify why exists a recursion with in the
        # authentication
        if self._authIntent == 0:
            username, password = self._auth
            authenticator.setUser(username)
            authenticator.setPassword(password)
        self._authIntent += 1
        
    def removeProxy(self):
        """Removes the proxy configuration
        """
        proxy = QNetworkProxy();
        proxy.setType(QNetworkProxy.NoProxy);
        self.setProxy(proxy)
        
    def createRequest(self, op, request, device=None):
        # FIXME: We have a problem here. Every request that is sended through
        # this NetworkAccessManager has the same Cache Policy. It's
        # Neccesary to move this to the Request or add some different
        # mechanism here.
        
        request.setAttribute(request.CacheLoadControlAttribute, QNetworkRequest.PreferCache)
        #FIXME: add regular expressions to avoid the loop
        #FIXME: It would be nice to use content type instead of the extension
        for ext in self._prevent_download:
            if unicode(request.url().toString()).endswith(ext):
                return super(NetworkAccessManager, self).createRequest(op, QNetworkRequest(QUrl()), device)
        
        reply = super(NetworkAccessManager, self).createRequest(op, request, device)
        self._add_resource(reply)
        return reply
    
    def _add_resource(self, reply, isStarting=True):
        self.networkMonitoring.add_resource(reply)
    
    def _add_resource_finished(self, reply):
        self.networkMonitoring.add_resource_finished(reply)
        