This repository 

1. downloads PDFs that correspond to the first and second pages of the original patent documents as provided by [Depatis]('https://depatisnet.dpma.de/DepatisNet/depatisnet?action=experte#Trefferlistenkonfiguration') [&rarr;](#downloading)
2. the code is parallelized for faster downloading

# downloading
the execution logic is to first navigate to the parent of the `depatis_pdf_crawl/` directory. Then execute

	python depatis_pdf_crawl -o /home/staff_homes/liebald/patents/downloads -w 64 -t /tmp  
    
All the downloaded files will be stored in the stated output folder `/home/staff_homes/liebald/patents/downloads`. The code is multiprocessd between 64 cores. Moreover, temporary files in the `/tmp` folder will be delted to not slow down the server. By default, the code downloads PDFs associated with the patent numbers stored in the list in the `missing_pn.py` file. If this list is empty, another list is generated (`pn_list = [generate_pn(pn) for pn in range(1, 100 + 1)]`) for which the range can be adjusted manually.
