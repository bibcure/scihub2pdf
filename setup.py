from setuptools import setup, find_packages

readme = open('README','r')
README_TEXT = readme.read()
readme.close()

setup(
    name="scihub2pdf",
    version="0.1.0",
    packages = find_packages(exclude=["build",]),
    # packages = find_packages(),
    scripts=["scihub2pdf/bin/scihub2pdf"],
    long_description = README_TEXT,
    install_requires = ["bibtexparser",
                        "title2bib",
                        "arxivcheck",
                        "future",
                        "Pillow",
                        "requests",
                        "lxml"],
    include_package_data=True,
    license="GPLv3",
    description="Downloads pdfs via a DOI number, article title or a bibtex file, sci-hub",
    author="Bruno Messias",
    author_email="messias.physics@gmail.com",
    download_url="https://github.com/bibcure/scihub2pdf/archive/0.1.0.tar.gz",
    keywords=["bibtex", "sci-hub", "libgen", "doi",  "science","scientific-journals"],

    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Topic :: Text Processing :: Markup :: LaTeX",
    ],
    url="https://github.com/bibcure/scihub2pdf"
)
