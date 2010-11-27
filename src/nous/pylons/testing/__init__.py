import wsgi_intercept
from routes.util import URLGenerator

import pylons
from pylons import url
from pylons.i18n.translation import _get_translator

from wsgi_intercept.urllib2_intercept import uninstall_opener
from wsgi_intercept.urllib2_intercept import install_opener
from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand

environ = {}


class LayerBase(object):

    def __init__(self):
        self.__name__ = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        self.__bases__ = []


class CompositeLayer(object):

    __name__ = 'Layer'

    def __init__(self, *bases, **kwargs):
        name = kwargs.get('name', None)
        if name is None:
            name = '[%s]' % (
                '/'.join('%s.%s' % (x.__module__, x.__name__) for x in bases))
        self.__bases__ = bases
        self.__name__ = name


class WsgiInterceptLayer(object):

    def setUp(self):
        def create_fn():
            return pylons.test.pylonsapp
        install_opener()
        wsgi_intercept.add_wsgi_intercept('localhost', 80, create_fn)

    def tearDown(self):
        wsgi_intercept.remove_wsgi_intercept()
        uninstall_opener()


class PylonsBaseLayer(object):

    def __init__(self, config_file, conf_dir, meta):
        self.config = config_file
        self.conf_dir = conf_dir
        self.meta = meta
        self.__name__ = '%s(%s)' % (self.__class__.__name__, self.config)
        self.__bases__ = []

    def setUp(self):
        SetupCommand('setup-app').run([self.conf_dir + '/%s' % self.config])
        pylons.test.pylonsapp = loadapp('config:%s' % self.config,
                                        relative_to=self.conf_dir)

    def tearDown(self):
        from sqlalchemy.schema import MetaData
        self.meta.metadata = MetaData()
        from sqlalchemy.orm import clear_mappers
        clear_mappers()
        pylons.test.pylonsapp = None

    def testSetUp(self):
        config = pylons.test.pylonsapp.config
        translator = _get_translator(config.get('lang'), pylons_config=config)
        pylons.translator._push_object(translator)
        url._push_object(URLGenerator(pylons.test.pylonsapp.config['routes.map'], environ))

    def testTearDown(self):
        url._pop_object()
        pylons.translator._pop_object()


class PylonsTestBrowserLayer(PylonsBaseLayer, WsgiInterceptLayer):

    def setUp(self):
        PylonsBaseLayer.setUp(self)
        WsgiInterceptLayer.setUp(self)

    def tearDown(self):
        PylonsBaseLayer.tearDown(self)
        WsgiInterceptLayer.tearDown(self)
