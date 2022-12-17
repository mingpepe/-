from PIL import Image

import pytesseract


def preprocess(image):
    return image


def image_to_string(path):
    image = Image.open(path)
    image = preprocess(image)
    return pytesseract.image_to_string(image)
