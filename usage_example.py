import os

import pylons

from nous.pylons.testing.browser import NousTestApp, NousTestBrowser
from nous.pylons.testing import LayerBase, GrokLayer, CompositeLayer, PylonsTestBrowserLayer

from my.model import meta


here_dir = os.path.dirname(os.path.abspath(__file__))
conf_dir = os.path.dirname(os.path.dirname(os.path.dirname(here_dir)))


class YourBaseLayer(LayerBase):

    def tearDown(self):
        pass

    def testSetUp(self):
        pass

    def testTearDown(self):
        pass


YourLayer = CompositeLayer(GrokLayer,
                            PylonsTestBrowserLayer('test.ini', conf_dir, meta),
                            YourBaseLayer(),
                            name='YourLayer')


YourErrorsLayer = CompositeLayer(GrokLayer,
                                  PylonsTestBrowserLayer('errors.ini', conf_dir, meta),
                                  YourBaseLayer(),
                                  name='YourErrorsLayer')


class YourTestBrowser(NousTestBrowser):

    @classmethod
    def logIn(cls, email='admin@example.com', password='asdasd'):
        browser = cls()
        form = browser.getForm('loginForm')
        form.getControl('Email').value = email
        form.getControl('Password').value = password
        form.getControl('Login').click()
        return browser


def setUp(test):
    test.globs['app'] = NousTestApp(pylons.test.pylonsapp)
    test.globs['Browser'] = YourTestBrowser


def tearDown(test):
    del test.globs['app']
    del test.globs['Browser']
