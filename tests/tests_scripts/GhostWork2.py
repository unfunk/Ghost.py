import pycurl
import urllib
import StringIO
import json
import logging
import sys

from BeautifulSoup import BeautifulSoup

from django.conf import settings
from ghost import Ghost


from ghost.BlackPearl import BlackPearl, Pirate

data = json.loads('{"step4": {"EDITASSISTENCIA24H": "C", "EDITVIDROS": "1"}, "step3": {"EDIT_FRANQUIA": "1", "EDITACIDENTES_PASSAGEIROS": 0, "EDITTEMKITGAS": "N", "EDITDANOSMATERIAIS": "50000", "EDITTIPO_COBERTURA": "1", "EDITDANOSCORPORAIS": "50000", "EDITKITGAS": "0", "EDITDANOSMORAIS": "0,00"}, "mode": "full", "step1": {"EDITKITGAS_SN": "N", "EDITBLINDAGEM1": "N", "CB000054": "N\\u00e3o", "CB000994": "Oficina Livre", "EDITANOFABRICACAO1": "2008", "EDITNIVELBONUSAUTO1": 0, "EDITCOR": "Preto", "EDITMODELO1": "14544", "EDITVALORAPPMORTE1": 0, "EDIT243": "582", "CB000040_2": "B\\u00e1sico", "EDITNIVELDP1": "50000", "EDITFINALVIGENCIA1": "07/08/2013", "EDITNOME1": "REGIS MARCELO SAPIAGINSKI ", "EDITNOMECONDUTOR": "REGIS MARCELO SAPIAGINSKI ", "EDITTIPO_PESSOA1": "F", "EDITVALORAPPDMH1": "0,00", "EDITZEROKM1": "N", "EDITLMI_BLINDAGEM1": "0,00", "CB000997": "1.0", "PILOTODECODIFICADOR": "S", "EDITDISPOSITIVO": "0", "MULT_CALCULOFABRICANTE": "99", "EDITTIPODEUSOVEIC1": "A", "EDITQBR_SN": "S", "EDITCPF": "703.218.099-04", "EDIT_CALCONLINE_SIM": "S", "EDITINICIOVIGENCIA1": "07/02/2013", "EDITCEP1": "78890-000", "EDITESTADO1_2": "C", "EDITNIVELDM1": "50000", "EDITTIPO_COBERTURA1": "1", "EDITP_AJUSTE1": "100,00", "CB000979": "N\\u00e3o", "EDITVALORBASE1": "", "EDITPROCEDENCIA1": "G", "EDITCNHCONDUTOR": "", "EDITCNPJ": "", "EDITMODALIDADE1": "A", "EDITANOMODELO1": "2008", "EDITFABRICANTE1": "99", "EDITPLACA": "tre1234", "EDITTIPOSEGURO": "4", "EDITCPFCONDUTOR": "703.218.099-04", "EDITCHASSI": "9BWCA01JX84030926", "EDITNUMPASSAG1": "0", "EDITLMI_KITGAS1": "0", "CB000945_2": "N\\u00e3o", "CB000946": "N\\u00e3o Possui"}, "operation": "cotization", "step2": {"EDITNASCIMENTO": "10/10/1986", "EDIT261": "714", "EDIT260": "711", "CBESTADOCIVIL": "B", "CBSEXO": "M", "EDIT252": "672", "EDIT250": "662", "EDIT251": "", "EDIT256": "691", "EDIT257": "696", "EDIT255": "685", "EDIT258": "699", "EDIT259": "704", "EDIT249": "659"}}')

def setTimeout(time, func, *args):
    pass

