import os
import pyautogui
import cv2 as cv
import pytesseract
import numpy
from collections import Counter

# Monkeypatch for pyautogui on multi-monitor setups. Goes after pyautogui import
from PIL import ImageGrab, Image
from functools import partial
ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)


IMAGE_PATH_BASE = 'cicauto/data/images/'

# TODO: compare 2 images, showing difference map


def get_image_path(filename):
    return os.path.join(IMAGE_PATH_BASE, filename)


def open_image(filename):
    image_path = get_image_path(filename)
    return Image.open(image_path)


def get_region_image(x, y, width, height, image_path=None):
    return pyautogui.screenshot(imageFilename=image_path, region=(x, y, width, height))


def get_sub_image(img: Image, region):
    box = img.getbbox()
    # TODO: assert region in box bounds (Let downstream error propogate?)
    return img.crop(region)


def get_top_colors(img: Image, max_colors=0):
    # TODO: idk if I need this, maybe add extrema checking with tolerance
    colors = img.getcolors(img.size[0]*img.size[1])


def erosion(img: numpy.ndarray, erosion_size, erosion_shape=cv.MORPH_RECT):
    # Ref: https://docs.opencv.org/3.4/db/df6/tutorial_erosion_dilatation.html
    # Note: in a grayscale image, white pixels are foreground, black pixels are background
    # cv.MORPH_RECT, cv.MORPH_CROSS, cv.MORPH_ELLIPSE
    element = cv.getStructuringElement(erosion_shape, (2 * erosion_size + 1, 2 * erosion_size + 1), (erosion_size, erosion_size))
    erosion_img = cv.erode(img, element)
    return erosion_img


def dilation(img: numpy.ndarray, dilation_size: int, dilation_shape=cv.MORPH_RECT):
    # Ref: https://docs.opencv.org/3.4/db/df6/tutorial_erosion_dilatation.html
    # Note: in a grayscale image, white pixels are foreground, black pixels are background
    element = cv.getStructuringElement(dilation_shape, (2 * dilation_size + 1, 2 * dilation_size + 1), (dilation_size, dilation_size))
    dilation_img = cv.dilate(img, element)
    return dilation_img


def convert_from_cv2_to_image(img: numpy.ndarray) -> Image:
    # See: https://stackoverflow.com/a/65634189
    # return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    return Image.fromarray(img)


def convert_from_image_to_cv2(img: Image) -> numpy.ndarray:
    # See: https://stackoverflow.com/a/65634189
    # return cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)
    return numpy.asarray(img)


def get_text_from_image(img: Image, threshold=200):
    # Starting with a PIL Image, convert to cv2 numpy array
    cv_img = convert_from_image_to_cv2(img)

    # Resize image for better OCR accuracy
    h, w = cv_img.shape[:2]
    cv_img = cv.resize(cv_img, (w * 4, h * 4))

    # Grayscale
    grayscale = cv.cvtColor(cv_img, cv.COLOR_BGR2GRAY)

    # Threshold (essentially convert all text to black, everything else to white)
    ret, bw_img = cv.threshold(grayscale, threshold, 255, cv.THRESH_BINARY_INV)

    # Take away from and add to the image for better cross checking OCR
    erode_img = erosion(bw_img, 5)
    dilate_img = dilation(bw_img, 5)

    # OCR the image to find numbers
    # Ref: https://github.com/tesseract-ocr/tessdoc/blob/main/ImproveQuality.md
    custom_config = r'--oem 3 --psm 6 outputbase digits'
    image_text_base = pytesseract.image_to_string(bw_img, config=custom_config).replace('\n', '')
    image_text_erode = pytesseract.image_to_string(erode_img, config=custom_config).replace('\n', '')
    image_text_dilate = pytesseract.image_to_string(dilate_img, config=custom_config).replace('\n', '')

    texts = [image_text_base, image_text_erode, image_text_dilate]
    only_digits = [''.join(filter(str.isdigit, x)) for x in texts]
    non_empty_texts = [x for x in only_digits if x]
    in_range_texts = [x for x in non_empty_texts if 0 < int(x) < 120]
    if in_range_texts:
        text_counter = Counter(in_range_texts)
        image_text = text_counter.most_common(1)[0][0]
        return image_text
    return ''


'''
import win32gui
import win32api

dc = win32gui.GetDC(0)
red = win32api.RGB(255, 0, 0)

old = win32gui.GetPixel(dc, 0, 0)
win32gui.SetPixel(dc, 0, 0, red)  # draw red at 0,0
win32gui.SetPixel(dc, 0, 0, old)
'''

if __name__ == '__main__':
    # primitive helper code for taking a screenshot snippet and saving to file in cicauto/data/images
    input('TopLeft')
    x1, y1 = pyautogui.position()
    x1 += 2560
    print(f'{x1=} {y1=}')

    input('BottomRight')
    x2, y2 = pyautogui.position()
    x2 += 2560
    print(f'{x2=} {y2=}')

    filepath = input('filename: ')
    filepath = f'{filepath}.png'
    filepath = os.path.join('..', IMAGE_PATH_BASE, filepath)
    get_region_image(x1, y1, x2 - x1, y2 - y1, filepath)

