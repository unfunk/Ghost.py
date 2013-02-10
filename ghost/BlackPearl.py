# -*- coding: utf-8 -*-
import os, random, hashlib, json, logging
import subprocess

from flask import Flask
from flask import request, Response
from ghost import Ghost

logging.basicConfig()
logger = logging.getLogger('ghost')

class Logger(logging.Logger):
    @staticmethod
    def log(message, sender="Ghost", level="info"):
        if not hasattr(logger, level):
            raise Exception('invalid log level')
        getattr(logger, level)("%s: %s", sender, message)
        

class Pirate():
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
    
    
class BlackPearl():
    
    def __init__(self, pirateClass, port=8000):
        """This is a Server that wake up Ghost instances.
        :param pirateClass: The class that we want to instanciate to do the work
        :param port: The port where the server will run
        """
        self._pirateClass = pirateClass
        self._port = port
    
    def start(self, command):
        Logger.log("Starting BlackPearl Server", sender="BlackPearl")
        self._start_server(command, self._port)
        
    def _start_server(self, command, port):
        self._server = Flask(__name__)
        self._server.config['CSRF_ENABLED'] = False
        self._server.config['SECRET_KEY'] = 'asecret'
        
        @self._server.route('/work', methods=['POST'])
        def work():
            data = request.values.to_dict().get("data", None)
            ret = self._start_process(command, data)
            return Response(ret)
        
        self._server.run(threaded=True)
        
    def _start_process(self, command, data=None):
        Logger.log("Starting Pirate Instance", sender="BlackPearl")
        
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        
        result = p.communicate(input=data)[0]
        print result
        
        #p.communicate(input="hola")
        #p.wait()
        #pirate = self._pirateClass()
        #pirate.start(data)
        Logger.log("Ending Pirate Instance", sender="BlackPearl")
        
        return result
        
