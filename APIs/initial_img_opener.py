import os
import requests
import subprocess
import platform

API_KEY = "<API_KEY_HERE>"
CSE_ID = "<CSE_ID_HERE>"

def google_image_search(object_name):
    query = f"simple {object_name} outline image"
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "searchType": "image",
        "q": query,
        "num": 1,
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "items" in data:
        first_image_url = data["items"][0]["link"]
        return first_image_url
    else:
        return None

def download_image(url, save_path):
    response = requests.get(url)
    with open(save_path, "wb") as f:
        f.write(response.content)
    print(f"Image saved to: {save_path}")

def open_in_inkscape(image_path):
    inkscape_command = "inkscape"

    if platform.system() == "Windows":
        # Uncomment and set your inkscape.exe path if it is not in PATH
        # inkscape_command = r"C:\Program Files\Inkscape\bin\inkscape.exe"
        pass

    try:
        subprocess.Popen([inkscape_command, image_path])
        print(f"Opened image in Inkscape: {image_path}")
    except FileNotFoundError:
        print("Inkscape executable not found. Please ensure Inkscape is installed and in your system PATH.")

if __name__ == "__main__":
    object_name = input("Enter object to search sketch for: ").strip()
    image_url = google_image_search(object_name)
    if image_url:
        print(f"Found image URL: {image_url}")

        save_folder = "C:/Users/USER/Desktop/cnc_project"
        os.makedirs(save_folder, exist_ok=True)
        file_name = f"{object_name.replace(' ', '_')}_pencil_sketch.jpg"
        save_path = os.path.join(save_folder, file_name)

        download_image(image_url, save_path)
        open_in_inkscape(save_path)

    else:
        print("No image found for the query.")
