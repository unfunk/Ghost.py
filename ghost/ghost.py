# -*- coding: utf-8 -*-
import sys
import os
import time
import codecs
import json
import logging
import subprocess
import random

from functools import wraps
from cookielib import Cookie, LWPCookieJar
try:
    import sip
    sip.setapi('QVariant', 2)
    
    from PyQt4 import QtWebKit, QtCore
    from PyQt4.QtWebKit import QWebPage
    from PyQt4.QtNetwork import QNetworkRequest, QNetworkAccessManager,\
                                QNetworkCookieJar, QNetworkDiskCache, \
                                QNetworkReply, QNetworkCookie
    from PyQt4.QtCore import QSize, QByteArray, QUrl, QDateTime, \
                                SIGNAL, pyqtSlot, pyqtSignal, \
                                QtCriticalMsg, QtDebugMsg, QtFatalMsg, \
                                QtWarningMsg, qInstallMsgHandler
    from PyQt4.QtGui import QApplication, QImage, QPainter
    
except ImportError:
    try:
        from PySide import QtWebKit, QtCore
        from PySide.QtWebKit import QWebPage
        from PySide.QtNetwork import QNetworkRequest, QNetworkAccessManager,\
                                    QNetworkCookieJar, QNetworkDiskCache, \
                                    QNetworkReply, QNetworkCookie
        from PySide.QtCore import QSize, QByteArray, QUrl, QDateTime, SIGNAL, \
                                QtCriticalMsg, QtDebugMsg, QtFatalMsg, \
                                QtWarningMsg, qInstallMsgHandler
        from PySide.QtCore import Slot as pyqtSlot
        from PySide.QtCore import Signal as pyqtSignal

        from PySide.QtGui import QApplication, QImage, QPainter
    except ImportError:
        raise Exception("Ghost.py requires PySide or PyQt")

from NetworkAccessManager import NetworkAccessManager
from pdf import Pdf

default_user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.2 " +\
    "(KHTML, like Gecko) Chrome/15.0.874.121 Safari/535.2"


logging.basicConfig()
logger = logging.getLogger('ghost')

class Logger(logging.Logger):
    @staticmethod
    def log(message, sender="Ghost", level="info"):
        if not hasattr(logger, level):
            raise Exception('invalid log level')
        getattr(logger, level)("%s: %s", sender, message)


class QTMessageProxy(object):
    """
        Redirects messages from QT Framework to python logging
    """
    def __init__(self, debug=False):
        self.debug = debug

    def __call__(self, msgType, msg):
        if msgType == QtDebugMsg and self.debug:
            Logger.log(msg, sender='QT', level='debug')
        elif msgType == QtWarningMsg and self.debug:
            Logger.log(msg, sender='QT', level='warning')
        elif msgType == QtCriticalMsg:
            Logger.log(msg, sender='QT', level='critical')
        elif msgType == QtFatalMsg:
            Logger.log(msg, sender='QT', level='fatal')
        elif self.debug:
            Logger.log(msg, sender='QT', level='info')

        
def can_load_page(func):
    """Decorator that specifies if user can expect page loading from
    this action. If expect_loading is set to True, ghost will wait
    for page_loaded event.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        expect_loading = False
        if 'expect_loading' in kwargs:
            expect_loading = kwargs['expect_loading']
            del kwargs['expect_loading']
        if expect_loading:
            self._reset_for_loading()
            func(self, *args, **kwargs)
            return self.wait_for_page_loaded()
        return func(self, *args, **kwargs)
    return wrapper


def client_utils_required(func):
    """Decorator that checks avabality of Ghost client side utils,
    injects require javascript file instead.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.global_exists('GhostUtils'):
            self.evaluate_js_file(
                os.path.join(os.path.dirname(__file__), 'utils.js'))
        return func(self, *args, **kwargs)
    return wrapper


