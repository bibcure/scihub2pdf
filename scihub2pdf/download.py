from __future__ import unicode_literals
from __future__ import print_function
import bibtexparser
# from . import __version__
# from lxml.etree import ParserError
import re
from title2bib.crossref import get_bib_from_title
from scihub import SciHub
from libgen import LibGen
from arxiv import Arxiv
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


# ScrapSci = SciHub(headers)
ScrapLib = LibGen(headers)
ScrapArx = Arxiv(headers)


def download_from_libgen(doi, pdf_file):
    found, r = ScrapLib.navigate_to(doi, pdf_file)
    if not found:
        print("something goes wrong..")
        return False, r

    success, tree = ScrapLib.generate_tree()
    if not success:
        return False, r

    found, url = ScrapLib.get_pdf_url()
    if not found:
        return False, r

    found, r = ScrapLib.download()

    return found, r


def download_from_arxiv(value, location, field="id"):

    pdf_file = location
    if not location.endswith(".pdf"):
        pdf_file = location+value+".pdf"

    found, pdf_url = ScrapArx.navigate_to(value, pdf_file, field)
    if found:
        found, r = ScrapArx.download()

    return found, pdf_url


def download_from_scihub(doi, pdf_file):
    found, r = ScrapSci.navigate_to(doi, pdf_file)
    if not found:
        print("something goes wrong..")
        print("\nurl")
        return False, r

    has_iframe = ScrapSci.get_iframe()
    if not has_iframe:
        return False, r
    has_captcha = ScrapSci.get_captcha()
    while has_captcha:
        ScrapSci.show_captcha()
        has_captcha = ScrapSci.get_captcha()

    found, r = ScrapSci.download()

    return found, r



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
                pdf_file = location+bib["journal"]+".pdf"
                download_from_arxiv(bib["journal"], pdf_file, "id")
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
        list(map(lambda bib: download_from_libgen(bib["doi"], bib["pdf_file"]), bibs_with_doi))
    else:
        for bib in bibs_with_doi:
            found, bib = download_from_scihub(bib["doi"], bib["pdf_file"])


def download_from_doi(doi, location="", use_libgen=False):
    pdf_name = "{}.pdf".format(doi.replace("/", "_"))
    pdf_file = location+pdf_name
    if use_libgen:
        download_from_libgen(doi, pdf_file)
    else:
        download_from_scihub(doi, pdf_file)


def download_from_title(title, location="", use_libgen=False):
    found, bib_string = get_bib_from_title(title)
    if found:
        bib = bibtexparser.loads(bib_string).entries[0]
        if "doi" in bib:
            pdf_name = "{}.pdf".format(
                bib["doi"].replace("/", "_")
            )
            bib["pdf_file"] = location+pdf_name
            if use_libgen:
                download_from_libgen(bib["doi"], bib["pdf_file"])
            else:
                found, bib = download_from_scihub(bib["doi"], bib["pdf_file"])
        else:
            print("Absent DOI")


