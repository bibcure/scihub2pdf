from __future__ import print_function
import requests
from lxml import html


def get_libgen_url(doi):
    url = "http://libgen.io/scimag/ads.php"
    params = {"doi": doi, "downloadname": ""}
    page = requests.get(url, params=params)
    html_tree = html.fromstring(page.content)
    html_a = html_tree.xpath("/html/body/table/tr/td[3]/a")
    download_link = html_a[0].attrib["href"]
    return download_link


def download_pdf(url, pdf_file):
    request_pdf = requests.get(url)
    pdf_file = open(pdf_file, "wb")
    pdf_file.write(request_pdf.content)
    pdf_file.close()
    return request_pdf


def download_pdf_from_bib(bib, location="sci2pdf/"):
    if "doi" in bib:
        download_link = get_libgen_url(bib["doi"])
        pdf_name = bib["ID"] if "ID" in bib else bib["doi"]
        pdf_name += ".pdf"
        pdf_file = location+pdf_name
        print("Downloading "+bib["title"])
        download_pdf(download_link, pdf_file)

    return bib


def download_from_doi(doi, location=""):

    download_link = get_libgen_url(doi)
    pdf_name = "sci2pdf-{}.pdf".format(doi.replace("/", "_"))
    pdf_file = location+pdf_name
    download_pdf(download_link, pdf_file)
    return doi
