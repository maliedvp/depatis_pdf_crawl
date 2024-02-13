This repository 

1. downloads PDFs that correspond to the first and second pages of the original patent documents as provided by [Depatis]('https://depatisnet.dpma.de/DepatisNet/depatisnet?action=experte#Trefferlistenkonfiguration') [&rarr;](#downloading)
2. the code is parallelized for faster downloading

# downloading
the execution logic is to first navigate to the `depatis_pdf_crawl/` directory. There you have to specify the range of patent numbers for which PDFs should be downloaded in line 23 of `__main__.py` (`pn_list = [generate_pn(pn) for pn in range(1, 100 + 1)]`; in this specification, we download all files that are associated with the patent numbers 1 - 100). Then execute

	python __main__.py
    
All the downloaded files will be stored in the folder `downloads/`