class GhostWork(Pirate):
    def __init__(self, ghost):
        """
        self.gh = Ghost(display=False,
            cache_size=10000,
            wait_timeout=30,
            prevent_download=["jpg", "png", "gif", "css"],
            download_images=False)
        """
        self.ghost = ghost
        self.page, name = self.ghost.create_page()
        
    def goto_cotization2(self):
        
        self.page.open("http://www.tokioweb.com.br/calculoweb/?page=101&codinterno=210&userid=willisltda&password=willis03",
            wait_onload_event=True)
        
        self.page.switch_to_frame("TMPC_IFRAME_CALC")
        self.page.wait_for_selector("#frmHome")
        self.page.evaluate("""
            document.getElementById("frmHomePage").value   = 401;
            document.getElementById("frmHomePortal").value = parent.document.getElementById("frmMenuPortal").value;
            document.getElementById("frmHome").target      = "_self";
            document.getElementById("frmHome").submit();
            """)
        
        self.page.wait_for_selector("#EDITINICIOVIGENCIA1")
    
    
    def goto_cotization2(self):
        
        self.page.open("http://www.tokioweb.com.br/calculoweb/?page=101&codinterno=210&userid=willisltda&password=willis03",
            wait_onload_event=True)
        
        self.page.switch_to_frame("TMPC_IFRAME_CALC")
        
        #setTimeout(0.01, lambda: self.page.wait_for_selector("#frmHome"))
        self.page.wait_for_selector("#frmHome")
        self.page.evaluate("""
            document.getElementById("frmHomePage").value   = 401;
            document.getElementById("frmHomePortal").value = parent.document.getElementById("frmMenuPortal").value;
            document.getElementById("frmHome").target      = "_self";
            document.getElementById("frmHome").submit();
            """)
        
        self.page.wait_for_selector("#EDITINICIOVIGENCIA1")
        
    def fill_page1(self, data):
        self.page.evaluate('document.querySelector("#EDIT_CALCONLINE_SIM").click()')
        for key in data.keys():
            self.page.evaluate('document.querySelector("#%s").value = "%s";' % (key, data[key]))
        
        self.page.evaluate('document.querySelector("#BTNBUSCACHASSI").click()')
        
        self.page.wait_for(
            lambda: self.page.evaluate('document.querySelectorAll("#EDITVALORBASE1 option").length')[0] > 1, "mal"
        )
        
        self.page.evaluate("""document.querySelector("#EDITVALORBASE1").value = '18026';""")
        self.page.evaluate("""document.querySelector("#EDITPROCEDENCIA1").value = document.querySelectorAll("#EDITPROCEDENCIA1 option")[1].value;""")
        self.page.evaluate("""document.querySelector("#EDITPROCEDENCIA1").onchange();""")
        
        self.page.wait_for(
            lambda: self.page.evaluate('document.querySelector("#EDITVALORVEICULO1").value')[0] != "0,00", "mal"
        )
        
        self.page.evaluate("""document.querySelector("#BTAVANCAR").click();""");        
        
        self.page.wait_for_text("Entende-se como temp")

        
    def fill_page2(self, data):
        
        for key in data.keys():
            self.page.evaluate('document.querySelector("#%s").value = "%s";' % (key, data[key]))
        
        self.page.evaluate("""document.querySelector("#BTAVANCAR").click();""");
        
        self.page.wait_for_text("Danos Materiais")
        
        dic = {
            "code": unicode(self.page.evaluate("""document.querySelector("#CHAVE").value.split(";")[0]""")[0]),
            "sourceParcFichaAV": self.__parse_vars(self.page.evaluate("sourceParcFichaAV")[0]),
            "sourceParcDebitoAV": self.__parse_vars(self.page.evaluate("sourceParcDebitoAV")[0])
        }
        
        return  json.dumps(dic)
    
    def __parse_vars(self, var):
        ret = []
        for i in range(len(var)):
            dic = {}
            for key in var[i]:
                dic[unicode(key)] = unicode(var[i][key])
            ret.append(dic)
        
        return ret
                
    
    def start(self,  data):
        self.goto_cotization1()
        self.fill_page1(data["step1"])
        html = self.fill_page2(data["step2"])
        self._result = html
        return html
    
    def get_result(self):
        return self._result


class GhostWork(Pirate):
    def __init__(self, ghost):
        """
        self.gh = Ghost(display=False,
            cache_size=10000,
            wait_timeout=30,
            prevent_download=["jpg", "png", "gif", "css"],
            download_images=False)
        """
        self.ghost = ghost
        self.page, name = self.ghost.create_page()
        
    def goto_cotization1(self):
        
        self.page.open("http://www.tokioweb.com.br/calculoweb/?page=101&codinterno=210&userid=willisltda&password=willis03",
            wait_onload_event=True)
        
        self.page.switch_to_frame("TMPC_IFRAME_CALC")
        
        while self.page.exists("#frmHome"):
            import time; time.sleep(1)
        
        self.page.evaluate("""
            document.getElementById("frmHomePage").value   = 401;
            document.getElementById("frmHomePortal").value = parent.document.getElementById("frmMenuPortal").value;
            document.getElementById("frmHome").target      = "_self";
            document.getElementById("frmHome").submit();
            """)
        
        while self.page.exists("#EDITINICIOVIGENCIA1"):
            import time; time.sleep(1)
        
    def start(self,  data):
        self.goto_cotization1()
        return self.page.get_current_frame_content()
    
    def get_result(self):
        return self._result


#data = sys.stdin.read()
#data = json.loads(data)
#gw = GhostWork()
#gw.start(data)
#html = gw.get_result()

#sys.stdout.write(html)
