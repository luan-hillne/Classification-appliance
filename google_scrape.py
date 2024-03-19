import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image

# search_terms = ['Nồi chiên không dầu', 'Bàn là', 'Máy hút bụi', 'Bếp từ', 'Máy ép',
#                 'Máy đánh trứng','Máy lọc nước','Bình nước nóng', 'Thiết bị Camera',
#                 'Lò vi sóng', 'Lò nướng','Máy lọc không khí']
search_terms =['thiết bị camera' ]
total_images_to_download = 200
# Function to fetch image links from a given Google Images search page URL
def fetch_image_links(url):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    thumbnails = []
    for raw_img in soup.find_all('img'):
        link = raw_img.get('src')
        if link and link.startswith("https://"):
            thumbnails.append(link)
    return thumbnails

# Function to download images
def download_images(image_links, folder_name, start_index):
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

# Fetch and download images for each search term
for term in search_terms:
    page_number = 0
    images_downloaded = 0
    while images_downloaded < total_images_to_download:
        page_number += 1
        url = f'https://www.google.no/search?q={term}&client=opera&hs=cTQ&source=lnms&tbm=isch&sa=X&safe=active&ved=0ahUKEwig3LOx4PzKAhWGFywKHZyZAAgQ_AUIBygB&biw=1920&bih=982&start={page_number}'
        #url = f'https://shopee.vn/search?q = {term}keyword=&page=2'
        image_links = fetch_image_links(url)
        if not image_links:
            print(f"No more images found for {term}.")
            break
        download_images(image_links, term.replace(' ', ''), start_index=images_downloaded + 1)
        images_downloaded += len(image_links)
