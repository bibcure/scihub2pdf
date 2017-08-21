from __future__ import print_function
import requests
from lxml import html
from multiprocessing.dummy import Pool as ThreadPool


headers = {
    "Connection": "close",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
}


def get_libgen_url(bib):
    download_link = None
    doi = bib["doi"]
    print(doi)
    url = "http://libgen.io/scimag/ads.php"
    params = {"doi": doi, "downloadname": ""}
    with requests.Session() as r:
        r.keep_alive = False
        r = requests.get(url, params=params, headers=headers)
        if r.status_code == 200:
            html_tree = html.fromstring(r.content)
            html_a = html_tree.xpath("/html/body/table/tr/td[3]/a")
            if len(html_a) > 0:
                download_link = html_a[0].attrib["href"]
            else:
                print("Link not found")
        else:
            print(r.status_code)

    bib["libgen"] = download_link
    return bib


def download_pdf(bib):
    with requests.Session() as r:
        r.keep_alive = False
        r = requests.get(bib["libgen"], headers=headers)
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


def download_pdf_from_bibs(bibs, location="sci2pdf/",
                           thread_size_links=1, thread_size_download=1):
    def put_pdf_location(bib):
        pdf_name = bib["ID"] if "ID" in bib else bib["doi"].replace("/", "_")
        pdf_name += ".pdf"
        pdf_file = location+pdf_name

        bib["pdf_file"] = pdf_file
        return bib

    bibs_with_doi = list(filter(lambda bib: "doi" in bib, bibs))

    # bibs_libgen = list(map(get_libgen_url, bibs_with_doi))

    pool = ThreadPool(thread_size_links)
    bibs_libgen = pool.map(get_libgen_url, bibs_with_doi)
    pool.close()
    pool.join()

    bibs_libgen = list(filter(
        lambda bib: bib["libgen"] is not None, bibs_libgen
    ))
    bibs_libgen = list(map(put_pdf_location, bibs_libgen))

    pool = ThreadPool(thread_size_download)
    pool.map(download_pdf, bibs_libgen)

    pool.close()
    pool.join()


def download_from_doi(doi, location=""):
    bib = {"doi": doi}
    bib_libgen = get_libgen_url(bib)
    pdf_name = "sci2pdf-{}.pdf".format(doi.replace("/", "_"))
    pdf_file = location+pdf_name
    bib_libgen["pdf_file"] = pdf_file
    download_pdf(bib)


def download_from_title(doi, location=""):
    bib = {"doi": doi}
    bib_libgen = get_libgen_url(bib)
    pdf_name = "sci2pdf-{}.pdf".format(doi.replace("/", "_"))
    pdf_file = location+pdf_name
    bib_libgen["pdf_file"] = pdf_file
    download_pdf(bib)
