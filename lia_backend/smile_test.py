from google.cloud import vision
import cv2
import io
import os
import logging
from google.auth.exceptions import DefaultCredentialsError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def detect_smile(image_path):
    # Load the image
    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    # Create a Vision API client
    client = vision.ImageAnnotatorClient()

    # Create the image object
    image = vision.Image(content=content)

    # Define the features to be extracted (face detection)
    features = [vision.Feature(type=vision.Feature.Type.FACE_DETECTION)]

    # Make the API request
    response = client.face_detection(image=image)  # Correct method call

    # Process face detection results
    for face in response.face_annotations:
        if face.joy_likelihood >= 0.7:
            return True

    return False

def analyze_images(directory):
    smiling_images = 0
    total_images = 0

    for i in range(1, 11):  # From P14_frame1.jpg to P14_frame10.jpg
        image_path = os.path.join(directory, f"P14_frame{i}.jpg")
        if os.path.isfile(image_path):
            total_images += 1
            if detect_smile(image_path):
                smiling_images += 1
                logger.info(f"{image_path}: Smile detected.")
            else:
                logger.info(f"{image_path}: No smile detected.")
        else:
            logger.warning(f"{image_path} does not exist.")

    return smiling_images, total_images

try:
    # Directory containing the still images
    stills_directory = r"C:\Users\benth\Desktop\capstone\smile_test\stills"

    smiling_images, total_images = analyze_images(stills_directory)

    if total_images > 0:
        smile_rate = smiling_images / total_images
        logger.info(f"Smile rate: {smile_rate:.2%}")
    else:
        logger.info("No images to analyze.")

except DefaultCredentialsError:
    logger.error("Failed to authenticate. Check your Google Cloud credentials.")
    logger.error("Ensure GOOGLE_APPLICATION_CREDENTIALS environment variable is set correctly.")
except Exception as e:
    logger.error(f"An unexpected error occurred: {str(e)}")

