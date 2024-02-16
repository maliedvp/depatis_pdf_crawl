import os
import numpy as np
import re
from get_pdfs import download_depatis_pdf
import multiprocessing as mp
from missing_pn import missing_pns

def generate_pn(pn):
    return 'DE' + str('000000000000' + str(pn))[-12:] + 'A'

def get_documents(pn):
    if not os.path.exists('downloads/'):
        os.makedirs('downloads/')

    if not str(pn + '_1') in [re.split(r'\.',f)[0] for f in os.listdir('downloads/')]:
    	download_depatis_pdf(patent_number=pn, page_num=1)
    elif not str(pn + '_2') in [re.split(r'\.',f)[0] for f in os.listdir('downloads/')]:
    	download_depatis_pdf(patent_number=pn, page_num=2)
    else:
    	print(f'Patent {pn}: Both files already exists')


def main():
    if missing_pns != []:
        pn_list = missing_pns
        print('Patent numbers from missing_pn are used')
    else:
        pn_list = [generate_pn(pn) for pn in range(1, 600000 + 1)]
        print('Automatic patent numbers in range are used')

    pn_split = np.array_split(
        pn_list,
        min(
            mp.cpu_count(),
            len(pn_list)
        )
    )
    pn_flat_list = [item for sublist in pn_split for item in sublist]

    with mp.Pool(mp.cpu_count()) as pool:
        pool.map(get_documents, pn_flat_list)

if __name__ == '__main__':
    main()
