# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 13:01:02 2020

@author: OHyic
"""
#import selenium drivers
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#import helper libraries
import time
from urllib.parse import urlparse
import os
import requests
import io
from PIL import Image
import re

#custom patch libraries
import patch

class GoogleImageScraper():
    def __init__(self, image_path, webdriver_path=None, search_key="cat", number_of_images=1, headless=True, min_resolution=(0, 0), max_resolution=(1920, 1080), max_missed=10):
        # Check parameter types
        image_path = os.path.join(image_path, search_key)
        if (type(number_of_images)!=int):
            print("[Error] Number of images must be integer value.")
            return
        if not os.path.exists(image_path):
            print("[INFO] Image path not found. Creating a new folder.")
            os.makedirs(image_path)
            
        # Setup Chrome options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--allow-insecure-localhost')
        
        # Set user agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        chrome_options.add_argument(f'user-agent={user_agent}')
        
        # Add headless option if specified
        if headless:
            chrome_options.add_argument('--headless')
        
        # Initialize driver
        driver = None
        
        try:
            # Check if webdriver_path exists or is None
            if webdriver_path and not os.path.isfile(webdriver_path):
                print(f"[INFO] ChromeDriver not found at {webdriver_path}. Downloading latest version...")
                is_patched = patch.download_lastest_chromedriver()
                if not is_patched:
                    raise Exception("[ERR] Failed to download ChromeDriver")
            
            # Initialize Chrome driver
            from selenium.webdriver.chrome.service import Service
            
            if webdriver_path and os.path.isfile(webdriver_path):
                print(f"[INFO] Using ChromeDriver at: {webdriver_path}")
                service = Service(executable_path=webdriver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                print("[INFO] Using system ChromeDriver")
                driver = webdriver.Chrome(options=chrome_options)
            
            # Set up browser session
            driver.set_window_size(1000, 1050)
            driver.get("https://www.google.com")
            try:
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "W0wltc"))).click()
            except Exception:
                print("[INFO] No cookie consent dialog found")
        
        except Exception as e:
            print(f"[ERROR] Failed to initialize Chrome driver: {e}")
            
            # Try to get Chrome version from error message
            pattern = r'(\d+\.\d+\.\d+\.\d+)'
            match = re.search(pattern, str(e))
            if match:
                version = match.group(1)
                print(f"[INFO] Detected Chrome version: {version}. Downloading matching chromedriver...")
                is_patched = patch.download_lastest_chromedriver(version)
                if is_patched:
                    try:
                        # Try again with updated driver
                        from selenium.webdriver.chrome.service import Service
                        service = Service(executable_path=webdriver_path)
                        driver = webdriver.Chrome(service=service, options=chrome_options)
                        driver.set_window_size(1000, 1050)
                        driver.get("https://www.google.com")
                        try:
                            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "W0wltc"))).click()
                        except Exception:
                            pass
                    except Exception as inner_e:
                        print(f"[ERROR] Failed to initialize Chrome driver after updating: {inner_e}")
                else:
                    print("[ERROR] Failed to download matching ChromeDriver")
        
        # Check if driver was initialized successfully
        if not driver:
            raise Exception("Failed to initialize Chrome driver. Please check if Chrome is installed and try again.")
        
        self.driver = driver
        self.search_key = search_key
        self.number_of_images = number_of_images
        self.webdriver_path = webdriver_path
        self.image_path = image_path
        self.url = f"https://www.google.com/search?q={self.search_key}+site%3Ashutterstock.com&source=lnms&tbm=isch"
        self.headless = headless
        self.min_resolution = min_resolution
        self.max_resolution = max_resolution
        self.max_missed = max_missed

    def find_image_urls(self):
        """
            This function search and return a list of image urls based on the search key.
            Example:
                google_image_scraper = GoogleImageScraper("webdriver_path","image_path","search_key",number_of_photos)
                image_urls = google_image_scraper.find_image_urls()

        """
        print("[INFO] Gathering image links")
        self.driver.get(self.url)
        image_urls=[]
        count = 0
        missed_count = 0
        indx_1 = 0
        indx_2 = 0
        search_string = '//*[@id="rso"]/div/div/div[1]/div/div/div[%s]/div[2]/h3/a/div/div/div/g-img'
        time.sleep(3)
        while self.number_of_images > count and missed_count < self.max_missed:
            if indx_2 > 0:
                try:
                    imgurl = self.driver.find_element(By.XPATH, search_string%(indx_1,indx_2+1))
                    imgurl.click()
                    indx_2 = indx_2 + 1
                    missed_count = 0
                except Exception:
                    try:
                        imgurl = self.driver.find_element(By.XPATH, search_string%(indx_1+1,1))
                        imgurl.click()
                        indx_2 = 1
                        indx_1 = indx_1 + 1
                    except:
                        indx_2 = indx_2 + 1
                        missed_count = missed_count + 1
            else:
                try:
                    imgurl = self.driver.find_element(By.XPATH, search_string%(indx_1+1))
                    imgurl.click()
                    missed_count = 0
                    indx_1 = indx_1 + 1    
                except Exception:
                    try:
                        imgurl = self.driver.find_element(By.XPATH, search_string%(indx_1,indx_2+1))
                        imgurl.click()
                        missed_count = 0
                        indx_2 = indx_2 + 1
                    except Exception:
                        indx_1 = indx_1 + 1
                        missed_count = missed_count + 1
                    
            try:
                #select image from the popup
                time.sleep(1)
                class_names = ["n3VNCb","iPVvYb","r48jcc","pT0Scc","H8Rx8c"]
                images = [self.driver.find_elements(By.CLASS_NAME, class_name) for class_name in class_names if len(self.driver.find_elements(By.CLASS_NAME, class_name)) != 0 ][0]
                for image in images:
                    #only download images that starts with http
                    src_link = image.get_attribute("src")
                    if(("http" in src_link) and (not "encrypted" in src_link)):
                        print(
                            f"[INFO] {self.search_key} \t #{count} \t {src_link}")
                        image_urls.append(src_link)
                        count +=1
                        break
            except Exception:
                print("[INFO] Unable to get link")

            try:
                #scroll page to load next image
                if(count%3==0):
                    self.driver.execute_script("window.scrollTo(0, "+str(indx_1*60)+");")
                element = self.driver.find_element(By.CLASS_NAME,"mye4qd")
                element.click()
                print("[INFO] Loading next page")
                time.sleep(3)
            except Exception:
                time.sleep(1)



        self.driver.quit()
        print("[INFO] Google search ended")
        return image_urls

    def save_images(self,image_urls, keep_filenames):
        print(keep_filenames)
        #save images into file directory
        """
            This function takes in an array of image urls and save it into the given image path/directory.
            Example:
                google_image_scraper = GoogleImageScraper("webdriver_path","image_path","search_key",number_of_photos)
                image_urls=["https://example_1.jpg","https://example_2.jpg"]
                google_image_scraper.save_images(image_urls)

        """
        print("[INFO] Saving image, please wait...")
        for indx,image_url in enumerate(image_urls):
            try:
                print("[INFO] Image url:%s"%(image_url))
                search_string = ''.join(e for e in self.search_key if e.isalnum())
                image = requests.get(image_url,timeout=5)
                if image.status_code == 200:
                    with Image.open(io.BytesIO(image.content)) as image_from_web:
                        try:
                            if (keep_filenames):
                                #extact filename without extension from URL
                                o = urlparse(image_url)
                                image_url = o.scheme + "://" + o.netloc + o.path
                                name = os.path.splitext(os.path.basename(image_url))[0]
                                #join filename and extension
                                filename = "%s.%s"%(name,image_from_web.format.lower())
                            else:
                                filename = "%s%s.%s"%(search_string,str(indx),image_from_web.format.lower())

                            image_path = os.path.join(self.image_path, filename)
                            print(
                                f"[INFO] {self.search_key} \t {indx} \t Image saved at: {image_path}")
                            image_from_web.save(image_path)
                        except OSError:
                            rgb_im = image_from_web.convert('RGB')
                            rgb_im.save(image_path)
                        image_resolution = image_from_web.size
                        if image_resolution != None:
                            if image_resolution[0]<self.min_resolution[0] or image_resolution[1]<self.min_resolution[1] or image_resolution[0]>self.max_resolution[0] or image_resolution[1]>self.max_resolution[1]:
                                image_from_web.close()
                                os.remove(image_path)

                        image_from_web.close()
            except Exception as e:
                print("[ERROR] Download failed: ",e)
                pass
        print("--------------------------------------------------")
        print("[INFO] Downloads completed. Please note that some photos were not downloaded as they were not in the correct format (e.g. jpg, jpeg, png)")
