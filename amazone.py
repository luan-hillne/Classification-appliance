import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image

class AmazonImageScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Upgrade-Insecure-Requests": "1",
            "Accept-Language": "en,en-GB;q=0.9,vi-VN;q=0.8,vi;q=0.7,en-US;q=0.6"
        }
        self.total_images_to_download = 100
        self.base_url = "https://www.amazon.in/s?k={term}&page={page_number}&qid=1710771319&ref=sr_pg_{page_number}"

    def get_doc(self, url):
        response = requests.get(url, headers=self.headers)
        print(response.status_code)
        if response.ok:
            with open("amazon_html_page.html", "a", encoding='utf8') as file:
                file.write(response.text)
            soup = BeautifulSoup(response.text, "html.parser")
            thumbnails = []
            for raw_img in soup.find_all('img'):
                link = raw_img.get('src')
                if link and link.startswith("https://"):
                    thumbnails.append(link)
            return thumbnails

    def download_images(self, image_links, folder_name, start_index):
        folder_path = os.path.join('images', folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        for i, thumbnail in enumerate(image_links, start=start_index):
            try:
                img_data = requests.get(thumbnail).content
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f'image_{i}_{current_time}.jpg'
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, 'wb') as handler:
                    handler.write(img_data)
                # Open the downloaded image using PIL
                img = Image.open(file_path)
                # Convert the image to 'RGB' mode before saving as JPEG
                img = img.convert('RGBA')  # Convert to RGBA mode
                if img.mode == 'RGBA':
                    # If image has transparency, convert to 'RGB' mode
                    img = img.convert('RGB')
                # Save the resized image
                img.save(file_path)

                print(f"Downloaded and resized image {file_name}")
            except Exception as e:
                print(f"Failed to download and resize image {i}: {e}")

    def scrape_images(self, search_terms):
        for term in search_terms:
            page_number = 0
            images_downloaded = 0
            while images_downloaded < self.total_images_to_download:
                page_number += 1
                url = self.base_url.format(term=term, page_number=page_number)
                image_links = self.get_doc(url)
                if not image_links:
                    print(f"No more images found for {term}.")
                    break
                self.download_images(image_links, term.replace(' ', ''), start_index=images_downloaded + 1)
                images_downloaded += len(image_links)

if __name__ == "__main__":
    scraper = AmazonImageScraper()
    # search_terms = ['air fryer', 'iron', 'robot vacuum cleaner', 'induction hob', 'fruit machine',
    #                 'egg beater', 'microwave oven', 'water purifier', 'storage water heater', 'webcam',
    #                 'smart camera', 'griller', 'air purifier']
    search_terms = ['iron']
    scraper.scrape_images(search_terms)
