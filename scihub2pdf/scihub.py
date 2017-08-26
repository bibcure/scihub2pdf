from __future__ import unicode_literals
from __future__ import print_function
import requests
from lxml import html
import bibtexparser
# from . import __version__
# from lxml.etree import ParserError
import re
from title2bib.crossref import get_bib_from_title
from arxivcheck.arxiv import get_arxiv_pdf_link
from phantom_scihub import norm_url, PhantomSciHub
import pdb
headers = {
"Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
}
# print("\n\t Checking state of scihub...")
# url_state = "https://raw.githubusercontent.com/bibcure/scihub_state/master/state.txt"
# try:
# r = requests.get(url_state, headers=headers)
# state_scihub = [i.split(">>")[1] for i in r.iter_lines()]
# url_captcha_scihub = state_scihub[0]
# url_libgen = state_scihub[1]
# url_scihub = state_scihub[2]
# xpath_libgen_a = state_scihub[3]
# xpath_scihub_captcha = state_scihub[4]
# xpath_scihub_iframe = state_scihub[5]
# xpath_scihub_pdf = state_scihub[6]
# has_update = state_scihub[7] != __version__
# if has_update:
# print("\n\t\tWill be better if you upgrade scihub2pdf.")
# print("\t\tFor that, just do:\n")
# print("\t\t\t sudo pip install scihub2pdf --upgrade\n")
# except:
url_libgen = "http://libgen.io/scimag/ads.php"

url_captcha_scihub = "http://moscow.sci-hub.cc"
url_scihub = "http://sci-hub.cc/"
xpath_libgen_a = "/html/body/table/tr/td[3]/a"
xpath_scihub_captcha = "//*[@id='captcha']"
xpath_scihub_pdf = "//*[@id='pdf']"
xpath_scihub_input = "/html/body/div/table/tbody/tr/td/form/input"
xpath_scihub_submit = "/html/body/div/table/tbody/tr/td/form/p[2]/input"

# s = None


def download_from_libgen(bib, s):
    params = {"doi": bib["doi"], "downloadname": ""}
    r = s.get(url_libgen, params=params, headers=headers)
    print("libgen link", r.url)

    if r.status_code != 200:
        print("Fail libgen url", r.status_code)
        print("Maybe libgen is down. Try to use sci-hub instead.")
        return

    html_tree = html.fromstring(r.content)
    html_a = html_tree.xpath(xpath_libgen_a)
    if len(html_a) == 0:
        print("Copy and paste the below link into your browser")
        print("\n\t", r.url, "\n")
        return

    download_link = norm_url(html_a[0].attrib["href"])
    bib["pdf_link"] = download_link
    s = download_pdf(bib)

    return s


Scrapper = PhantomSciHub()


def download_from_scihub(bib):
    found, r = Scrapper.navigate_to(bib["doi"], bib["pdf_file"])
    if not found:
        print("something goes wrong..")
        print("\nurl")
        return False, r

    has_iframe = Scrapper.get_iframe()
    if not has_iframe:
        return False, r
    has_captcha = Scrapper.get_captcha()
    while has_captcha:
        Scrapper.show_captcha()
        has_captcha = Scrapper.get_captcha()

    found, r = Scrapper.download_pdf()

    return found, r


def download_pdf(bib, s):
    # global s
    r = s.get(bib["pdf_link"], headers=headers)
    print("r_pdf_link ", r.url)
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

    return r, bib, s


def download_pdf_from_bibs(bibs, location="",
                           use_libgen=False):
    def put_pdf_location(bib):
        pdf_name = bib["ID"] if "ID" in bib else bib["doi"].replace("/", "_")
        pdf_name += ".pdf"
        bib["pdf_file"] = location+pdf_name
        return bib

    # bibs_with_doi = list(filter(lambda bib: "doi" in bib, bibs))
    bibs_with_doi = []
    # bibs_arxiv = []
    for bib in bibs:
        if "journal" in bib:
            if bool(re.match("arxiv:", bib["journal"], re.I)):
                print("arxiv")
                download_from_arxiv(bib["journal"], "id", location)
            elif "doi" in bib:
                bibs_with_doi.append(bib)

        elif "doi" in bib:
            bibs_with_doi.append(bib)
            # bibs_journal = list(filter(lambda bib: "journal" in bib, bibs))
            # bibs_arxiv = list(
            # filter(
            # lambda bib: bool(re.match("arxiv:", bib["journal"], re.I)) in bib, bibs_journal
            # )
            # )

    bibs_with_doi = list(map(put_pdf_location, bibs_with_doi))
    # libgen has no  captcha, try to use multiprocessing?
    if use_libgen:
        with requests.Session() as s:
            list(map(lambda bib: download_from_libgen(bib, s), bibs_with_doi))
    else:
        for bib in bibs_with_doi:
            found, bib = download_from_scihub(bib)


def download_from_doi(doi, location="", use_libgen=False):
    bib = {"doi": doi}
    pdf_name = "{}.pdf".format(doi.replace("/", "_"))
    bib["pdf_file"] = location+pdf_name
    s = requests.Session()
    if use_libgen:
        download_from_libgen(bib, s)
    else:
        download_from_scihub(bib)


def download_from_title(title, location="", use_libgen=False):
    found, bib_string = get_bib_from_title(title)
    s = requests.Session()
    if found:
        bib = bibtexparser.loads(bib_string).entries[0]
        if "doi" in bib:
            pdf_name = "{}.pdf".format(
                bib["doi"].replace("/", "_")
            )
            bib["pdf_file"] = location+pdf_name
            if use_libgen:
                download_from_libgen(bib, s)
            else:
                found, bib = download_from_scihub(bib)
        else:
            print("Absent DOI")


def download_from_arxiv(value, field="id", location=""):
    print("Downloading...", value)
    found, pdf_link = get_arxiv_pdf_link(value, field)
    if found and pdf_link is not None:
        bib = {}
        pdf_name = "{}.pdf".format(value.replace("/", "_"))
        bib["pdf_file"] = location+pdf_name
        s = requests.Session()
        bib["pdf_link"] = pdf_link
        download_pdf(bib, s)
    else:
        print(value, ": Arxiv not found.")
