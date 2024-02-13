from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
from bs4 import BeautifulSoup
import time
import pathlib

def download_depatis_pdf(patent_number, page_num):
    # specify download link
    link = f'https://depatisnet.dpma.de/DepatisNet/depatisnet?action=pdf&docid={patent_number}'
    
    # initialize and specify optinos
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    # chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080") # full screen

    # Specify the download directory here
    download_directory = os.path.join(os.getcwd(), 'downloads')

    # set additional preferences
    prefs = {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,  # Disable download prompt
        "plugins.always_open_pdf_externally": True  # Automatically download PDFs
    }
    chrome_options.add_experimental_option("prefs", prefs)

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

        time.sleep(2)
        
        # the download
        try: 
            # Wait for the download button to be clickable
            download_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, 'download'))
            )

            download_button.click()
            print(f'Patent {patent_number} (Page {page_num}): Download has started')
            # Wait for the download to complete
            time.sleep(2)

        except Exception as e:
            print("Error waiting for download button:", e)

    else:
        print(f'Patent {patent_number} (Page {page_num}): Server blocked access')

    driver.quit()

