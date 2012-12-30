try:
    from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest
except ImportError:
    try:
        from PySide.QtNetwork import QNetworkAccessManager, QNetworkRequest
    except ImportError:
        raise Exception("Ghost.py requires PySide or PyQt")

import datetime, time
import hashlib

VERSION = "0.2b"

class NetworkMonitor(object):
    """
        We use the fllowing HAR specification
        http://www.softwareishard.com/blog/har-12-spec/
    """
    _entries = []
    _pages = {}
    
    def __init__(self):
        self._resources = {}
            
    def _get_time_now(self):
        #return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
        #return "2009-04-16T12:07:25.123+01:00"
        return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
    
    def _parse_time(self, time):
        #millis = int(round(time.time() * 1000))
        #print millis
        #return time.strftime("%Y-%m-%dT%H:%M:%S.%f:+00:00")
        #return "2009-04-16T12:07:25.123+01:00"
        return time.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
    
    def _get_milliseconds(self, timedelta):
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
            "stime": time.time(),
            "url": unicode(resource.url().toString())
        }
    
    def add_and_get_page(self, resource):
        url = unicode(resource.request().originatingObject().url().toString())
        key = "pk_{0}".format(url)
        
        if key not in self._pages:
            self._pages[key] = dict(url=url, entries=[])
        return key
    
    def add_resource_finished(self, resource):
        pageKey = self.add_and_get_page(resource)
        url = self._md5_name(unicode(resource.url().toString()))
        request = resource.request()
        startReply = self._resources[url]["start"]
        t = int((time.time() - startReply["stime"]) * 1000)
        
        print unicode(resource.url().toString())
        entry = {
            "startedDateTime": self._parse_time(startReply["time"]),
            "time": t,
            "request": {
                "method": self._get_operation_name(resource.operation()),
                "url": unicode(resource.url().toString()),
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
                "dns": 0,
                "connect": 0,
                "send": 0,
                "wait": 0, #self._get_seconds(datetime.datetime.now() - startReply["time"]),
                "receive": t, # self._get_seconds(datetime.datetime.now() - startReply["time"]),
                "ssl": 0
            },
            "pageref": pageKey
        }
        self._pages[pageKey]["entries"].append(entry)

            
    def dump(self, address, title):
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
                "pages": [],
                "entries": [],
                "comment": ""
            }
        }
        
        for pk in self._pages.keys():
            har["log"]["pages"].append(
                {
                    "startedDateTime": self._parse_time(datetime.datetime.now()),
                    "id":  pk,
                    "title": title,
                    "pageTimings": {},
                    "comment": ""
                })
            har["log"]["entries"] += self._pages[pk]["entries"]
        
        return har
        