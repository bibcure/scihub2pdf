# SciHub to PDF

## Description

scihub2pdf is a module of [bibcure](https://github.com/bibcure/bibcure)

Downloads pdfs via a DOI number, article title or a bibtex file, using the
database of libgen or Sci-Hub.

## Install

```
$ sudo pip install scihub2pdf
```

## Features and how to use

Given a bibtex file
```
$ scihub2pdf -i input.bib 
```

Given a DOI number...
```
$ scihub2pdf 10.1038/s41524-017-0032-0
```

Given a title...
```
$ sci2bib --title An useful paper
```
Location folder as argument
```
$ scihub2pdf -i input.bib -l somefoler/
```

Use libgen instead sci-hub

```
$ scihub2pdf -i input.bib --uselibgen
```

## Sci-hub:

- Stable
- Annoying CAPTCHA
- Fast


## Libgen

- Unstalbe
- No CAPTCHA
- Slow
