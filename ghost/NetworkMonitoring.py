try:
    from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest
except ImportError:
    try:
        from PySide.QtNetwork import QNetworkAccessManager, QNetworkRequest
    except ImportError:
        raise Exception("Ghost.py requires PySide or PyQt")

import datetime
import hashlib

VERSION = "0.2b"

class NetworkMonitoring(object):
    """
        We use the fllowing HAR specification
        http://www.softwareishard.com/blog/har-12-spec/
    """
    _entries = []
    _pages = {}
    
    def __init__(self):
        self._resources = {}
            
    def _get_time_now(self):
        return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    
    def _parse_time(self, time):
        return time.strftime("%Y-%m-%dT%H:%M:%S.%f")
    
    def _get_seconds(self, timedelta):
        return (timedelta.days * 24 * 60 * 60) + (timedelta.seconds)
    
    def _md5_name(self, url):
        m = hashlib.md5()
        m.update(str(url))
        return m.hexdigest()
    
    def _get_operation_name(self, operation):
        if operation == QNetworkAccessManager.PutOperation:
            return "PUT"
        elif operation == QNetworkAccessManager.PostOperation:
            return "POST"
        elif operation == QNetworkAccessManager.DeleteOperation:
            return "DELETE"
        return "GET"
    
    def _get_list_of_headers(self, resource):
        headers = []
        resource.rawHeader(unicode(resource.rawHeaderList()[0]))
        for i in resource.rawHeaderList():
            headers.append({
                "name": unicode(i),
                "value": unicode(resource.rawHeader(i)),
                "comment": ""
            })
        return headers
    
    def _get_list_of_query_items(self, resource):
        items = []
        pairs = resource.url().queryItems()
        for i in range(0, len(pairs), 2):
            items.append({
                "name": unicode(pairs[i]),
                "value": unicode(pairs[i+1]),
                "comment": ""
            })
        
        return items
    
    def _get_list_of_cookies(self, resource):
        headers = resource.header(QNetworkRequest.CookieHeader)
        ret = []
        if headers is not None:
            for h in headers:
                ret.append(unicode(h.toRawForm()))
        return ret
    
            
    def add_resource(self, resource):
        url = self._md5_name(unicode(resource.url().toString()))
        if url not in self._resources:
            self._resources[url] = {}
            
        self._resources[url]["start"] = {
            "time": datetime.datetime.now(),
            "url": unicode(resource.url().toString())
        }
    
    def add_and_get_page(self, resource):
        url = unicode(resource.request().originatingObject().url().toString())
        #pageUrl = unicode(resource.request().url().toString())
        #key = self._md5_name(url)
        key = url
        
        if key not in self._pages:
            self._pages[key] = dict(url=url, entries=[])
        return key
    
    def add_resource_finished(self, resource):
        pageKey = self.add_and_get_page(resource)
        url = self._md5_name(unicode(resource.url().toString()))
        request = resource.request()
        startReply = self._resources[url]["start"]
        address = ""

        entry = {
            "startedDateTime": self._parse_time(startReply["time"]),
            "time": self._get_seconds(datetime.datetime.now() - startReply["time"]),
            "request": {
                "method": self._get_operation_name(resource.operation()),
                "url": resource.url().toString(),
                "httpVersion": "HTTP/1.1",
                "cookies": self._get_list_of_cookies(request),
                "headers": self._get_list_of_headers(request),
                "queryString": self._get_list_of_query_items(resource),
                "headersSize": -1,
                "bodySize": -1
            },
            "response": {
                "status": resource.attribute(QNetworkRequest.HttpStatusCodeAttribute),
                "statusText": "",
                "httpVersion": "HTTP/1.1",
                "cookies": self._get_list_of_cookies(resource),
                "headers": self._get_list_of_headers(resource),
                "redirectURL": "",
                "headersSize": -1,
                "bodySize": -1,
                "content": {
                    "size": -1,
                    "mimeType": ""
                }
            },
            "cache": {},
            "timings": {
                "blocked": 0,
                "dns": -1,
                "connect": -1,
                "send": 0,
                "wait": self._get_seconds(datetime.datetime.now() - startReply["time"]),
                "receive": self._get_seconds(datetime.datetime.now() - startReply["time"]),
                "ssl": -1
            },
            "pageref": address
        }
        self._pages[pageKey]["entries"].append(entry)
            
    def dump(self, address, title):
        print self._pages.keys()
        import pdb; pdb.set_trace()
        har = {
            "log": {
                "version" : VERSION,
                "creator" : {
                    "name": "Ghost.py",
                    "version": VERSION,
                    "comment": ""
                },
                "browser": {
                    "name": "Ghost.py",
                    "version": VERSION,
                    "comment": ""
                },
                "pages": [
                    {
                        "startedDateTime": self._parse_time(datetime.datetime.now()),
                        "id": self._md5_name(address),
                        "title": title,
                        "pageTimings": {},
                        "comment": ""
                    }
                ],
                "entries": self._entries,
                "comment": ""
            }
        }
        
        return har
    
    def reset(self):
        self._entries = []
        