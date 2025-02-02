import streamlit as st
import requests
from woocommerce import API
import zipfile
import os
from PIL import Image
from io import BytesIO

# Access secrets from Streamlit
WC_API_URL = st.secrets["WC_API_URL"]
WC_CONSUMER_KEY = st.secrets["WC_CONSUMER_KEY"]
WC_CONSUMER_SECRET = st.secrets["WC_CONSUMER_SECRET"]

# Initialize the WooCommerce API
wcapi = API(
    url=WC_API_URL,
    consumer_key=WC_CONSUMER_KEY,
    consumer_secret=WC_CONSUMER_SECRET,
    version="wc/v3"
)

def fetch_product_images(product_id):
    """Fetch product images from WooCommerce using the product ID."""
    response = wcapi.get(f"products/{product_id}")
    if response.status_code == 200:
        product_data = response.json()
        images = product_data.get('images', [])
        image_urls = [img['src'] for img in images]
        return image_urls
    else:
        st.error("Failed to fetch product data. Please check the product ID.")
        return []

def download_images(image_urls):
    """Download images from the provided URLs."""
    images = []
    for url in image_urls:
        response = requests.get(url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            images.append(img)
        else:
            st.warning(f"Failed to download image from {url}")
    return images

def create_zip(images, zip_filename="product_images.zip"):
    """Create a zip file from the downloaded images."""
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for i, img in enumerate(images):
            img_filename = f"image_{i+1}.png"
            img.save(img_filename)
            zipf.write(img_filename)
            os.remove(img_filename)  # Clean up the individual image file
    return zip_filename

def main():
    st.title("WooCommerce Product Image Downloader")

    # Create two columns
    col1, col2 = st.columns(2)

    # Left column: Input field
    with col1:
        product_id = st.text_input("Enter Product ID:")

    # Right column: Display images and download button
    with col2:
        if product_id:
            # Fetch image URLs
            image_urls = fetch_product_images(product_id)
            
            if image_urls:
                st.success(f"Found {len(image_urls)} images for product ID {product_id}.")
                
                # Display all images in a single st.image() widget
                st.image(image_urls, caption=[f"Image {i+1}" for i in range(len(image_urls))], use_column_width=True)
                
                # Download images
                images = download_images(image_urls)
                
                with col1:
                    if images:
                        # Create a zip file
                        zip_filename = create_zip(images)
                        
                        # Provide download button
                        with open(zip_filename, "rb") as f:
                            st.download_button(
                                label="Download Images as Zip",
                                data=f,
                                file_name=zip_filename,
                                mime="application/zip"
                            )
                        
                        # Clean up the zip file
                        os.remove(zip_filename)
                    else:
                        st.warning("No images were downloaded.")
            else:
                st.warning("No images found for the given product ID.")

if __name__ == "__main__":
    main()
