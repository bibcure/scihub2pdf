from __future__ import print_function
import requests
from lxml import html
from multiprocessing.dummy import Pool as ThreadPool
from pdb import set_trace
# pool = ThreadPool(3)


def get_libgen_url(bib):
    doi = bib["doi"]
    print(doi)
    url = "http://libgen.io/scimag/ads.php"
    params = {"doi": doi, "downloadname": ""}
    r = requests.get(url, params=params)
    html_tree = html.fromstring(r.content)
    print(r.status_code)
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

    pool = ThreadPool(5)
    # urls_libgen = [get_libgen_url(bib["doi"]) for bib in bibs_with_doi]
    urls_libgen = pool.map(get_libgen_url, bibs_with_doi)

    pool.close()
    pool.join()
    set_trace()
    # r_pdfs = pool.map(requests.get, urls_libgen)
    r_pdfs = list(map(requests.get, urls_libgen))
    # pool.close(),
    # pool.join()
    for i, r in enumerate(r_pdfs):

        bib = bibs_with_doi[i]
        pdf_name =  bib["ID"] if "ID" in bib else bib["doi"]
        pdf_name += ".pdf"
        pdf_file = location+pdf_name
        print(pdf_name)
        print(r.status_code)
        pdf_file = open(pdf_file, "wb")
        pdf_file.write(r.content)
        pdf_file.close()


def download_from_doi(doi, location=""):

    download_link = get_libgen_url(doi)
    pdf_name = "sci2pdf-{}.pdf".format(doi.replace("/", "_"))
    pdf_file = location+pdf_name
    download_pdf(download_link, pdf_file)
    return doi
