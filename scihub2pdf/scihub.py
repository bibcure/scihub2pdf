from __future__ import unicode_literals
from __future__ import print_function
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from builtins import input
from PIL import Image
from tools import norm_url, download_pdf
try:
    from StringIO import StringIO
    from io import BytesIO
except ImportError:
    from io import StringIO, BytesIO


url_captcha_scihub = "http://moscow.sci-hub.cc"
url_scihub = "http://sci-hub.cc/"
xpath_scihub_captcha = "//*[@id='captcha']"
xpath_scihub_pdf = "//*[@id='pdf']"
xpath_scihub_input = "/html/body/div/table/tbody/tr/td/form/input"
xpath_scihub_submit = "/html/body/div/table/tbody/tr/td/form/p[2]/input"


class SciHub(object):
    def __init__(self, headers):
        self.driver = None
        self.sci_url = None
        self.el_captcha = None
        self.el_iframe = None
        self.has_captcha = False
        self.has_iframe = False
        self.pdf_url = None
        self.doi = None
        self.pdf_file = None
        self.s = None
        self.headers = headers

    def start(self):
        self.driver = webdriver.PhantomJS()
        self.s = requests.Session()

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
            self.headers,
            filetype="application/octet-stream")

        if not found:
            self.driver.save_screenshot(self.pdf_file+".png")

        return found,  r

    def navigate_to(self, doi, pdf_file):
        self.doi = doi
        self.pdf_file = pdf_file
        self.sci_url = url_scihub+doi
        print("Sci-Hub LINK ->" + self.sci_url)
        r = requests.get(self.sci_url)
        found = r.status_code == 200
        if found:
            self.driver.get(self.sci_url)
            self.driver.set_window_size(1120, 550)
        return found, r

    def show_captcha(self):
        from base64 import b64decode as b64d
        self.driver.switch_to.frame(self.el_iframe)
        location = self.el_captcha.location
        size = self.el_captcha.size
        captcha_screenshot = self.driver.get_screenshot_as_base64()
        image = Image.open(StringIO(b64d(captcha_screenshot)))
        # self.driver.save_screenshot("~/teste/captcha.png")
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        image = image.crop((left, top, right, bottom))
        image.show()
        # image.save("~/teste/captcha.png", 'png')

        captcha_text = input("put captcha:")
        self.input_box.send_keys(captcha_text)
        self.submit_box.click()

        self.driver.save_screenshot('after.png')
        self.driver.switch_to.default_content()

    def get_iframe(self):
        self.has_iframe, self.el_iframe = self.get_el(xpath_scihub_pdf)
        if self.has_iframe:
            self.pdf_url = norm_url(self.el_iframe.get_attribute("src"))
        else:
            self.driver.save_screenshot(self.pdf_file+".png")
            print ('No iframe')

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

    def get_captcha(self):

        self.driver.switch_to.frame(self.el_iframe)
        self.has_captcha, self.el_captcha = self.get_el(xpath_scihub_captcha)
        if self.has_captcha:
            found, self.input_box = self.get_el(xpath_scihub_input)
            found, self.submit_box = self.get_el(xpath_scihub_submit)
        else:
            print ('No captcha')

        self.driver.switch_to.default_content()

        return self.has_captcha
