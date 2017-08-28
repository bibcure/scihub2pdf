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
            self.s = requests.Session()
            self.driver = webdriver.PhantomJS()
        except WebDriverException:
            print("\n\t Install PhantomJS for download files in sci-hub.\n")
            print("\t OSX:")
            print("\t\t npm install -g phantomjs")
            print("\n\t Linux with npm:")
            print("\t\t sudo apt-get install npm\n")
            print("\t\t sudo npm install -g phantomjs\n")

            sys.exit(1)

    def get_session(self):
        cookies = self.driver.get_cookies()
        for cookie in cookies:
            self.s.cookies.set(cookie['name'], cookie['value'])

        return self.s

    def download(self):
        found, r = download_pdf(
            self.s,
            self.pdf_file,
            self.pdf_url,
            self.headers)

        if not found:
            self.driver.save_screenshot(self.pdf_file+".png")

        return found,  r

    def navigate_to(self, doi, pdf_file):
        self.doi = doi
        self.pdf_file = pdf_file
        self.sci_url = self.domain_scihub+doi
        print("\n\tDOI: ", doi)
        print("\tSci-Hub Link: ", self.sci_url)
        r = requests.get(self.sci_url)
        found = r.status_code == 200
        if found:
            self.driver.get(self.sci_url)
            self.driver.set_window_size(1120, 550)
        else:
            print("\tSomething is wrong with sci-hub,")
            print("\tstatus_code: ", r.status_code)
        return found, r

    def get_captcha_img(self):
        self.driver.execute_script("document.getElementById('content').style.zIndex = 9999;")
        self.driver.switch_to.frame(self.el_iframe)
        self.driver.execute_script("document.getElementById('captcha').style.zIndex = 9999;")
        location = self.el_captcha.location
        size = self.el_captcha.size
        captcha_screenshot = self.driver.get_screenshot_as_base64()
        image_b64d = b64d(captcha_screenshot)
        if isinstance(image_b64d, string_types):
            image = Image.open(StringIO(image_b64d))
        else:
            image = Image.open(BytesIO(image_b64d))

        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        image = image.crop((left, top, right, bottom))
        self.driver.switch_to.default_content()
        return image


    def solve_captcha(self, captcha_text):

        # self.driver.save_screenshot(self.pdf_file+"before_solve.png")
        self.driver.switch_to.frame(self.el_iframe)
        self.el_input_text.send_keys(captcha_text)
        # self.driver.save_screenshot(self.pdf_file+"send_keys.png")
        self.el_form.submit()

        self.driver.switch_to.default_content()
        # with self.wait_for_page_load(timeout=10):
        found, r = self.navigate_to(self.doi, self.pdf_file)
        # self.driver.save_screenshot(self.pdf_file+"after_submit.png")
        return self.check_captcha()

    def get_iframe(self):
        self.has_iframe, self.el_iframe = self.get_el(self.xpath_pdf)
        if self.has_iframe:
            self.pdf_url = norm_url(self.el_iframe.get_attribute("src"))
        else:
            self.driver.save_screenshot(self.pdf_file+".png")

        return self.has_iframe

    def get_el(self, xpath):
        try:
            el = self.driver.find_element_by_xpath(
                xpath
            )
            found = True
        except NoSuchElementException:
            el = None
            found = False

        return found, el

    def check_captcha(self):
        print("\tchecking if has captcha...")
        has_iframe = self.get_iframe()
        if has_iframe is False:
            print("\tNo pdf found. Maybe, the sci-hub dosen't have the file")
            print("\tTry to open the link in your browser.")
            return False, has_iframe

        self.driver.save_screenshot(self.pdf_file+"check_captcha.png")
        self.driver.switch_to.frame(self.el_iframe)
        self.has_captcha, self.el_captcha = self.get_el(self.xpath_captcha)
        if self.has_captcha:
            found, self.el_input_text = self.get_el(self.xpath_input)
            found, self.el_form = self.get_el(self.xpath_form)

        self.driver.switch_to.default_content()

        return self.has_captcha, has_iframe
