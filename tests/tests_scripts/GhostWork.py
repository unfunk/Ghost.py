import pycurl
import urllib
import StringIO
import json
import logging
import sys

from BeautifulSoup import BeautifulSoup

from django.conf import settings
from ghost import Ghost
from ghost.BlackPearl import Pirate

def none_callback(x):
    return (x is not None, x)

class GhostWork(Pirate):
    
    def goto_cotization1(self):
        def ev():
            p = self.page.open("http://www.tokioweb.com.br/calculoweb/?page=101&codinterno=210&userid=willisltda&password=willis03",
                wait_onload_event=True, wait_for_loading=False)
            return True, p
        
        self.add_event(ev)
        self.add_event(self.page.get_loaded_page,
                       callback=none_callback)
        self.add_event(self.page.switch_to_frame, frameName="TMPC_IFRAME_CALC",
                       callback=none_callback)
        self.add_event(self.page.exists, selector="#frmHome",
                       callback=lambda x: (x, x))
        def ev():
            self.page.evaluate("""document.getElementById("frmHomePage").value   = 401;document.getElementById("frmHomePortal").value = parent.document.getElementById("frmMenuPortal").value;document.getElementById("frmHome").target      = "_self";document.getElementById("frmHome").submit();""")
            return True, None
        self.add_event(ev)
        self.add_event(self.page.exists, selector="#EDITINICIOVIGENCIA1",
                       callback=lambda x: (x, x))
            
        
    def fill_page1(self, data):
        def ev():
            self.page.evaluate('document.querySelector("#EDIT_CALCONLINE_SIM").click()')
            for key in data.keys():
                self.page.evaluate('document.querySelector("#%s").value = "%s";' % (key, data[key]))
            
            self.page.evaluate('document.querySelector("#BTNBUSCACHASSI").click()')
            return True, None
        self.add_event(ev)
        
        self.add_event(self.page.evaluate, script='document.querySelectorAll("#EDITVALORBASE1 option").length',
                callback=lambda x: (x > 1, None))
        
        def ev():
            self.page.evaluate("""document.querySelector("#EDITVALORBASE1").value = '18026';""")
            self.page.evaluate("""document.querySelector("#EDITPROCEDENCIA1").value = document.querySelectorAll("#EDITPROCEDENCIA1 option")[1].value;""")
            self.page.evaluate("""document.querySelector("#EDITPROCEDENCIA1").onchange();""")
            return True, None
        self.add_event(ev)
        
        self.add_event(self.page.evaluate, script='document.querySelector("#EDITVALORVEICULO1").value',
                callback=lambda x: (x != "0,00", None))

        self.add_event(self.page.evaluate, script='document.querySelector("#BTAVANCAR").click();',
                callback=lambda x: (True, None))
        
        self.add_event(self.page.get_current_frame_content,
                callback=lambda x: ("Entende-se como temp" in x, None))

        
    def fill_page2(self, data):
        def ev():
            for key in data.keys():
                self.page.evaluate('document.querySelector("#%s").value = "%s";' % (key, data[key]))
            
            self.page.evaluate("""document.querySelector("#BTAVANCAR").click();""");
            
            return True, None
        
        self.add_event(ev)
        self.add_event(self.page.get_current_frame_content,
                callback=lambda x: ("Danos Materiais" in x, None))
        
        def ev():
            dic = {
                "code": unicode(self.page.evaluate("""document.querySelector("#CHAVE").value.split(";")[0]""")),
                "sourceParcFichaAV": self.__parse_vars(self.page.evaluate("sourceParcFichaAV")),
                "sourceParcDebitoAV": self.__parse_vars(self.page.evaluate("sourceParcDebitoAV"))
            }
            return True, dic
        self.add_event(ev)
    
    def __parse_vars(self, var):
        ret = []
        for i in range(len(var)):
            dic = {}
            for key in var[i]:
                dic[unicode(key)] = unicode(var[i][key])
            ret.append(dic)
        
        return ret
                
    
    def start(self,  data):
        data = json.loads(data)
        self.goto_cotization1()
        self.fill_page1(data["step1"])
        self.fill_page2(data["step2"])
    
    def get_result(self):
        return self._last_result