class GhostWebPage(QWebPage):
    """Overrides QtWebKit.QWebPage in order to intercept some graphical
    behaviours like alert(), confirm().
    Also intercepts client side console.log().
    
    :param app: a QApplication that it's running Ghost.
    :param network_manager: a NetworkManager instance in charge of managing all the network
        requests.
    :param wait_timeout: Maximum step duration in second.
    :param wait_callback: An optional callable that is periodically
        executed until Ghost stops waiting.
    :param viewport_size: A tupple that sets initial viewport size.
    :param user_agent: The default User-Agent header.
    :param log_level: The optional logging level.
    :param download_images: Indicate if the browser download or not the images
    :param plugins_enabled: Enable plugins (like Flash).
    :param java_enabled: Enable Java JRE.
    :param create_page_callback: A method called when a popup it's opened
    :param is_popup: Boolean who indicate if the page it's a popup
    :param max_resource_queued: Indicates witch it's the max number of resources that can be
            saved in memory. If None then no limits are applied. If 0 then no resources are kept/
            If the number it's > 0 then the number of resources won't be more than max_resource_queued
    """
    user_agent = ""
    removeWindowFromList = pyqtSignal(object)
    
    _alert = None
    _confirm_expected = None
    _prompt_expected = None
    _upload_file = None
    _app = None
    
    def __init__(self, app, network_manager, wait_timeout=20, wait_callback=None,
                viewport_size=(800, 600), user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.121 Safari/535.2',
                log_level=30, download_images=True, plugins_enabled=False,
                java_enabled=False, create_page_callback=None,
                is_popup=False, max_resource_queued=None,
                *args, **kargs):
        
        super(GhostWebPage, self).__init__(parent=app)
        self._app = app
        self.pdf_engine = Pdf()
        self.http_resources = []
        self.http_resource_page = None
        self.max_resource_queued = max_resource_queued
        self.wait_timeout = wait_timeout
        self.wait_callback = wait_callback
        self.loaded = True
        self.create_page_callback = create_page_callback
        self.is_popup = is_popup
        # Internal library object
        self.ghostInit =  GhostInit()
        
        self.setForwardUnsupportedContent(True)
        self.settings().setAttribute(QtWebKit.QWebSettings.AutoLoadImages, download_images)
        self.settings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)
        self.settings().setAttribute(QtWebKit.QWebSettings.JavascriptCanOpenWindows, True)
        self.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, plugins_enabled)
        self.settings().setAttribute(QtWebKit.QWebSettings.JavaEnabled, java_enabled)

        self.set_viewport_size(*viewport_size)

        # Page signals
        self.loadFinished.connect(self._page_loaded)
        self.loadStarted.connect(self._page_load_started)
        self.loadProgress.connect(self._page_load_progress)
        self.unsupportedContent.connect(self._unsupported_content)
        self.network_manager = network_manager
        self.setNetworkAccessManager(self.network_manager)
        self.network_manager.finished.connect(self._request_ended)
        # User Agent
        self.setUserAgent(user_agent)

        self.main_frame = self.mainFrame()
        self._unsupported_files = {}
        self.windowCloseRequested.connect(self._closeWindow)
        
        logger.setLevel(log_level)
        
    
    class confirm:
        """Statement that tells Ghost how to deal with javascript confirm().

        :param confirm: A bollean that confirm.
        :param callable: A callable that returns a boolean for confirmation.
        """
        def __init__(self, confirm=True, callback=None):
            self.confirm = confirm
            self.callback = callback

        def __enter__(self):
            GhostWebPage._confirm_expected = (self.confirm, self.callback)

        def __exit__(self, type, value, traceback):
            GhostWebPage._confirm_expected = None
    
    
    class prompt:
        """Statement that tells Ghost how to deal with javascript prompt().

        :param value: A string value to fill in prompt.
        :param callback: A callable that returns the value to fill in.
        """
        def __init__(self, value='', callback=None):
            self.value = value
            self.callback = callback

        def __enter__(self):
            GhostWebPage._prompt_expected = (self.value, self.callback)

        def __exit__(self, type, value, traceback):
            GhostWebPage._prompt_expected = None     
            
    def chooseFile(self, frame, suggested_file=None):
        return self._upload_file

    def javaScriptConsoleMessage(self, message, line, source):
        """Prints client console message in current output stream."""
        super(GhostWebPage, self).javaScriptConsoleMessage(message, line,
            source)
        log_type = "error" if "Error" in message else "info"
        Logger.log("%s(%d): %s" % (source or '<unknown>', line, message),
        sender="Frame", level=log_type)

    def javaScriptAlert(self, frame, message):
        """Notifies ghost for alert, then pass."""
        self._alert = message
        Logger.log("alert('%s')" % message, sender="Frame")

    def javaScriptConfirm(self, frame, message):
        """Checks if ghost is waiting for confirm, then returns the right
        value.
        """
        if GhostWebPage._confirm_expected is None:
            raise Exception('You must specified a value to confirm "%s"' %
                message)
        
        confirmation, callback = GhostWebPage._confirm_expected
        GhostWebPage._confirm_expected = None
        Logger.log("confirm('%s')" % message, sender="Frame")
        if callback is not None:
            return callback()
        return confirmation

    def javaScriptPrompt(self, frame, message, defaultValue, result=None):
        """Checks if ghost is waiting for prompt, then enters the right
        value.
        """
        if GhostWebPage._prompt_expected is None:
            raise Exception('You must specified a value for prompt "%s"' %
                message)
        result_value, callback = GhostWebPage._prompt_expected
        Logger.log("prompt('%s')" % message, sender="Frame")
        if callback is not None:
            result_value = callback()
        if result_value == '':
            Logger.log("'%s' prompt filled with empty string" % message,
                level='warning')
        GhostWebPage._prompt_expected = None
        if result is None:
            # PySide
            return True, result_value
        result.append(result_value)
        return True

    def setUserAgent(self, user_agent):
        self.user_agent = user_agent

    def userAgentForUrl(self, url):
        return self.user_agent
    
    def acceptNavigationRequest(self, frame, request, ttype):
        self._lastUrl = request.url()
        return True
    
    def createWindow(self, ttype):
        page = None
        if self.create_page_callback is not None:
            page, name = self.create_page_callback(is_popup=True)
            page.open(self._lastUrl)
            
        return page
    
    def _closeWindow(self):
        #if self._main_window is not None:
        self.removeWindowFromList.emit(self)
        
    def switch_to_sub_window(self, index):
        """Change the focus to the sub window (popup)
        :param index: The index of the window, in the order that the
            window was opened
        """
        if len(self._windows) > index:
            self._windows[index].mainFrame().setFocus()
            return self._windows[index]                    
        return None
    
    def capture(self, region=None, selector=None,
            format=QImage.Format_ARGB32_Premultiplied):
        """Returns snapshot as QImage.

        :param region: An optional tupple containing region as pixel
            coodinates.
        :param selector: A selector targeted the element to crop on.
        :param format: The output image format.
        """
        if region is None and selector is not None:
            region = self.region_for_selector(selector)
        if region:
            x1, y1, x2, y2 = region
            w, h = (x2 - x1), (y2 - y1)
            image = QImage(QSize(x2, y2), format)
            painter = QPainter(image)
            self.currentFrame().render(painter)
            painter.end()
            image = image.copy(x1, y1, w, h)
        else:
            self.currentFrame().setScrollBarPolicy(QtCore.Qt.Vertical,
                                QtCore.Qt.ScrollBarAlwaysOff)
            self.currentFrame().setScrollBarPolicy(QtCore.Qt.Horizontal,
                                QtCore.Qt.ScrollBarAlwaysOff)
            self.setViewportSize(self.currentFrame().contentsSize())
            image = QImage(self.viewportSize(), format)
            painter = QPainter(image)
            self.currentFrame().render(painter)
            painter.end()
        return image   
    
    
    def capture_to(self, path, region=None, selector=None,
        format=QImage.Format_ARGB32_Premultiplied):
        """Saves snapshot as image.

        :param path: The destination path.
        :param region: An optional tupple containing region as pixel
            coodinates.
        :param selector: A selector targeted the element to crop on.
        :param format: The output image format.
            The available formats can be found here http://qt-project.org/doc/qt-4.8/qimage.html#Format-enum
            There is also a "pdf" format that will render the page into a pdf file
        """
        if str(format).startswith("pdf"):
            return self.pdf_engine.render_pdf(self, path)
        else:
            self.capture(region=region, format=format,
                selector=selector).save(path)
            
    
    @client_utils_required
    def region_for_selector(self, selector):
        """Returns frame region for given selector as tupple.

        :param selector: The targeted element.
        """
        geo = self.currentFrame().findFirstElement(selector).geometry()
        try:
            region = (geo.left(), geo.top(), geo.right(), geo.bottom())
        except:
            raise Exception("can't get region for selector '%s'" % selector)
        return region
    
    
    @client_utils_required
    @can_load_page
    def click(self, selector):
        """Click the targeted element.

        :param selector: A CSS3 selector to targeted element.
        """
        if not self.exists(selector):
            raise Exception("Can't find element to click")
        return self.evaluate('GhostUtils.click("%s");' % selector)
    
    
    @property
    def content(self):
        """Returns main_frame HTML as a string."""
        return unicode(self.main_frame.toHtml())

    
    def get_current_frame_content(self):
        """Returns current frame HTML as a string."""
        return unicode(self.currentFrame().toHtml())
    
    @can_load_page
    def evaluate(self, script):
        """Evaluates script in page frame.

        :param script: The script to evaluate.
        """
        return self.currentFrame().evaluateJavaScript("%s" % script)

    def evaluate_js_file(self, path, encoding='utf-8'):
        """Evaluates javascript file at given path in current frame.
        Raises native IOException in case of invalid file.

        :param path: The path of the file.
        :param encoding: The file's encoding.
        """
        self.evaluate(codecs.open(path, encoding=encoding).read())

    def exists(self, selector):
        """Checks if element exists for given selector.

        :param string: The element selector.
        """
        return not self.currentFrame().findFirstElement(selector).isNull()
    
    
    @can_load_page
    def fill(self, selector, values):
        """Fills a form with provided values.

        :param selector: A CSS selector to the target form to fill.
        :param values: A dict containing the values.
        """
        if not self.exists(selector):
            raise Exception("Can't find form")
        
        for field in values:
            self.set_field_value("%s [name=%s]" % (selector, field),
                values[field])
        return True

    @client_utils_required
    @can_load_page
    def fire_on(self, selector, method):
        """Call method on element matching given selector.

        :param selector: A CSS selector to the target element.
        :param method: The name of the method to fire.
        :param expect_loading: Specifies if a page loading is expected.
        """
        return self.evaluate('GhostUtils.fireOn("%s", "%s");' % (
            selector, method))

    def global_exists(self, global_name):
        """Checks if javascript global exists.

        :param global_name: The name of the global.
        """
        return self.evaluate('!(typeof %s === "undefined");' %
            global_name)
    
    def _reset_for_loading(self):
        """Prepare GhostWebPage to load a new url into
        the Main Frame
        """
        self.http_resources = []
        self.http_resource_page = None
        self.loaded = False
        
    def open(self, address, method='get', headers={}, auth=None,
            wait_onload_event=True, wait_for_loading=True):
        """Opens a web page.

        :param address: The resource URL.
        :param method: The Http method.
        :param headers: An optional dict of extra request hearders.
        :param auth: An optional tupple of HTTP auth (username, password).
        :param wait_onload_event: If it's set to True waits until the OnLoad event from
            the main page is fired. Otherwise wait until the Dom is ready.
        :param wait_for_loading: If True waits until the page is Loaded. Note that wait_onload_event
            isn't valid if wait_for_loading is False.
        :return: Page resource, All loaded resources.
        """
        if not wait_onload_event:
            if self.ghostInit.receivers(SIGNAL("dom_is_ready(bool)")) == 0:
                self.ghostInit.dom_is_ready.connect(self._page_loaded)
            Logger.log("Waiting until OnReady event is fired")
        else:
            if self.ghostInit.receivers(SIGNAL("dom_is_ready(bool)")) > 0:
                self.ghostInit.dom_is_ready.disconnect(self._page_loaded)
            #Logger.log("Waiting until OnLoad event is fired")
        
        body = QByteArray()
        
        try:
            method = getattr(QNetworkAccessManager,
                "%sOperation" % method.capitalize())
        except AttributeError:
            raise Exception("Invalid http method %s" % method)
        request = QNetworkRequest(QUrl(address))
        request.CacheLoadControl(QNetworkRequest.AlwaysNetwork)
        for header in headers:
            request.setRawHeader(header, headers[header])
        
        if auth is not None:
            self.network_manager.setAuthCredentials(auth[0], auth[1])
        self._reset_for_loading()
        self.main_frame.load(request, method, body)
        
        if not wait_for_loading:
            return self.get_loaded_page()
        return self.wait_for_page_loaded()
    
    
    def download(self, path, address, **kwards):
        page = self.open(address, **kwards)
        
        with open(path, "wb") as f:
            f.write(page.content)
        
        return page
    
    
    @can_load_page
    @client_utils_required
    def set_field_value(self, selector, value, blur=True):
        """Sets the value of the field matched by given selector.

        :param selector: A CSS selector that target the field.
        :param value: The value to fill in.
        :param blur: An optional boolean that force blur when filled in.
        """
        def _set_text_value(selector, value):
            return self.evaluate(
                'document.querySelector("%s").value=%s;' %
                    (selector, json.dumps(value)))

        res, resources = None, []

        element = self.main_frame.findFirstElement(selector)
        if element.isNull():
            raise Exception('can\'t find element for %s"' % selector)
        self.fire_on(selector, 'focus')
        if element.tagName() in ["TEXTAREA", "SELECT"]:
            res = _set_text_value(selector, value)
        elif element.tagName() == "INPUT":
            if element.attribute('type') in ["color", "date", "datetime",
                "datetime-local", "email", "hidden", "month", "number",
                "password", "range", "search", "tel", "text", "time",
                "url", "week"]:
                res = _set_text_value(selector, value)
            elif element.attribute('type') == "checkbox":
                res = self.evaluate(
                    'GhostUtils.setCheckboxValue("%s", %s);' %
                        (selector, json.dumps(value)))
            elif element.attribute('type') == "radio":
                res = self.evaluate(
                    'GhostUtils.setRadioValue("%s", %s);' %
                        (selector, json.dumps(value)))
            elif element.attribute('type') == "file":
                self._upload_file = value
                res = self.click(selector)
                self._upload_file = None
        else:
            raise Exception('unsuported field tag')
        if blur:
            self.fire_on(selector, 'blur')
            
        return res

    def set_viewport_size(self, width, height):
        """Sets the page viewport size.

        :param width: An integer that sets width pixel count.
        :param height: An integer that sets height pixel count.
        """
        self.setViewportSize(QSize(width, height))
    
    def wait_for(self, condition, timeout_message):
        """Waits until condition is True.

        :param condition: A callable that returns the condition.
        :param timeout_message: The exception message on timeout.
        """
        started_at = time.time()
        while not condition():
            if time.time() > (started_at + self.wait_timeout):
                raise Exception(timeout_message)
            time.sleep(0.01)
            self._app.processEvents()
            if self.wait_callback is not None:
                self.wait_callback()

    def wait_for_alert(self):
        """Waits for main frame alert().
        """
        self.wait_for(lambda: self._alert is not None,
            'User has not been alerted.')
        msg = self._alert
        self._alert = None
        return msg

    def wait_for_page_loaded(self):
        """Waits until page is loaded, assumed that a page as been requested.
        """
        self.wait_for(lambda: self.loaded and len(self._unsupported_files.keys()) == 0,
            'Unable to load requested page')
        
        return self.get_loaded_page()
    
    def get_loaded_page(self):
        if self.loaded and len(self._unsupported_files.keys()) == 0:
            return self.http_resource_page            
            
        return None
    
    def wait_for_selector(self, selector):
        """Waits until selector match an element on the frame.

        :param selector: The selector to wait for.
        """
        self.wait_for(lambda: self.exists(selector),
            'Can\'t find element matching "%s"' % selector)
        return True

    def wait_for_text(self, text):
        """Waits until given text appear on main frame.

        :param text: The text to wait for.
        """
        self.wait_for(lambda: text in self.currentFrame().toPlainText(),
            'Can\'t find "%s" in current frame' % text)
        return True
    
    def _page_load_progress(self, progress):
        pass
        
    def _page_loaded(self, ok):
        """Called back when page is loaded.
        """
        # FIXME: Check why ok == False when we are trying to load
        # unsupported content
        self.loaded = True

    def _page_load_started(self):
        """Called back when page load started.
        """
        self.loaded = False

    def _release_last_resources(self):
        """Releases last loaded resources.

        :return: The released resources.
        """
        last_resources = self.http_resources
        self.http_resources = []
        return last_resources
    
    def release_last_resources(self):
        return self._release_last_resources()
    
    def _insert_dom_ready_code(self):
        self.mainFrame().addToJavaScriptWindowObject("GhostInit", self.ghostInit);
        #self.page.mainFrame().addToJavaScriptWindowObject("ghost_frame", self.page.mainFrame());
        self.evaluate_js_file(os.path.join(os.path.dirname(__file__), 'domready.js'))
    
    def _request_ended(self, reply):
        """Adds an HttpResource object to http_resources.

        :param reply: The QNetworkReply object.
        """
        if reply.url() == self.currentFrame().url():
            Logger.log("Injecting DOMReady code")
            self._insert_dom_ready_code()
        
        content = None
        if unicode(reply.url()) in self._unsupported_files:
            del self._unsupported_files[unicode(reply.url())]
            content = reply.readAll()
        
        if reply.attribute(QNetworkRequest.HttpStatusCodeAttribute):
            cache = self.network_manager.cache()
            http_resource = HttpResource(reply, cache, content)
            
            if self.http_resource_page is None:
                self.http_resource_page = http_resource
            
            if self.max_resource_queued is None or self.max_resource_queued > 0:
                self.http_resources.append(http_resource)
            
            
            if self.max_resource_queued is not None and \
                len(self.http_resources) > self.max_resource_queued:
                self.http_resources.pop(0)
                #self._del_resources()
            
            
    def _unsupported_content(self, reply):
        """Adds an HttpResource object to http_resources with unsupported
        content.

        :param reply: The QNetworkReply object.
        """
        self._unsupported_files[unicode(reply.url())] = reply
    
    
    def switch_to_frame(self, frameName=None):
        """Change the focus to the indicated frame

        :param frameName: The name of the frame
        """
        if frameName is None:
            self.main_frame.setFocus()
            return True
        
        for frame in self.currentFrame().childFrames():
            if frame.frameName() == frameName:
                frame.setFocus()
                return True
        return False
    
    def switch_to_frame_nro(self, nro=-1):
        """Change the focus to the indicated frame

        :param nro: Number of the frame
        """
        if nro == -1:
            self.main_frame.setFocus()
        
        frames = self.currentFrame().childFrames()
        if len(frames) <= (nro + 1):
            frames[nro].setFocus()
        
        return nro is None or len(frames) < nro
    
    @property
    def cookies(self):
        """Returns all cookies."""
        return self.network_manager.cookieJar().allCookies()

    def delete_cookies(self):
        """Deletes all cookies."""
        self.network_manager.cookieJar().setAllCookies([])
    
    def delete_cache(self):
        self.network_manager.cache().clear()
        
    def load_cookies( self, cookie_storage, keep_old=False ):
        """load from cookielib's CookieJar or Set-Cookie3 format text file.

        :param cookie_storage: file location string on disk or CookieJar instance.
        :param keep_old: Don't reset, keep cookies not overriden.
        """
        def toQtCookieJar(pyCookieJar, qtCookieJar):
            all_cookies = qtCookieJar.cookies if keep_old else []
            for pc in pyCookieJar:
                qc = toQtCookie(pc)
                all_cookies.append(qc)
            qtCookieJar.setAllCookies(all_cookies)

        def toQtCookie(pyCookie):
            qc = QNetworkCookie(pyCookie.name, pyCookie.value)
            qc.setSecure(pyCookie.secure)
            if pyCookie.path_specified:
                qc.setPath(pyCookie.path)
            if pyCookie.domain != "" :
                qc.setDomain(pyCookie.domain)
            if pyCookie.expires != 0:
                t = QDateTime()
                t.setTime_t(pyCookie.expires)
                qc.setExpirationDate(t)
            # not yet handled(maybe less useful):
            #   py cookie.rest / QNetworkCookie.setHttpOnly()
            return qc

        if cookie_storage.__class__.__name__ == 'str':
            cj = LWPCookieJar(cookie_storage)
            cj.load()
            toQtCookieJar(cj, self.network_manager.cookieJar())
        elif cookie_storage.__class__.__name__.endswith('CookieJar') :
            toQtCookieJar(cookie_storage, self.network_manager.cookieJar())
        else:
            raise ValueError, 'unsupported cookie_storage type.'
        
    
    def save_cookies(self, cookie_storage):
        """Save to cookielib's CookieJar or Set-Cookie3 format text file.

        :param cookie_storage: file location string or CookieJar instance.
        """
        def toPyCookieJar(qtCookieJar, pyCookieJar):
            for c in qtCookieJar.allCookies():
                pyCookieJar.set_cookie(toPyCookie(c))

        def toPyCookie(qtCookie):
            port = None
            port_specified = False
            secure = qtCookie.isSecure()
            name = str(qtCookie.name())
            value = str(qtCookie.value())
            v = str(qtCookie.path())
            path_specified = bool( v != "" )
            path = v if path_specified else None
            v = str(qtCookie.domain())
            domain_specified = bool( v != "" )
            domain = v
            domain_initial_dot = v.startswith('.') if domain_specified else None
            v = long(qtCookie.expirationDate().toTime_t())
            # Long type boundary on 32bit platfroms; avoid ValueError
            expires = 2147483647 if v > 2147483647 else v
            rest = {}
            discard = False
            return Cookie(0, name, value, port, port_specified, domain,
                domain_specified, domain_initial_dot, path, path_specified,
                secure, expires, discard, None, None, rest)

        if cookie_storage.__class__.__name__ == 'str':
            cj = LWPCookieJar(cookie_storage)
            toPyCookieJar(self.network_manager.cookieJar(), cj)
            cj.save()
        elif cookie_storage.__class__.__name__.endswith('CookieJar') :
            toPyCookieJar(self.network_manager.cookieJar(), cookie_storage)
        else:
            raise ValueError, 'unsupported cookie_storage type.'
        
