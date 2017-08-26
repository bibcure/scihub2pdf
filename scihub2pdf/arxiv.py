from __future__ import unicode_literals
from __future__ import print_function
import requests
from arxivcheck.arxiv import get_arxiv_pdf_link


class Arxiv(object):

    def __init__(self, headers={}):
        self.s = requests.Session()
        self.headers = headers
        self.pdf_file = None
        self.pdf_url = None

    def download_pdf(self):
        r = self.s.get(
            self.pdf_url,
            headers=self.headers
        )
        print("r_pdf_url ", r.url)
        print(r.headers['content-type'])
        found = r.status_code == 200
        is_pdf = r.headers["content-type"] == "application/pdf"
        if found and is_pdf:
            pdf_file = open(self.pdf_file, "wb")
            pdf_file.write(r.content)
            pdf_file.close()
            print("Download   ok")
        else:
            print("Fail in download ",
                  self.pdf_url,
                  " status_code ",
                  r.status_code)
        return found,  r

    def navigate_to(self, value, pdf_file, field="id"):
        self.pdf_file = pdf_file
        found, self.pdf_url = get_arxiv_pdf_link(value, field)
        if not found:
            print("Arxiv ", value, " not found\n")
            print(self.pdf_url)
        return found, self.pdf_url
