import os
import numpy as np
import re
import multiprocessing as mp
import pathlib
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import shutil
from bs4 import BeautifulSoup
import time
from datetime import datetime

from missing_pn import missing_pns


class Download_pdf_depatis():
    def __init__(self, output_directory, workers_max, temp_directory):
        self.output_directory = pathlib.Path(output_directory)
        self.temp_directory = pathlib.Path(temp_directory)
        self.workers_max = workers_max
        


    def generate_pn(self, pn):
        return 'DE' + str('000000000000' + str(pn))[-12:] + 'A'



    def get_documents(self, pn):
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        if not str(pn + '_1') in [re.split(r'\.',f)[0] for f in os.listdir(self.output_directory)]:
            self.download_depatis_pdf(patent_number=pn, page_num=1)
            self.clean_temp_folder()
        elif not str(pn + '_2') in [re.split(r'\.',f)[0] for f in os.listdir(self.output_directory)]:
            self.download_depatis_pdf(patent_number=pn, page_num=2)
            self.clean_temp_folder()
        else:
            print(f'Patent {pn}: Both files already exists')


    def clean_temp_folder(self):
        for target_path in [f for f in os.listdir(self.temp_directory) if re.search(r'chromium|google' ,f)!=None]:
            try:
                path_to_checked = self.temp_directory / target_path
                creation_time = datetime.fromtimestamp(path_to_checked.stat().st_ctime)
                age_in_minutes = (datetime.now() - creation_time).total_seconds() / 60.0


                if age_in_minutes >= 4:
                    if path_to_checked.is_file():
                        try:
                            os.remove(path_to_checked)
                            print(f"File {path_to_checked} has been removed.")
                        except:
                            pass
                    elif path_to_checked.is_dir():
                        try:
                            shutil.rmtree(path_to_checked)
                            print(f"Directory {path_to_checked} and all its contents have been removed.")
                        except:
                            pass
                    else:
                        print(f"The target {path_to_checked} does not exist.")
                else:
                    print(f"The target {path_to_checked} is too young to be deleted.")
            except:
                print(f"The target {path_to_checked} impossible to be deleted.")


    def download_depatis_pdf(self, patent_number, page_num):
        # specify download link
        link = f'https://depatisnet.dpma.de/DepatisNet/depatisnet?action=pdf&docid={patent_number}'
        
        # initialize and specify optinos
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        # chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080") # full screen

        # set additional preferences
        prefs = {
            "download.default_directory": str(self.output_directory),
            "download.prompt_for_download": False,  # Disable download prompt
            "plugins.always_open_pdf_externally": True  # Automatically download PDFs
        }
        chrome_options.add_experimental_option("prefs", prefs)

        for _ in range(5):
            try:
                # open the browser
                driver = webdriver.Chrome(options=chrome_options)

                # Navigate to the webpage
                driver.get(link)

                # Find the iframe and switch to it
                iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "dpma-iframe-sa-full"))
                )
                driver.switch_to.frame(iframe)

                # Read the iframe's source code
                iframe_source_code = driver.page_source
                soup = BeautifulSoup(iframe_source_code, "html.parser")
                iframe = soup.find("iframe", id="dpma-sa-pdf-iframe")


                # navigate to the second page and read iframe source code again
                if iframe and iframe.has_attr("src"):

                    if page_num == 2: # extra round if second pdf shall be downloaded

                        button = driver.find_element(By.XPATH, '//a[@title="Nächste Seite des aktuellen Dokuments"]')
                        button.click()

                        driver.page_source

                        iframe = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "dpma-iframe-sa-full"))
                        )

                        driver.switch_to.frame(iframe)

                        iframe_source_code = driver.page_source
                        soup = BeautifulSoup(iframe_source_code, "html.parser")
                        iframe = soup.find("iframe", id="dpma-sa-pdf-iframe")

                    
                    pdf_viewer_link = iframe["src"]
                    driver.get(pdf_viewer_link)

                    time.sleep(3)
                    
                    # the download
                    try: 
                        # Wait for the download button to be clickable
                        download_button = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.ID, 'download'))
                        )

                        download_button.click()
                        print(f'Patent {patent_number} (Page {page_num}): Download has started')
                        # Wait for the download to complete
                        time.sleep(3)

                    except Exception as e:
                        print("Error waiting for download button:", e)

                else:
                    print(f'Patent {patent_number} (Page {page_num}): Server blocked access')

                driver.quit()
                break
                
            except:
                print(f'Patent {patent_number} (Page {page_num}): Server blocked access')



    def main(self):
        if missing_pns != []:
            pn_list = missing_pns
            print('Patent numbers from missing_pn are used')
        else:
            pn_list = [generate_pn(pn) for pn in range(1, 600000 + 1)]
            print('Automatic patent numbers in range are used')

        workers_number = min(
                self.workers_max,
                len(pn_list)
            )

        pn_split = np.array_split(
            pn_list,
            workers_number
        )
        pn_flat_list = [item for sublist in pn_split for item in sublist]

        with mp.Pool(workers_number) as pool:
            pool.map(self.get_documents, pn_flat_list)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o','--output_directory', help='Output Directory', required=True)
    parser.add_argument('-w','--workers_max', help='Maximum number of parallel processes', required=True)
    parser.add_argument('-t','--temp_directory', help='Directory where temp files are stored', required=True)
    args = parser.parse_args()

    Download_pdf_depatis(
        output_directory = args.output_directory,
        workers_max = int(args.workers_max),
        temp_directory = args.temp_directory
    ).main()