class HttpResource(object):
    """Represents an HTTP resource.
    """
    def __init__(self, reply, cache, content=None):
        self.url = reply.url().toString()
        self.content = content
        # TODO: in some request reply.attribute(QNetworkRequest.SourceIsFromCacheAttribute)
        # returns None. I'm not sure why that is happening.
        is_from_cache = reply.attribute(QNetworkRequest.SourceIsFromCacheAttribute)
        self.is_from_cache = False if is_from_cache is None else is_from_cache
        if self.content is None:
            # Tries to get back content from cache
            buffer = cache.data(QUrl(self.url))
            if buffer is not None:
                content = buffer.readAll()
                try:
                    self.content = unicode(content)
                except UnicodeDecodeError:
                    self.content = content
                
        self.http_status = reply.attribute(
            QNetworkRequest.HttpStatusCodeAttribute)
        Logger.log("Resource loaded: %s %s" % (self.url, self.http_status))
        self.headers = {}
        for header in reply.rawHeaderList():
            self.headers[unicode(header)] = unicode(reply.rawHeader(header))
        self._reply = reply


class GhostInit(QtCore.QObject):  
    """This class inject the DomReady Script in order to
        detect when the DOM is Ready
    """
    dom_is_ready = pyqtSignal(bool)
    
    @pyqtSlot()  
    def is_ready(self):
        Logger.log("Firing Dom Ready Signal")
        self.dom_is_ready.emit(True)
        
        
