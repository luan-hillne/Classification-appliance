import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image

class ScapeLazada():
    def fetch_image_links(self, term, page_number):
        url = f'https://www.lazada.vn/catalog/?page={page_number}&q={term}'
        driver = webdriver.Chrome()
        driver.get(url)

        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#root")))

        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        thumbnails = []
        for item in soup.findAll('img'):
            link = item.get('src')
            if link and link.startswith("https://") and link.endswith(".webp"):
                # Remove the _80x80q80.jpg_ part from the link
                link = link.split("_")[0]
                thumbnails.append(link)
        driver.close()
        return thumbnails

    def download_images(self, image_links, folder_name, start_index):
        folder_path = os.path.join('appliance', folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        for i, thumbnail in enumerate(image_links, start=start_index):
            try:
                img_data = requests.get(thumbnail).content
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f'image_shoppe_{i}_{current_time}.jpg'
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, 'wb') as handler:
                    handler.write(img_data)

                # Open the downloaded image using PIL
                img = Image.open(file_path)

                if img.mode == 'RGBA':
                    img = img.convert('RGB')

                # Resize the image while preserving aspect ratio
                img.thumbnail((320, 320))

                # If the image is still larger than 320x320, crop it to 320x320
                left = (img.width - 320) / 2
                top = (img.height - 320) / 2
                right = (img.width + 320) / 2
                bottom = (img.height + 320) / 2
                img = img.crop((left, top, right, bottom))

                # Save the resized image
                img.save(file_path)

                print(f"Downloaded and resized image {file_name}")
            except Exception as e:
                print(f"Failed to download and resize image {i}: {e}")

    def scrape(self):
        search_terms = ['máy ảnh']  # Make sure search terms are in a list
        total_images = 300
        for term in search_terms:
            page_number = 0
            images_downloaded = 0
            while images_downloaded < total_images:
                page_number += 1
                image_links = self.fetch_image_links(term, page_number)
                if not image_links:
                    print(f"No more images found for {term}.")
                    break
                self.download_images(image_links, term.replace(' ', ''), start_index=images_downloaded + 1)
                images_downloaded += len(image_links)

sl = ScapeLazada()
sl.scrape()
