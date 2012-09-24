import wsgiref.simple_server
import paste.auth.multi
import paste.auth.basic
import paste.proxy
import paste.urlmap

def start_proxy_app(port, port_forward, add_auth=False):
    def dummyauth(environ, username, password):
        return username == password
    
    url_forward = "http://localhost:{0}/".format(port_forward)
    simple_app = paste.urlmap.URLMap()
    proxy = paste.proxy.make_proxy(global_conf={}, address=url_forward,
            allowed_request_methods='')
    
    simple_app['/'] = proxy
    multi = paste.auth.multi.MultiHandler(simple_app)
    if add_auth:
        multi.add_method('basic', paste.auth.basic.middleware, "test", dummyauth)
        multi.set_default('basic')
    
    httpd = wsgiref.simple_server.make_server('', port, multi)
    httpd.serve_forever()

#start_proxy_app(5001, 5000)
#while 1: pass