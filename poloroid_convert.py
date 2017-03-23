import numpy as np
import cv2
import math
import os
import re

# Define Constants to use for unit conversions
inch_to_pixel = 300
inch_to_mm = 25.4


def rotate_an_image(image_function):
    rows, cols, colors = image_function.shape
    M = cv2.getRotationMatrix2D((cols / 2, rows / 2), 90, 1)
    final_rotated_image = cv2.warpAffine(image_function, M, (cols, rows))

    return final_rotated_image


def convert_image(image_convert):
    # Determine image dimensions
    image_len, image_width, colors = image_convert.shape

    # Determine ratio of image length to width to determine portrait or landscape processing
    image_ratio = float(image_len) / float(image_width)

    # Apply polaroid look and feel processing before creating resized image
    blur_image = cv2.GaussianBlur(image_convert, (7, 7), 0)

    if round(image_ratio, 1) == 1.3:
        # Resize image to portrait polaroid size
        resize_image = cv2.resize(blur_image,
                                  (int(73.0 / inch_to_mm * inch_to_pixel), int(96.0 / inch_to_mm * inch_to_pixel)),
                                  interpolation=cv2.INTER_AREA)
        # Create temporary image border to pad to make whole image a square. First step in rotation so corners don't cutoff
        temp_image_border = cv2.copyMakeBorder(resize_image, 70, 215, 278, 278, cv2.BORDER_CONSTANT,
                                               value=(255, 255, 255, 255))

        # Get padded image dimensions and rotate it 90 degrees counter clockwise about the center
        rotated_image = rotate_an_image(temp_image_border)

        # Add border along the length to make image 6 inches. Cut image from the width to 4 inches. Creates 4 by 6 image
        image_length_full = cv2.copyMakeBorder(rotated_image, 0, 0, 0, 382, cv2.BORDER_CONSTANT,
                                               value=(255, 255, 255, 255))
        printsize_image = image_length_full[10:1210, :, :]

        # Draw two lines at the points where to cut the image to make a polaroid
        cv2.line(printsize_image, (0, 198), (1800, 198), color=0, thickness=1, lineType=4)
        cv2.line(printsize_image, (1467, 0), (1467, 1200), color=0, thickness=1, lineType=4)

    # If image is Square, follow square final image creation
    elif round(image_ratio, 1) == 1.0:
        # Resize image to portrait polaroid size
        resize_image = cv2.resize(blur_image, (int(3.1 * inch_to_pixel), int(3.1 * inch_to_pixel)),
                                  interpolation=cv2.INTER_AREA)
        # Create temporary image border to pad to make whole image a square. First step in rotation so corners don't cutoff
        temp_image_border = cv2.copyMakeBorder(resize_image, 60, 270, 120, 210, cv2.BORDER_CONSTANT,
                                               value=(255, 255, 255, 255))

        # Get padded image dimensions and rotate it 90 degrees counter clockwise about the center
        rotate_image = rotate_an_image(temp_image_border)

        # Add border along the length to make image 6 inches. Cut image from the width to 4 inches. Creates 4 by 6 image
        image_length_full = cv2.copyMakeBorder(rotate_image, 0, 0, 0, 540, cv2.BORDER_CONSTANT,
                                               value=(255, 255, 255, 255))
        printsize_image = image_length_full[0:1200, :, :]

        # Draw two lines at points where to cut the image to make a polaroid
        cv2.line(printsize_image, (0, 150), (1800, 150), color=0, thickness=1, lineType=4)
        cv2.line(printsize_image, (1260, 0), (1260, 1200), color=0, thickness=1, lineType=4)

    # If Image is landscape follow landscape orientation
    elif 0.7 < image_ratio < 0.8:
        # Resize image to portrait polaroid size
        resize_image = cv2.resize(blur_image, (
        int(99 / inch_to_mm * inch_to_pixel), int(math.ceil(62 / inch_to_mm * inch_to_pixel))),
                                  interpolation=cv2.INTER_AREA)

        # Add border to make it 4 by 6 image AND give polaroid borders
        printsize_image = cv2.copyMakeBorder(resize_image, 288, 180, 53, 577, cv2.BORDER_CONSTANT,
                                             value=(255, 255, 255, 255))

        # Draw lines at points where to cut the image to make a polaroid
        cv2.line(printsize_image, (0, 228), (1800, 228), color=0, thickness=1, lineType=4)
        cv2.line(printsize_image, (1276, 0), (1276, 1200), color=0, thickness=1, lineType=4)
    else:
        printsize_image = [0]

    return printsize_image


def main(image):

    current_path = os.getcwd()

    image_test = cv2.imread(os.path.join(current_path + '/uploads', image))

    printed_image = convert_image(image_test)

    if len(printed_image) == 1:
        output_file_name = "Your picture does not match the desired formats of this program. It needs to be either:\n"
        printed_image = "1.Portrait with ratio of 1.3\n 2.Landspace with ratio of 0.75 \n 3.Square with ratio of 1"
    else:
        output_file_name = image.rsplit('.', 1)[0] + '_polaroid.jpg'
        printed_image = printed_image

    return output_file_name, printed_image
