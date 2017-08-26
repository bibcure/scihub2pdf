from __future__ import unicode_literals
from __future__ import print_function


def download_pdf(s, pdf_file, pdf_url, headers, filetype="application/pdf"):
    r = s.get(
        pdf_url,
        headers=headers
    )
    found = r.status_code == 200
    is_right_type = r.headers["content-type"] == filetype
    if found and is_right_type:
        pdf = open(pdf_file, "wb")
        pdf.write(r.content)
        pdf.close()
        print("Download   ok")
    else:
        print("Fail in download ",
              " status_code ",
              r.status_code)
    return found,  r


def norm_url(url):
    if url.startswith("//"):
        url = "http:" + url

    return url


