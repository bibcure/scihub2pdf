from setuptools import setup, find_packages

readme = open('README','r')
README_TEXT = readme.read()
readme.close()

setup(
    name="sci2pdf",
    version="0.0.1",
    packages = find_packages(exclude=["build",]),
    scripts=["sci2pdf/bin/sci2pdf"],
    long_description = README_TEXT,
    install_requires = ["bibtexparser",
                        "titletobib",
                        "future",
                        "requests",
                        "lxml"],
    include_package_data=True,
    license="GPLv3",
    description=" Helps you to have a better bibtex file",
    author="Bruno Messias",
    author_email="messias.physics@gmail.com",
    download_url="https://github.com/bibcure/sci2pdf/archive/0.0.1.tar.gz",
    keywords=["bibtex", "sci-hub", "libgen", "doi",  "science","scientific-journals"],

    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Topic :: Text Processing :: Markup :: LaTeX",
    ],
    url="https://github.com/bibcure/sci2pdf"
)
