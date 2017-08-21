from __future__ import print_function
import requests
from lxml import html

from gevent import monkey, pool
import gevent
monkey.patch_all()

p = pool.Pool(3)

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

def download_pdf_from_bibs(bibs, location="sci2pdf/"):
    bibs_with_doi = list(filter(lambda bib: "doi" in bib, bibs))
    urls_libgen = [get_libgen_url(bib["doi"]) for bib in bibs_with_doi]
    r_pdfs = [
        p.spawn(requests.get, url)
        for url in urls_libgen
    ]
    gevent.joinall(r_pdfs)
    for i, r in enumerate(r_pdfs):

        bib = bibs_with_doi[i]
        pdf_name =  bib["ID"] if "ID" in bib else bib["doi"]
        pdf_name += ".pdf"
        pdf_file = location+pdf_name
        response = r.get()

        print(response.status_code)
        pdf_file = open(pdf_file, "wb")
        pdf_file.write(response.content)
        pdf_file.close()

def download_from_doi(doi, location=""):

    download_link = get_libgen_url(doi)
    pdf_name = "sci2pdf-{}.pdf".format(doi.replace("/", "_"))
    pdf_file = location+pdf_name
    download_pdf(download_link, pdf_file)
    return doi
