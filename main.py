# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 11:02:06 2020

@author: OHyic

"""
#Import libraries
import os
import concurrent.futures
from GoogleImageScraper import GoogleImageScraper
from patch import webdriver_executable


def worker_thread(search_key):
    try:
        print(f"[DEBUG] Starting worker thread for '{search_key}'")
        image_scraper = GoogleImageScraper(
            image_path = image_path,
            webdriver_path = webdriver_path,
            search_key = search_key, 
            number_of_images = number_of_images, 
            headless = headless, 
            min_resolution = min_resolution, 
            max_resolution = max_resolution, 
            max_missed = max_missed)
        print(f"[DEBUG] Created scraper object for '{search_key}'")
        image_urls = image_scraper.find_image_urls()
        print(f"[DEBUG] Found {len(image_urls)} image URLs for '{search_key}'")
        image_scraper.save_images(image_urls, keep_filenames)
        print(f"[DEBUG] Saved images for '{search_key}'")
        
        #Release resources
        del image_scraper
    except Exception as e:
        print(f"[ERROR] Exception in worker thread for '{search_key}': {str(e)}")

if __name__ == "__main__":
    print("[DEBUG] Starting Google Image Scraper")
    
    #Define file path
    webdriver_path = os.path.normpath(os.path.join(os.getcwd(), 'webdriver', webdriver_executable()))
    if not os.path.exists(webdriver_path):
        print("[INFO] Webdriver not found. Downloading latest version...")
        from patch import download_lastest_chromedriver
        download_lastest_chromedriver()
        
    image_path = os.path.normpath(os.path.join(os.getcwd(), 'photos'))
    print(f"[DEBUG] Image path: {image_path}")


    #Add new search key into array ["cat","t-shirt","apple","orange","pear","fish"]
    search_keys = list(set(["Honda Jazz"]))

    #Parameters
    number_of_images = 100                # Desired number of images
    headless = False                    # True = No Chrome GUI
    min_resolution = (0, 0)             # Minimum desired image resolution
    max_resolution = (9999, 9999)       # Maximum desired image resolution
    max_missed = 10                     # Max number of failed images before exit
    number_of_workers = 10               # Number of "workers" used
    keep_filenames = False              # Keep original URL image filenames

    #Run each search_key in a separate thread
    #Automatically waits for all threads to finish
    #Removes duplicate strings from search_keys
    with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_workers) as executor:
        executor.map(worker_thread, search_keys)
