from __future__ import print_function
import requests
from lxml import html
from title2bib.crossref import get_bib_from_title
import bibtexparser
from builtins import input
from PIL import Image
from StringIO import StringIO


headers = {
    # "Connection": "close",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
}


url_captcha_scihub = "http://moscow.sci-hub.cc"
url_libgen = "http://libgen.io/scimag/ads.php"
url_scihub = "http://sci-hub.cc/"


def norm_url(url):
    if url.startswith("//"):
        url = "http:" + url

    return url


def get_libgen_url(bib, s):
    download_link = None
    doi = bib["doi"]
    print(doi)
    params = {"doi": doi, "downloadname": ""}

    r = s.get(url_libgen, params=params, headers=headers, allow_redirects=True)
    if r.status_code == 200:
        html_tree = html.fromstring(r.content)
        html_a = html_tree.xpath("/html/body/table/tr/td[3]/a")
        if len(html_a) > 0:
            download_link = norm_url(html_a[0].attrib["href"])
        else:
            print("Link not found")
    else:
        print(r.status_code)

    bib["scihub"] = download_link
    return bib


def check_captcha(iframe_url, url, html_tree, s):
    html_captcha = html_tree.xpath("//*[@id='captcha']")
    if len(html_captcha) > 0:
        captcha_url = url_captcha_scihub+html_captcha[0].attrib["src"]
        r = s.get(captcha_url)

        Image.open(StringIO(r.content)).show()
        captcha_solution = input("Put the CAPTCHA: ")
        r = s.post(iframe_url, data={
            "captcha_code": captcha_solution
        })
        return True
    else:

        return False


def download_from_scihub(bib, s):

    url = url_scihub+bib["doi"]
    print("sci-hub link", url)
    r = s.get(url, headers=headers, allow_redirects=True)

    if r.status_code != 200:
        print("Fail scihub url", r.status_code)
        return

    html_tree = html.fromstring(r.content)
    iframe_url = html_tree.xpath("//iframe/@src")

    if len(iframe_url) == 0:
        print("Iframe not found")
        return

    iframe_url = iframe_url[0]
    ri = s.get(iframe_url, headers=headers)
    html_tree_ri = html.fromstring(ri.content)

    if check_captcha(iframe_url, url,  html_tree_ri, s):
        return download_from_scihub(bib, s)

    html_pdf = html_tree.xpath("//*[@id='pdf']")

    if len(html_pdf) == 0:
        print("pdf file not found")
        return

    download_link = norm_url(html_pdf[0].attrib["src"])
    bib["scihub"] = download_link
    download_pdf(bib, s)
    return


def download_pdf(bib, s):
    r = s.get(bib["scihub"], headers=headers)
    if r.status_code == 200:
        pdf_file = open(bib["pdf_file"], "wb")
        pdf_file.write(r.content)
        pdf_file.close()
        print("Download of", bib["pdf_file"], " ok")
    else:
        print("Fail in download ",
              bib["pdf_file"],
              " status_code ",
              r.status_code)


def download_pdf_from_bibs(bibs, location="",
                           thread_size=1):
    def put_pdf_location(bib):
        pdf_name = bib["ID"] if "ID" in bib else bib["doi"].replace("/", "_")
        pdf_name += ".pdf"
        pdf_file = location+pdf_name

        bib["pdf_file"] = pdf_file
        return bib

    bibs_with_doi = list(filter(lambda bib: "doi" in bib, bibs))

    bibs = list(map(put_pdf_location, bibs_with_doi))

    with requests.Session() as s:
        list(map(lambda bib: download_from_scihub(bib, s), bibs))


def download_from_doi(doi, location=""):
    bib = {"doi": doi}
    pdf_name = "sci2pdf-{}.pdf".format(doi.replace("/", "_"))
    pdf_file = location+pdf_name
    bib["pdf_file"] = pdf_file

    with requests.Session() as s:
        download_from_scihub(bib, s)


def download_from_title(title, location=""):
    found, bib_string = get_bib_from_title(title)

    if found:
        bib = bibtexparser.loads(bib_string).entries[0]
        if "doi" in bib:
            pdf_name = "sci2pdf-{}.pdf".format(
                bib["doi"].replace("/", "_")
            )
            pdf_file = location+pdf_name
            bib["pdf_file"] = pdf_file
            with requests.Session() as s:
                download_from_scihub(bib, s)
        else:
            print("Absent DOI")
