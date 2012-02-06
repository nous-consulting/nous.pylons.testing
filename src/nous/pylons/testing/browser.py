import re
import urllib2
import sys
import webbrowser

from xml.etree.ElementTree import _escape_cdata
from lxml.html import fromstring
from lxml import etree

from webtest import TestApp
from wsgi_intercept.zope_testbrowser.wsgi_testbrowser import WSGI_Browser
from wsgiref.simple_server import make_server

import pylons.test


class NousTestApp(TestApp):

    request = None

    def do_request(self, req, status, expect_errors):
        self.request = req
        return super(NousTestApp, self).do_request(req, status, expect_errors)

    def serve(self):
        try:
            page_url = getattr(self.request, 'url', 'http://localhost/')
            # XXX we rely on browser being slower than our server
            webbrowser.open(addPortToURL(page_url, 5001))
            print >> sys.stderr, 'Starting HTTP server...'
            srv = make_server('localhost', 5001, pylons.test.pylonsapp)
            srv.serve_forever()
        except KeyboardInterrupt:
            print >> sys.stderr, 'Stopped HTTP server.'



def indent(elem, omit_attributes, omit_classes, include_classes, include_attributes, level=0):
    """Function that properly indents xml.

    Stolen from http://infix.se/2007/02/06/gentlemen-indent-your-xml
    """
    i = "\n" + level*"  "
    for attr_name in list(elem.keys()):
        if attr_name == 'class':
            classes = elem.attrib['class'].split()
            if include_classes:
                classes = [klass for klass in classes if klass in include_classes]
            elif omit_classes:
                classes = [klass for klass in classes if klass not in omit_classes]
            elem.attrib['class'] = ' '.join(classes)
        # if we got includes set, we ignore excludes
        if include_attributes:
            if attr_name not in include_attributes:
                del elem.attrib[attr_name]
        elif omit_attributes:
            if attr_name in omit_attributes:
                del elem.attrib[attr_name]
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, omit_attributes, omit_classes, include_classes, include_attributes, level+1)
            if not e.tail or not e.tail.strip():
                e.tail = i + "  "
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if elem.text:
            elem.text = elem.text.strip()
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def to_string(node, omit_attributes, omit_classes, include_classes, include_attributes):
    if isinstance(node, basestring):
        return _escape_cdata(node, 'ascii').rstrip()
    else:
        indent(node, omit_attributes, omit_classes, include_classes, include_attributes)
        return etree.tostring(node, pretty_print=True).rstrip()


def addPortToURL(url, port):
    """Add a port number to the url.

        >>> addPortToURL('http://localhost/foo/bar/baz.html', 3000)
        'http://localhost:3000/foo/bar/baz.html'
        >>> addPortToURL('http://foo.bar.com/index.html?param=some-value', 555)
        'http://foo.bar.com:555/index.html?param=some-value'

        >>> addPortToURL('http://localhost:666/index.html', 555)
        'http://localhost:555/index.html'

    """
    (scheme, netloc, url, query, fragment) = urllib2.urlparse.urlsplit(url)
    netloc = netloc.split(':')[0]
    netloc = "%s:%s" % (netloc, port)
    url = urllib2.urlparse.urlunsplit((scheme, netloc, url, query, fragment))
    return url


class NousTestBrowser(WSGI_Browser):

    def __init__(self, url='http://localhost/'):
        super(NousTestBrowser, self).__init__()
        self.handleErrors = False
        self.open(url)

    def serve(self):
        try:
            # XXX we rely on browser being slower than our server
            webbrowser.open(addPortToURL(self.url, 5001))
            print >> sys.stderr, 'Starting HTTP server...'
            srv = make_server('localhost', 5001, pylons.test.pylonsapp)
            srv.serve_forever()
        except KeyboardInterrupt:
            print >> sys.stderr, 'Stopped HTTP server.'

    def printContents(self):
        normal_body_regex = re.compile(r'[ \n\r\t]+')
        print normal_body_regex.sub(' ', self.contents)

    def queryHTML(self, query,
                  selector='xpath',
                  omit_attributes=['style', 'width', 'height'],
                  omit_classes=None,
                  include_classes=None,
                  include_attributes=None):
        doc = fromstring(self.contents)
        selector = getattr(doc, selector)
        result = [to_string(node,
                            omit_attributes,
                            omit_classes,
                            include_classes,
                            include_attributes).strip()
                  for node in selector(query)]
        return result

    def printQuery(self, query,
                   selector='xpath',
                   omit_attributes=['style', 'width', 'height'],
                   omit_classes=None,
                   include_classes=None,
                   include_attributes=None):
        # width, height, method, action, value, type, style
        # class, href, title, alt, id, src
        for item in self.queryHTML(query, selector, omit_attributes, omit_classes, include_classes, include_attributes):
            print item

