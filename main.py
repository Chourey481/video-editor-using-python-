import os
import requests
from moviepy import ImageSequenceClip
from PIL import Image

def fetch_images_from_pexels(api_key, query, per_page=15, page=1, save_folder="videos"):
    """
    Fetches images from Pexels API based on a search query and saves them in the specified folder.

    Parameters:
        api_key (str): Pexels API key.
        query (str): Search term for images.
        per_page (int): Number of images to fetch per page (max 80).
        page (int): Page number to fetch.
        save_folder (str): Folder to save the downloaded images.
    """
    # Create the folder if it doesn't exist
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Pexels API endpoint
    url = "https://api.pexels.com/v1/search"

    # API headers
    headers = {
        "Authorization": api_key
    }

    # API parameters
    params = {
        "query": query,
        "per_page": per_page,
        "page": page
    }

    try:
        # Make the API request
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse the JSON response
        data = response.json()
        photos = data.get("photos", [])

        if not photos:
            print("No photos found for the given query.")
            return

        # Download and save each photo
        for photo in photos:
            image_url = photo.get("src", {}).get("original")
            if image_url:
                image_id = photo.get("id")
                file_extension = image_url.split(".")[-1]
                file_name = f"{image_id}.{file_extension}"
                file_path = os.path.join(save_folder, file_name)

                # Download the image
                with requests.get(image_url, stream=True) as img_response:
                    img_response.raise_for_status()
                    with open(file_path, "wb") as img_file:
                        for chunk in img_response.iter_content(chunk_size=8192):
                            img_file.write(chunk)

                print(f"Downloaded: {file_name}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def crop_images_to_reel_format(folder, output_folder, aspect_ratio=(9, 16)):
    """
    Crops images to the specified aspect ratio (default 9:16 for Instagram Reels).

    Parameters:
        folder (str): Folder containing the images to crop.
        output_folder (str): Folder to save cropped images.
        aspect_ratio (tuple): Target aspect ratio (width, height).
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(folder):
        if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(folder, file_name)
            try:
                with Image.open(image_path) as img:
                    width, height = img.size
                    target_width = width
                    target_height = int(width * aspect_ratio[1] / aspect_ratio[0])

                    if target_height > height:
                        target_height = height
                        target_width = int(height * aspect_ratio[0] / aspect_ratio[1])

                    left = (width - target_width) / 2
                    top = (height - target_height) / 2
                    right = left + target_width
                    bottom = top + target_height

                    cropped_img = img.crop((left, top, right, bottom))
                    cropped_img = cropped_img.resize((1080, 1920), Image.ANTIALIAS)

                    cropped_img.save(os.path.join(output_folder, file_name))
                    print(f"Cropped and saved: {file_name}")
            except Exception as e:
                print(f"Failed to process {file_name}: {e}")

def create_reel_from_images(folder, output_video, duration=20):
    """
    Creates a video from images in the specified folder.

    Parameters:
        folder (str): Folder containing images.
        output_video (str): Path to save the video.
        duration (int): Total duration of the video in seconds.
    """
    images = []
    for file_name in sorted(os.listdir(folder)):
        if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
            images.append(os.path.join(folder, file_name))

    if not images:
        print("No images found to create a video.")
        return

    try:
        clip = ImageSequenceClip(images, fps=len(images) / duration)
        clip.write_videofile(output_video, codec="libx264", fps=24)
        print(f"Video created: {output_video}")
    except Exception as e:
        print(f"Failed to create video: {e}")

# Replace with your Pexels API key
PEXELS_API_KEY = "NpiiyRX7XO04Yscj5xyXZ9f7P0cbhjUgiskQxHZ3L229wMMM6HoGKtqJ"

# Parameters
SEARCH_QUERY = "nature"  # Change this to any keyword you want
PER_PAGE = 10  # Number of images per request
PAGE = 1  # Page number to fetch
SAVE_FOLDER = "images"  # Folder to save images
CROPPED_FOLDER = "cropped_videos"  # Folder for cropped images
OUTPUT_VIDEO = "reel_video.mp4"  # Final video path
DURATION = 20  # Duration of the video in seconds

# Fetch, crop, and create video
fetch_images_from_pexels(PEXELS_API_KEY, SEARCH_QUERY, PER_PAGE, PAGE, SAVE_FOLDER)
crop_images_to_reel_format(SAVE_FOLDER, CROPPED_FOLDER)
create_reel_from_images(CROPPED_FOLDER, OUTPUT_VIDEO, DURATION)
