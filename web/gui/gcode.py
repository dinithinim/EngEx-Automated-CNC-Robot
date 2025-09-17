import os
import requests
import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError
from skimage.morphology import skeletonize
from skimage import img_as_bool, img_as_ubyte
import svgwrite
import xml.etree.ElementTree as ET


API_KEY = "AIzaSyDZfuNNQKi625ep6NWnbD8Ty_UyeChHZXc"
CSE_ID = "511ba7e683f874473"

def google_image_search(object_name, num_results=3):
    query = f"simple flat {object_name} image" # simple {obj} outline image
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "searchType": "image",
        "q": query,
        "num": num_results,
    }
    response = requests.get(url, params=params)
    data = response.json()
    image_urls = []
    if "items" in data:
        for item in data["items"]:
            link = item.get("link")
            if link:
                image_urls.append(link)
    return image_urls

def download_image(url, save_path):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

    if response.status_code != 200:
        print(f"Failed to download image. Status code: {response.status_code}")
        return False

    content_type = response.headers.get("Content-Type", "")
    if "image" not in content_type:
        print(f"URL is not an image: {url} (Content-Type: {content_type})")
        return False

    try:
        with open(save_path, "wb") as f:
            f.write(response.content)
        # validate image
        try:
            Image.open(save_path).verify()  # PIL verification
        except UnidentifiedImageError:
            print(f"Downloaded file is not a valid image: {url}")
            return False
        print(f"Image saved to: {save_path}")
        return True
    except Exception as e:
        print(f"Could not save image: {e}")
        return False


def preprocess_image(image_path):
    """Load image and binarize safely"""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print("OpenCV failed, retrying with PIL...")
        try:
            pil_img = Image.open(image_path).convert("L")
            img = np.array(pil_img)
        except UnidentifiedImageError:
            raise ValueError(f"Could not open image {image_path}")

    # adaptive thresholding
    binary = cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )
    return binary.astype(np.uint8)

def skeletonize_image(binary):
    """Skeletonize (thin lines)"""
    if binary is None or not isinstance(binary, np.ndarray):
        raise ValueError("Invalid binary input")
    skeleton = skeletonize(img_as_bool(binary))
    return img_as_ubyte(skeleton)

def save_as_svg(skeleton, svg_path):
    """Convert skeleton pixels into SVG polylines"""
    contours, _ = cv2.findContours(skeleton, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    h, w = skeleton.shape
    dwg = svgwrite.Drawing(svg_path, size=(w, h))

    for cnt in contours:
        if len(cnt) > 1:
            points = [(int(p[0][0]), int(p[0][1])) for p in cnt]
            dwg.add(dwg.polyline(points=points, stroke="black", fill="none", stroke_width=1))

    dwg.save()
    print(f"SVG saved to: {svg_path}")

def svg_to_gcode(svg_path, gcode_path):
    """SVG → G-code conversion (polylines only)"""
    tree = ET.parse(svg_path)
    root = tree.getroot()
    ns = {"svg": "http://www.w3.org/2000/svg"}

    gcode_lines = [
        "G21 ; set units to mm",
        "G90 ; absolute positioning",
        "F1000",
        "G0 Z5.0 ; pen up"
    ]

    for poly in root.findall(".//svg:polyline", ns):
        points = poly.attrib.get("points", "").strip().split()
        coords = []
        for p in points:
            if "," in p:
                x, y = map(float, p.split(","))
                coords.append((x, y))
        if len(coords) < 2:
            continue
        x0, y0 = coords[0]
        gcode_lines.append(f"G0 X{x0:.2f} Y{y0:.2f}")
        gcode_lines.append("G1 Z-1.0 F300 ; pen down")
        for (x, y) in coords[1:]:
            gcode_lines.append(f"G1 X{x:.2f} Y{y:.2f}")
        gcode_lines.append("G0 Z5.0 ; pen up")

    gcode_lines.append("G0 X0 Y0 ; return home")
    gcode_lines.append("M2 ; end program")

    with open(gcode_path, "w") as f:
        f.write("\n".join(gcode_lines))
    print(f"G-code saved to: {gcode_path}")

def optimize_gcode(input_gcode, optimized_gcode):
    """Remove duplicate moves"""
    with open(input_gcode, "r") as f:
        lines = f.readlines()
    optimized = []
    prev = ""
    for line in lines:
        if line != prev:
            optimized.append(line)
        prev = line
    with open(optimized_gcode, "w") as f:
        f.writelines(optimized)
    print(f"Optimized G-code saved to: {optimized_gcode}")


#if __name__ == "__main__":
def main_func(object_name):
    #object_name = input("Enter object to search sketch for: ").strip()
    image_urls = google_image_search(object_name, num_results=3)

    if not image_urls:
        print("No images found for the query.")
        exit()

    save_folder = "images"
    os.makedirs(save_folder, exist_ok=True)

    # file_name = f"sketch.jpg"
    # svg_name = f"sketch.svg"
    # gcode_name = f"output.gcode"
    # optimized_name = f"output_optimized.gcode"

    # img_path = "images/sketch.jpg"
    # svg_path = "images/sketch.svg"
    # gcode_path = "gcode/output.gcode"
    # optimized_path = "gcode/output_optimized.gcode"

    # Try each image URL until success
    for url in image_urls:
        if download_image(url, "images/sketch.jpg"):
            try:
            #     binary = preprocess_image(img_path)
            #     skeleton = skeletonize_image(binary)
            #     save_as_svg(skeleton, svg_path)
            #     svg_to_gcode(svg_path, gcode_path)
            #     optimize_gcode(gcode_path, optimized_path)
            #     print("Pipeline finished successfully!")
                #break
                gcode_generation()
                return 0
            except Exception as e:
                print(f"Processing failed for {url}: {e}")
        else:
            print(f"Skipping URL: {url}")
    else:
        print("All image URLs failed. Cannot generate G-code.")
        return 1
    

def gcode_generation():
    img_path = "images/sketch.jpg"
    svg_path = "images/sketch.svg"
    gcode_path = "gcode/output.gcode"
    optimized_path = "gcode/output_optimized.gcode"

    
    binary = preprocess_image(img_path)
    skeleton = skeletonize_image(binary)
    save_as_svg(skeleton, svg_path)
    svg_to_gcode(svg_path, gcode_path)
    optimize_gcode(gcode_path, optimized_path)
    print("Pipeline finished successfully!")
    return 0

    
