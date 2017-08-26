from __future__ import unicode_literals
from __future__ import print_function
import requests
from lxml import html
from lxml.etree import ParserError


def norm_url(url):
    if url.startswith("//"):
        url = "http:" + url

    return url


class LibGen(object):
    def __init__(self,
                 headers={},
                 libgen_url="http://libgen.io/scimag/ads.php",
                 xpath_pdf_url="/html/body/table/tr/td[3]/a"):

        self.s = requests.Session()
        self.libgen_url = libgen_url
        self.xpath_pdf_url = xpath_pdf_url
        self.headers = headers

        self.doi = None
        self.pdf_file = None
        self.pdf_url = None
        self.page_url = None
        self.html_tree = None
        self.html_content = None

    def download_pdf(self):
        r = self.s.get(
            self.pdf_url,
            headers=self.headers
        )
        print("r_pdf_url ", r.url)
        print(r.headers['content-type'])
        found = r.status_code == 200
        is_right_filetype = r.headers["content-type"] == "application/octet-stream"
        if found and is_right_filetype:
            pdf_file = open(self.pdf_file, "wb")
            pdf_file.write(r.content)
            pdf_file.close()
            print("Download ok")
        else:
            print("Fail in download ",
                  " status_code ",
                  r.status_code)
        return found,  r

    def navigate_to(self, doi, pdf_file):

        params = {"doi": doi, "downloadname": ""}
        r = self.s.get(
            self.libgen_url,
            params=params,
            headers=self.headers
        )
        self.page_url = r.url
        print("libgen link", self.page_url)
        found = r.status_code == 200
        if not found:
            print("Maybe libgen is down. Try to use sci-hub instead.")
            return found,  r

        self.html_content = r.content
        return found, r

    def generate_tree(self):

        try:
            self.html_tree = html.fromstring(self.html_content)
            success = True
        except ParserError:
            print("The LibGen page has a strange bewavior\n")
            print("Try open in browser to check\n")
            print(self.page_url)
            success = False

        return success, self.html_tree

    def get_pdf_url(self):
        html_a = self.html_tree.xpath(self.xpath_pdf_url)
        if len(html_a) == 0:
            print("PDF link for ", self.page_url, " not found")
            found = False
            self.pdf_url = None
        else:
            self.pdf_url = norm_url(html_a[0].attrib["href"])
            found = True

        return found, self.pdf_url
