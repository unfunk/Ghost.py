#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest
import logging

from ghost import GhostTestCase, Ghost
from app import app
from wsgi_proxy import start_proxy_app

PORT = 5000
PORT_PROXY = 5001
base_url = 'http://localhost:%s/' % PORT


class GhostTest(GhostTestCase):
    port = PORT
    display = False
    log_level = logging.INFO
    test_path = os.path.dirname(__file__)
    
    
    @classmethod
    def tearDownClass(cls):
        super(GhostTest, cls).tearDownClass()
        
        filesToDelete = ["pdf_test_file.pdf"]
        for f in filesToDelete:
            p = os.path.join(cls.test_path, f)
            if os.path.exists(p):
                os.remove(p)
    
    
    @classmethod
    def create_app(cls):
        return app
    
    @classmethod
    def create_proxy_server(self):
        return start_proxy_app
        
    def test_open(self):
        page = self.page.open(base_url)
        self.assertEqual(page.url, base_url)
        self.assertTrue("Test page" in self.page.get_current_frame_content())
    
    def test_http_status(self):
        page = self.page.open("%sprotected" % base_url)
        self.assertEqual(page.http_status, 403)
        page = self.page.open("%s404" % base_url)
        self.assertEqual(page.http_status, 404)

    def test_evaluate(self):
        self.page.open(base_url)
        self.assertEqual(self.page.evaluate("x='ghost'; x;"), 'ghost')
    
    def test_external_api(self):
        page = self.page.open("%smootools" % base_url)
        resources = self.page.release_last_resources()
        self.assertEqual(len(resources), 2)
        self.assertEqual(type(self.page.evaluate("document.id('list')")),
            dict)
    
    def test_extra_resource_content(self):
        page = self.page.open("%smootools" % base_url)
        resources = self.page.release_last_resources()
        self.assertIn('MooTools: the javascript framework',
            resources[1].content)

    def test_extra_resource_binaries(self):
        page = self.page.open("%simage" % base_url)
        resources = self.page.release_last_resources()
        self.assertEqual(resources[1].content.__class__.__name__,
            'QByteArray')

    def test_wait_for_selector(self):
        page = self.page.open("%smootools" % base_url)
        resources = self.page.release_last_resources()
        success = self.page.click("#button")
        
        success = self.page\
            .wait_for_selector("#list li:nth-child(2)")
        resources = self.page.release_last_resources()
        self.assertEqual(resources[-1].url, "%sitems.json" % base_url)
    
    def test_wait_for_text(self):
        page = self.page.open("%smootools" % base_url)
        
        self.page.click("#button")
        success = self.page.wait_for_text("second item")
        resources = self.page.release_last_resources()
        
        self.assertEqual(resources[-1].url, "%sitems.json" % base_url)
    
    """
    def test_wait_for_timeout(self):
        self.page.open("%s" % base_url)
        self.assertRaises(Exception, self.page.wait_for_text, "undefined")
    """
    
    def test_fill(self):
        self.page.open("%sform" % base_url)
        values = {
            'text': 'Here is a sample text.',
            'email': 'my@awesome.email',
            'textarea': 'Here is a sample text.\nWith several lines.',
            'checkbox': True,
            "radio": "first choice"
        }
        self.page.fill('#contact-form', values)
        for field in ['text', 'email', 'textarea']:
            value = self.page\
                .evaluate('document.getElementById("%s").value' % field)
            self.assertEqual(value, values[field])
        value = self.page.evaluate(
            'document.getElementById("checkbox").checked')
        self.assertEqual(value, True)
        value = self.page.evaluate(
            'document.getElementById("radio-first").checked')
        self.assertEqual(value, True)
        value = self.page.evaluate(
            'document.getElementById("radio-second").checked')
        self.assertEqual(value, False)
    
    def test_form_submission(self):
        self.page.open("%sform" % base_url)
        values = {
            'text': 'Here is a sample text.',
        }
        self.page.fill('#contact-form', values)
        page = self.page.fire_on('#contact-form', 'submit',
            expect_loading=True)
        self.assertIn('form successfully posted', self.page.get_current_frame_content())

    def test_global_exists(self):
        self.page.open("%s" % base_url)
        self.assertTrue(self.page.global_exists('myGlobal'))

    def test_resource_headers(self):
        page = self.page.open(base_url)
        self.assertEqual(page.headers['Content-Type'], 'text/html; charset=utf-8')

    def test_click_link(self):
        page = self.page.open("%s" % base_url)
        page = self.page.click('a', expect_loading=True)
        self.assertEqual(page.url, "%sform" % base_url)

    def test_cookies(self):
        self.page.open("%scookie" % base_url)
        self.assertEqual(len(self.page.cookies), 1)
    
    def test_delete_cookies(self):
        self.page.open("%scookie" % base_url)
        self.page.delete_cookies()
        self.assertEqual(len(self.page.cookies), 0)
    
    def test_save_load_cookies(self):
        self.page.delete_cookies()
        self.page.open("%sset/cookie" % base_url)
        self.page.save_cookies('testcookie.txt')
        self.page.delete_cookies()
        self.page.load_cookies('testcookie.txt')
        self.page.open("%sget/cookie" % base_url)
        self.assertTrue('OK' in self.page.content)
        
    def test_wait_for_alert(self):
        self.page.open("%salert" % base_url)
        self.page.click('#alert-button')
        msg = self.page.wait_for_alert()
        self.assertEqual(msg, 'this is an alert')
    
    def test_confirm(self):
        self.page.open("%salert" % base_url)
        with self.page.confirm(True):
            self.page.click('#confirm-button')
        msg = self.page.wait_for_alert()
        self.assertEqual(msg, 'you confirmed!')
    
    def test_no_confirm(self):
        self.page.open("%salert" % base_url)
        with self.page.confirm(False):
            self.page.click('#confirm-button')
        msg = self.page.wait_for_alert()
        self.assertEqual(msg, 'you denied!')

    def test_confirm_callback(self):
        self.page.open("%salert" % base_url)
        with self.page.confirm(callback=lambda: False):
            self.page.click('#confirm-button')
        msg = self.page.wait_for_alert()
        self.assertEqual(msg, 'you denied!')

    
    def test_prompt(self):
        self.page.open("%salert" % base_url)
        with self.page.prompt('my value'):
            self.page.click('#prompt-button')
        value = self.page.evaluate('promptValue')
        self.assertEqual(value, 'my value')
    
    def test_prompt_callback(self):
        self.page.open("%salert" % base_url)
        with self.page.prompt(callback=lambda: 'another value'):
            self.page.click('#prompt-button')
        value = self.page.evaluate('promptValue')
        self.assertEqual(value, 'another value')
    
    def test_capture_to(self):
        self.page.open(base_url)
        self.page.capture_to('test.png')
        self.assertTrue(os.path.isfile('test.png'))
        os.remove('test.png')

    def test_region_for_selector(self):
        self.page.open(base_url)
        x1, y1, x2, y2 = self.page.region_for_selector('h1')
        self.assertEqual(x1, 8)
        self.assertEqual(y1, 21)
        self.assertEqual(x2, 791)

    def test_capture_selector_to(self):
        self.page.open(base_url)
        self.page.capture_to('test.png', selector='h1')
        self.assertTrue(os.path.isfile('test.png'))
        os.remove('test.png')

    def test_set_field_value(self):
        self.page.open("%sform" % base_url)
        values = {
            'text': "Here is a sample text with ' \" quotes.",
            'email': 'my@awesome.email',
            'textarea': 'Here is a sample text.\nWith several lines.',
            'checkbox': True,
            "multiple-checkbox": "second choice",
            "radio": "first choice"
        }
        for field in values:
            self.page.set_field_value('[name=%s]' % field, values[field])

        for field in ['text', 'email', 'textarea']:
            value = self.page\
                .evaluate('document.getElementById("%s").value' % field)
            self.assertEqual(value, values[field])

        value = self.page.evaluate(
            'document.getElementById("checkbox").checked')
        self.assertEqual(value, True)

        value = self.page.evaluate(
            'document.getElementById("multiple-checkbox-first").checked')
        self.assertEqual(value, False)
        value = self.page.evaluate(
            'document.getElementById("multiple-checkbox-second").checked')
        self.assertEqual(value, True)

        value = self.page.evaluate(
            'document.getElementById("radio-first").checked')
        self.assertEqual(value, True)
        value = self.page.evaluate(
            'document.getElementById("radio-second").checked')
        self.assertEqual(value, False)
    
    def test_set_simple_file_field(self):
        self.page.open("%supload" % base_url)
        self.page.set_field_value('[name=simple-file]',
            os.path.join(os.path.dirname(__file__), 'static', 'blackhat.jpg'))
        page = self.page.fire_on('form', 'submit',
            expect_loading=True)
        file_path = os.path.join(
            os.path.dirname(__file__), 'uploaded_blackhat.jpg')
        self.assertTrue(os.path.isfile(file_path))
        os.remove(file_path)

    def test_basic_http_auth_success(self):
        page = self.page.open("%sbasic-auth" % base_url,
            auth=('admin', 'secret'))
        self.assertEqual(page.http_status, 200)

    def test_basic_http_auth_error(self):
        page = self.page.open("%sbasic-auth" % base_url,
            auth=('admin', 'wrongsecret'))
        self.assertEqual(page.http_status, 401)

    def test_unsupported_content(self):
        page = self.page.open("%ssend-file" % base_url)
        resources = self.page.release_last_resources()
        with open(os.path.join(os.path.dirname(__file__), 'static',
            'foo.tar.gz'), 'r') as f:
            foo = f.read()
        self.assertEqual(resources[0].content, foo)
        self.assertEqual(len(resources), 1)
        
        
        page = self.page.open("%ssend_pdf" % base_url)
        resources = self.page.release_last_resources()
        with open(os.path.join(os.path.dirname(__file__), 'static',
            'martin_fierro.pdf'), 'r') as f:
            foo = f.read()
        self.assertEqual(resources[0].content, foo)
        self.assertEqual(len(resources), 1)
    
    def test_change_frame(self):
        page = self.page.open("%siframe" % base_url)
        self.page.switch_to_frame("frame2")
        self.assertEqual(str(self.page.evaluate("document.title")), "Title2")
        
        self.page.switch_to_frame()
        self.assertEqual(str(self.page.evaluate("document.title")), "Title1")

        self.page.switch_to_frame_nro(0)
        self.assertEqual(str(self.page.evaluate("document.title")), "Title2")
        
        self.page.switch_to_frame_nro()
        self.assertEqual(str(self.page.evaluate("document.title")), "Title1")
    
    def test_cache_enabled(self):
        page = self.page.open("%siframe" % base_url)
        resources = self.page.release_last_resources()

        r = [r for r in resources if "jquery.min.js" in r.url][0]
        self.assertTrue(not r.is_from_cache)
        
        page = self.page.open("%siframe" % base_url)
        resources = self.page.release_last_resources()
        r = [r for r in resources if "jquery.min.js" in r.url][0]
        self.assertTrue(r.is_from_cache)
    
    def test_windows_switch(self):
        page = self.page.open("%siframe" % base_url)
        self.assertEqual(self.page.evaluate("document.title"), "Title1")
        self.page.click("#newWindow")
        popup = self.ghost.get_page(1)
        popup.wait_for(lambda: popup.evaluate("document.title") == "Title2", 5000)
        popup.evaluate("window.close()")
        self.assertEqual(self.page.evaluate("document.title"), "Title1")
        self.assertTrue(self.ghost.get_page(1) is None)
        

    def test_prevent_download(self):
        page = self.ghost_prevent_download_page.open("%simage" % base_url)
        resources = self.ghost_prevent_download_page.release_last_resources()
        self.assertEqual(len(resources), 1)
        
        page = self.page.open("%simage" % base_url)
        resources = self.page.release_last_resources()
        self.assertEqual(len(resources), 2)
    
    def test_fire_on_loaded(self):
        page = self.page.open(
            "%slocal_resource" % base_url,
            wait_onload_event=True)
        resources = self.page.release_last_resources()
        self.assertEqual(len(resources), 2)
        
        page = self.page.open(
            "%slocal_resource" % base_url,
            wait_onload_event=False)
        resources = self.page.release_last_resources()
        self.assertEqual(len(resources), 1)
        
    
    def test_proxy_configuration(self):
        self.page.network_manager.configureProxy("127.0.0.1", 5001)
        page = self.page.open("%siframe" % base_url,
                auth=("1", "2"))
        self.assertNotEqual(self.page.evaluate("document.title"), "Title1")
        self.page.network_manager.removeProxy()
        
        self.page.network_manager.configureProxy("127.0.0.1", 5001)
        page = self.page.open("%siframe" % base_url,
                auth=("dummy", "dummy"))
        self.assertEqual(self.page.evaluate("document.title"), "Title1")
    
    def test_pdf_capture(self):
        p = os.path.join(self.test_path, "pdf_test_file.pdf")
        page = self.page.open("%siframe" % base_url)
        self.page.capture_to(p, format="pdf")
        self.assertTrue(os.path.exists(p))
    
    
    def test_max_resources(self):
        gpage, name = self.ghost.create_page(max_resource_queued=0)
        page = gpage.open("%simage" % base_url)
        self.ghost.remove_page(gpage)
        self.assertEqual(len(gpage.release_last_resources()), 0)
        self.assertEqual(page.url, "%simage" % base_url)
        
        gpage, name = self.ghost.create_page(max_resource_queued=0)
        page = gpage.open("%simage" % base_url)
        self.ghost.remove_page(gpage)
        self.assertEqual(len(gpage.release_last_resources()), 0)
        
        gpage, name = self.ghost.create_page(max_resource_queued=1)
        page = gpage.open("%simage" % base_url)
        self.ghost.remove_page(gpage)
        self.assertEqual(len(gpage.release_last_resources()), 1)
        
        gpage, name = self.ghost.create_page(max_resource_queued=10)
        page = gpage.open("%simage" % base_url)
        self.ghost.remove_page(gpage)
        self.assertEqual(len(gpage.release_last_resources()), 2)
    
if __name__ == '__main__':
    unittest.main()
