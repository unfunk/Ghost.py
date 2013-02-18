# -*- coding: utf-8 -*-
import os, random, hashlib, json, logging
import subprocess, time

from flask import Flask
from flask import request, Response
from threading import Thread

logging.basicConfig()
logger = logging.getLogger('ghost')

class Logger(logging.Logger):
    @staticmethod
    def log(message, sender="Ghost", level="info"):
        if not hasattr(logger, level):
            raise Exception('invalid log level')
        getattr(logger, level)("%s: %s", sender, message)


class Event:
    
    def __init__(self, method, callback=None, sleep_time=1, *args, **kwargs):
        self.method = method
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.sleep_time = sleep_time
        
    def execute(self):
        if self.callback is None:
            self._is_ready, self._result = self.method(*self.args, **self.kwargs)
        else:
            self._is_ready, self._result = self.callback(self.method(*self.args, **self.kwargs))
        
        if self._is_ready:
            return 0
        return self.sleep_time
    
    def get_results(self):
        return self._result
    
    def is_ready(self):
        return self._is_ready
        
        
class Pirate():
    def __init__(self, ghost):
        self.gh = ghost
        self.events = []
        self.page, name = self.gh.create_page()
        
    def add_event(self, method, callback=None, *args, **kwargs):
        self.events.append(Event(method, callback, *args, **kwargs))
    
    def has_events(self):
        return len(self.events) > 0
    
    def get_event(self):
        if len(self.events) == 0:
            return None
        
        return self.events.pop(0)
    
    def event_ready(self, ev):
        if ev.is_ready():
            self._last_result = ev.get_results()
        else:
            self.events.insert(0, ev)
    
    def start(self, data=None):
        """Starts the ghost implementation
        :param data: An initial information for Ghost
        """
        raise NotImplementedError()
    
    def get_result(self):
        """Return the result of the Ghost scrapping
        :return: An String with the information obtained
        """
        raise NotImplementedError()
    
    def __del__(self):
        self.gh.remove_page(self.page)


class PirateRequest:
    def __init__(self, request_life, name, pirate):
        self.end = time.time() + request_life
        self.name = name
        self.pirate = pirate
    
    def is_old(self):
        return self.end < time.time()

        
class BlackPearl():
    
    def __init__(self, ghost, pirateClass, port=8000, request_life=300):
        """This is a Server that wake up Ghost instances.
        :param pirateClass: The class that we want to instanciate to do the work
        :param port: The port where the server will run
        """
        self._pirateClass = pirateClass
        self._port = port
        self._pirates = []
        self._start_request = []
        self._request_ready = {}
        self._sleep_bag = {}
        self.gh = ghost
        self.request_life = request_life
        
    def start(self):
        Logger.log("Starting BlackPearl Server", sender="BlackPearl")
        self._start_server(self._port)
        self.process_events()
                
    def _start_server(self, port):
        self._server = Flask(__name__)
        self._server.config['CSRF_ENABLED'] = False
        self._server.config['SECRET_KEY'] = 'asecret'
        
        @self._server.route('/work', methods=['POST'])
        def work():
            data = request.values.to_dict().get("data", None)
            name = self._start_process(data)
            
            while self._request_ready[name] is None:
                time.sleep(1)
            Logger.log("Ending Pirate Instance", sender="BlackPearl")
            return Response(json.dumps(self._request_ready[name]))
        
        self.server = Thread(target=self._server.run, kwargs=dict(threaded=True))
        self.server.start()
        #self._server.run(threaded=True)
        
    def _start_process(self, data=None):
        Logger.log("Starting Pirate Instance", sender="BlackPearl")
        
        # Encola todos los eventos
        name = str(random.randint(0, 999999999))
        self._request_ready[name] = None
        self._start_request.append((name, data))
        
        return name
    
    def _set_ready(self, pirateRequest, data):
        self._request_ready[pirateRequest.name] = data
        self._pirates.remove(pirateRequest)
        del pirateRequest.pirate
    
    def _queue_pirates(self):
        while len(self._start_request) > 0:
            name, data = self._start_request.pop(0)
            pirate = self._pirateClass(self.gh)
            pirate.start(data)
            #self._pirates.append((name, pirate))
            self._pirates.append(PirateRequest(self.request_life, name, pirate))
            
            
    def process_events(self):
        j = 0
        while True:
            try:
                self._queue_pirates()
                
                for pr in self._pirates:
                    name, pirate = pr.name, pr.pirate
                    
                    Logger.log("Executing Event", sender="BlackPearl")
                    ev = pirate.get_event()
                    if ev is not None:
                        try:
                            self.gh.process_events()
                            if pr.is_old():
                                is_ready = True
                                Logger.log("Error. Old request", sender="BlackPearl")
                            else:
                                if ev in self._sleep_bag and self._sleep_bag[ev] > time.time():
                                    # we wait for this
                                    pirate.event_ready(ev)
                                    break
                                sleep_time = ev.execute()
                                pirate.event_ready(ev)
                                is_ready = not pirate.has_events()
                                
                                if sleep_time > 0.0 and not is_ready:
                                    self._sleep_bag[ev] = time.time() + sleep_time
                                self.gh.process_events()    
                        except Exception as ex:
                            print ex
                            is_ready = True
                            Logger.log("Error. Removing element", sender="BlackPearl")
                        
                        if is_ready:
                            data = pirate.get_result()
                            self._set_ready(pr, data)
                            
                            if ev in self._sleep_bag:
                                del self._sleep_bag[ev]
                                
                if len(self._start_request) == 0 and len(self._pirates) == 0:
                    time.sleep(0.1)
                    
            except KeyboardInterrupt:
                Logger.log("Keyboard interupt. Let get out of here.", sender="BlackPearl")
                self.server._Thread__stop()
                break
                