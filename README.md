# SciHub to PDF

## Description
sci2pdf is a module of [bibcure](https://github.com/bibcure/bibcure)

Downloads pdfs via a DOI number, article title or a bibtex file, using the
database of libgen(sci-hub).
## Install

```
$ sudo pip install sci2pdf
```

## Features and how to use

Given a bibtex file
```
$ sci2pdf -i input.bib 
```

Given a DOI number...
```
$ sci2pdf 10.1038/s41524-017-0032-0
```

Given a title...
```
$ sci2bib --title An useful paper
```

