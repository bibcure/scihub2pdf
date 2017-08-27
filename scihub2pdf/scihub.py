from __future__ import unicode_literals, print_function, absolute_import

import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from PIL import Image
from scihub2pdf.tools import norm_url, download_pdf
from base64 import b64decode as b64d
from six import string_types
import sys
try:
    from StringIO import StringIO
    from io import BytesIO
except ImportError:
    from io import StringIO, BytesIO


class SciHub(object):
    def __init__(self,
                 headers,
                 xpath_captcha="//*[@id='captcha']",
                 xpath_pdf="//*[@id='pdf']",
                 xpath_input="/html/body/div/table/tbody/tr/td/form/input",
                 xpath_form="/html/body/div/table/tbody/tr/td/form",
                 domain_scihub="http://sci-hub.cc/",
                 ):

        self.xpath_captcha = xpath_captcha
        self.xpath_input = xpath_input
        self.xpath_form = xpath_form
        self.xpath_pdf = xpath_pdf
        self.domain_scihub = domain_scihub
        self.headers = headers
        self.driver = None
        self.sci_url = None
        self.el_captcha = None
        self.el_iframe = None
        self.el_form = None
        self.el_input_text = None
        self.has_captcha = False
        self.has_iframe = False
        self.pdf_url = None
        self.doi = None
        self.pdf_file = None
        self.s = None


    def start(self):
        try:
            self.driver = webdriver.PhantomJS()
        except WebDriverException:
            print("\n\t Install PhantomJS for download files in sci-hub.\n")
            print("\t OSX:")
            print("\t\t npm install -g phantomjs")
            print("\n\t Linux with npm:")
            print("\t\t sudo apt-get install npm\n")
            print("\t\t sudo npm install -g phantomjs\n")

            sys.exit(1)