class Ghost(object):
    """Ghost manages multiple QWebPage's.

    :param user_agent: The default User-Agent header.
    :param wait_timeout: Maximum step duration in second.
    :param wait_callback: An optional callable that is periodically
        executed until Ghost stops waiting.
    :param log_level: The optional logging level.
    :param display: A boolean that tells ghost to displays UI.
    :param viewport_size: A tupple that sets initial viewport size.
    :param cache_dir: a directory where Ghost is going to put the cache
    :param cache_size: the Size of the cache in MB. If it's 0 the
        cache it's automatically disabled. 
    :param share_cookies: A boolean that indicates if every page created has
        to share the same cookie jar. If False every page will have a different
        cookie jar 
    :param share_cache: A boolean that indicates if every page created has
        to share the same cache directory. If False, cache directory will be called
        cache_dir + randomint in order to separate the directories.
    :param plugin_path: Array with paths to plugin directories (default ['/usr/lib/mozilla/plugins'])
    :param qt_debug: Redirect QT Framework messages to python logging
    """
    _app = None
    
    def __init__(self, user_agent=default_user_agent, wait_timeout=20,
            wait_callback=None, log_level=logging.WARNING, display=False,
            viewport_size=(800, 600), cache_dir='/tmp/ghost.py', cache_size=10,
            plugin_path=['/usr/lib/mozilla/plugins',],
            share_cookies=True, share_cache=True, qt_debug=False):
        
        self.user_agent = user_agent
        self.wait_timeout = wait_timeout
        self.wait_callback = wait_callback
        self.viewport_size = viewport_size
        self.log_level = log_level
        self.display = display
        self.share_cookies = share_cookies
        self.share_cache = share_cache
        self.cache_dir = cache_dir
        self.cache_size = cache_size
        self.network_managers = []
        self.current_page = None
        self._pages = []
        
        if not sys.platform.startswith('win') and not 'DISPLAY' in os.environ\
                and not hasattr(Ghost, 'xvfb'):
            try:
                os.environ['DISPLAY'] = ':99'
                Ghost.xvfb = subprocess.Popen(['Xvfb', ':99'])
            except OSError:
                raise Exception('Xvfb is required to a ghost run oustside ' +\
                    'an X instance')

        self.display = display
        if not Ghost._app:
            Ghost._app = QApplication.instance() or QApplication(['ghost'])
            qInstallMsgHandler(QTMessageProxy(qt_debug))
        for p in plugin_path:
            Ghost._app.addLibraryPath(p)
        QtWebKit.QWebSettings.setMaximumPagesInCache(0)
        QtWebKit.QWebSettings.setObjectCacheCapacities(0, 0, 0)
        
        logger.setLevel(log_level)

    def __del__(self):
        self.exit()
    
    def get_page(self, index):
        """Return the indicated GhostWebPage.
        :param index: Number of the GhostWebPage
        :return: Returns the page if the index exists, None otherwise 
        """
        page = None
        if index in range(len(self._pages)):
            page = self._pages[index]
        
        return page
        
    def switch_to_page(self, index):
        """Return the indicated page and change the focus.
        :param index: Number of the GhostWebPage
        :return: Returns a GhostWebPage if the index exists, None otherwise
        """
        page = self.get_page(index)
        self.current_page = page
        
        return page
    
    def remove_page(self, page):
        """Destoy the indicated GhostWebPage
        :param page: The GhostWebPage that we want to destroy
        """
        self._remove_page(page)
        
    @pyqtSlot(object)    
    def _remove_page(self, page):
        # TODO see what happends when the page has a dependency (popups)
        if not self.share_cookies:
            nm = page.networkAccessManager()
            
            if nm in self.network_managers:
                self.network_managers.remove(nm)
                del nm
            
        if page in self._pages:
            self._pages.remove(page)
            del page
        
    
    def create_page(self, wait_timeout=20, wait_callback=None, is_popup=False,
                    max_resource_queued=None, download_images=True,
                    prevent_download=[]):
        """Create a new GhostWebPage
        :param wait_timeout: The timeout used when we want to load a new url.
        :param wait_callback: An optional callable that is periodically
        executed until Ghost stops waiting.
        :param is_popup: Indicates if the QWebPage it's a popup
        :param max_resource_queued: Indicates witch it's the max number of
        resources that can be saved in memory. If None then no limits
        are applied. If 0 then no resources are kept. If the number
        it's > 0 then the number of resources won't be more than
        max_resource_queued
        :param download_images: Indicate if the browser download or not the images
        :param prevent_download: A List of extensions of the files that you want
        to prevent from downloading
        """
        cache_name = self.cache_dir if self.share_cache else self.cache_dir + str(random.randint(0, 100000000))
        network_manager = NetworkAccessManager(cache_dir=cache_name, cache_size=self.cache_size,
                    prevent_download=prevent_download)
        if not self.share_cookies or len(self.network_managers) == 0:
            cookie_jar = QNetworkCookieJar()
            network_manager.setCookieJar(cookie_jar)
            self.cookie_jar = cookie_jar
        else:
            network_manager.setCookieJar(self.cookie_jar)
        
        if self.share_cookies:
            self.cookie_jar.setParent(None)
        self.network_managers.append(network_manager)
        
        page = GhostWebPage(app=Ghost._app, network_manager=network_manager, wait_timeout=wait_timeout,
                wait_callback=wait_callback, viewport_size=self.viewport_size,
                user_agent=self.user_agent, log_level=self.log_level, create_page_callback=self.create_page,
                is_popup=is_popup, max_resource_queued=max_resource_queued,
                download_images=download_images)
        
        page.removeWindowFromList.connect(self._remove_page)
        
        self._pages.append(page)

        if self.display:
            self.webview = QtWebKit.QWebView()
            self.webview.setPage(page)
            self.webview.show()

        return page, (len(self._pages) - 1)
    
    def process_events(self):
        self._app.processEvents()
        
    def exit(self):
        """Exits application and relateds."""
        if self.display:
            self.webview.close()
        Ghost._app.quit()
        for n in self.network_managers:
            del n
        for page in self._pages:
            del page
        if self.share_cookies:
            del self.cookie_jar
            
        if hasattr(self, 'xvfb'):
            self.xvfb.terminate()

    def hide(self):
        """Close the webview."""
        try:
            self.webview.close()
        except:
            raise Exception("no webview to close")

    def show(self):
        """Show current page inside a QWebView.
        """
        self.webview = QtWebKit.QWebView()
        self.webview.setPage(self.page)
        self.webview.show()
