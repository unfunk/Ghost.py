from ghost import Ghost
import logging

gh = Ghost(display=True, cache_size=10000, wait_timeout=200,
           download_images=False, log_level=logging.DEBUG, prevent_download=["css", "jquery"])

#gh.open("http://www.tokioweb.com.br/calculoweb/login/login01.htm", wait_onload_event=False)

#gh.evaluate("""
#            document.querySelector('#codinterno').value = "210";
#            document.querySelector('#userid').value = "willisltda";
#            document.querySelector('#password').value = "willis03";
#            document.querySelector('#frmLogin').submit();
#            """)
print "Opening"
gh.open("http://www.tokioweb.com.br/calculoweb/?page=101&codinterno=210&userid=willisltda&password=willis03",
        wait_onload_event=True)
#gh.open("http://www.facebook.com")
gh.switch_to_frame("TMPC_IFRAME_CALC")
gh.wait_for_selector("#frmHome")
print "Going to next page"
gh.evaluate("""
            document.getElementById("frmHomePage").value   = 401;
            document.getElementById("frmHomePortal").value = parent.document.getElementById("frmMenuPortal").value;
            document.getElementById("frmHome").target      = "_self";
            document.getElementById("frmHome").submit();
            """)

#gh.switch_to_frame("TMPC_IFRAME_CALC")
gh.wait_for_selector("#EDITINICIOVIGENCIA1")
print "Page cotization loaded"

print unicode(gh.page.currentFrame().toHtml())
#print gh.evaluate("""document.getElementById("frmHomePage").value   = 401;""")
import pdb; pdb.set_trace()      

def a():
    gh.evaluate("""
            document.getElementById("frmHomePage").value   = 401;
            document.getElementById("frmHomePortal").value = parent.document.getElementById("frmMenuPortal").value;
            document.getElementById("frmHome").target      = "_self";
            document.getElementById("frmHome").submit();
            """)

