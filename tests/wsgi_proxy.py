import wsgiref.simple_server
import paste.auth.multi
import paste.auth.basic
import paste.proxy
import paste.urlmap

def start_proxy_app(port, port_forward, add_auth=False):
    print "Proxy started in {0}  redirecting to {1}".format(port, port_forward)
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

if __name__ == '__main__':
    start_proxy_app(5001, 5000, True)
    while 1: pass