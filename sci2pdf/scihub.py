from __future__ import print_function
import requests
from lxml import html
from multiprocessing.dummy import Pool as ThreadPool
from title2bib.crossref import get_bib_from_title
import bibtexparser
import pdb
# from PIL import Image
from builtins import input
# from StringIO import StringIO
# from builtins import input
# try:
    # from urllib import quote
# except ImportError:
    # from urllib.parse import quote


headers = {
    # "Connection": "close",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
}


def norm_url(url):
    if url.startswith("//"):
        url = "http:" + url

    return url


def get_libgen_url(bib, s):
    download_link = None
    doi = bib["doi"]
    print(doi)
    url = "http://libgen.io/scimag/ads.php"
    params = {"doi": doi, "downloadname": ""}

    r = s.get(url, params=params, headers=headers, allow_redirects=True)
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


def check_captcha(html_tree, url, s):
    html_captcha = html_tree.xpath("//*[@id='captcha']")
    if len(html_captcha) > 0:
        pdb.set_trace()
        captcha_url = url+html_captcha[0].attrib["src"]
        s.get(captcha_url)
        # Image.open(StringIO(r.content)).show()
        captcha_solution = input("Put the CAPTCHA: ")
        # submit_captcha(captcha_solution)
        return True
    else:

        return False


def get_scihub_url(bib, s):

    download_link = None
    doi = bib["doi"]
    # print(doi)
    url = "http://sci-hub.cc/"+bib["doi"]
    print("sci-hub link", url)
    r = s.get(url, headers=headers, allow_redirects=True)
    if r.status_code == 200:
        html_tree = html.fromstring(r.content)
        iframe_url = html_tree.xpath("//iframe/@src")[0]
        ri = s.get(iframe_url, headers=headers)
        html_tree_ri = html.fromstring(ri.content)
        if check_captcha(html_tree_ri, url, s) is False:
            # get_scihub_url(bib,)
            html_pdf = html_tree.xpath("//*[@id='pdf']")
            if len(html_pdf) > 0:
                download_link = norm_url(html_pdf[0].attrib["src"])
                print("sci-hub download", download_link)
            else:
                print("no pdf")
    else:
        print(r.status_code)

    bib["scihub"] = download_link
    return bib


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

    with requests.Session() as s:
        if thread_size == 1:
            bibs_scihub = list(map(
                lambda bib: get_scihub_url(bib, s),
                bibs_with_doi
            ))
        else:
            pool = ThreadPool(thread_size)
            bibs_scihub = pool.map(get_scihub_url, bibs_with_doi)
            pool.close()
            pool.join()

        bibs_scihub = list(filter(
            lambda bib: bib["scihub"] is not None, bibs_scihub
        ))
        bibs_scihub = list(map(put_pdf_location, bibs_scihub))

        if thread_size == 1:
            list(map(lambda bib: download_pdf(bib, s), bibs_scihub))
        else:
            pool = ThreadPool(thread_size)
            pool.map(download_pdf, bibs_scihub)
            bibs_scihub = pool.map(get_scihub_url, bibs_with_doi)
            pool.close()
            pool.join()


def download_from_doi(doi, location=""):
    bib = {"doi": doi}

    with requests.Session() as s:
        bib_scihub = get_scihub_url(bib, s)
        if bib_scihub["scihub"] is not None:
            pdf_name = "sci2pdf-{}.pdf".format(doi.replace("/", "_"))
            pdf_file = location+pdf_name
            bib_scihub["pdf_file"] = pdf_file
            download_pdf(bib, s)


def download_from_title(title, location=""):
    found, bib_string = get_bib_from_title(title)

    if found:
        bib = bibtexparser.loads(bib_string).entries[0]
        if "doi" in bib:

            with requests.Session() as s:
                bib_scihub = get_scihub_url(bib, s)
                if bib_scihub["scihub"] is not None:
                    pdf_name = "sci2pdf-{}.pdf".format(
                        bib["doi"].replace("/", "_")
                    )
                    pdf_file = location+pdf_name
                    bib_scihub["pdf_file"] = pdf_file
                    download_pdf(bib_scihub, s)
        else:
            print("Absent DOI")
