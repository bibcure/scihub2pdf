# SciHub to PDF(Beta)


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
$ scihub2pdf --title An useful paper
```

Arxiv...
```
$ scihub2pdf arxiv:0901.2686
$ scihub2pdf --title arxiv:Periodic table for topological insulators
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

## Using bibcure modules

Given a text file like
```
10.1063/1.3149495
10.7717/peerj.3714
.....
```
download all pdf's
```
$ doi2bib -i input_dois.txt > refs.bib
$ scihub2pdf -i refs.bib
```
