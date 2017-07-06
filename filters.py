import cv2
import numpy as np
import blend


def vintage_blue(image):
    # Convert image to float to avoid overflow and ease computations
    image = np.array(image, dtype=np.float64)
    # Increase intensity of the blue channel higher than other two
    # Increased values were found by fiddling until the results looked satisfactory
    image[:, :, 0] += 75
    image[:, :, 1] += 20
    image[:, :, 2] += 25
    # Normalize the image
    merged_norm_image = cv2.normalize(image, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    # Create black and white mask based on image dimensions
    _create_mask(image)
    # Read in the mask output by _create_mask function
    masked_image = cv2.imread('mask.png')
    # Blend the mask and the input image using Assignment 6 blend functions
    # We use the Mask as the input black image itself to futher fade the effects
    final = blend.blend_two_images(masked_image, merged_norm_image, masked_image)

    return final


def black_and_white(image):
    # Convert Image to Grayscale
    image_black_and_white = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # Add Salt and Pepper Noise
    image_noise = _add_salt_pepper_noise(image_black_and_white, 150)
    # Blur the image slightly
    kernel = _get_median_kernel(5)
    image_final = cv2.filter2D(image_noise, -1, kernel)

    return image_final


def vintage_yellow(image):
    # Increase Contrast of Image
    image_boosted_contrast = _increase_contrast(image)
    # Convert image to float type
    image = np.array(image_boosted_contrast, dtype=np.float64)
    # Split all channels and increase the green and red channel intensities
    image[:, :, 1] += 75
    image[:, :, 2] += 75
    # Normalize the image
    merged_norm_image = cv2.normalize(image, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    return merged_norm_image


# Sepia Specifications: http://stackoverflow.com/questions/1061093/how-is-a-sepia-tone-created
def sepia(image):
    image = np.array(image, dtype=np.float64)
    # Split image into all three channels
    blue_channel = image[:, :, 0]
    green_channel = image[:, :, 1]
    red_channel = image[:, :, 2]
    # Create new  channels by multiplying existing by sepia specified values
    out_red_channel = blue_channel * .189 + green_channel * .769 + red_channel * .393
    out_green_channel = blue_channel * .168 + green_channel * .686 + red_channel * .349
    out_blue_channel = blue_channel * .131 + green_channel * .534 + red_channel * .272
    # Merge the channels and normalize the image
    final_image = cv2.merge((out_blue_channel, out_green_channel, out_red_channel))
    final_output_image = cv2.normalize(final_image, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    return final_output_image

# Called Acid Wash in the UI
def funky_image(image):
    # Convert image to HSV colorspace
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Alpha Blend HSV image with input image
    blended_image = hsv_image * 0.25 + image * 0.75
    # Normalize and Blur the output
    final_image = cv2.normalize(blended_image, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    final_image_filtered = cv2.filter2D(final_image, -1, kernel=_get_median_kernel(5))

    return final_image_filtered


def _add_salt_pepper_noise(image, intensity_value=10):
    # Create Random Matrix
    random_matrix = np.round(np.random.random(image.shape) * intensity_value)
    # Add Salt and Pepper Noise
    image = np.where(random_matrix == 0, 0, image)
    image = np.where(random_matrix == intensity_value, 255, image)

    return image


def _get_median_kernel(k):

    kernel = np.ones((k, k), dtype=np.float64) * float(1./k**2)

    return kernel


def _increase_contrast(image):
    # Convert to YUV colorspace and equalize histogram for 1st channel
    if len(image.shape) == 3:
        image_YUV = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        image_YUV[:, :, 0] = cv2.equalizeHist(image_YUV[:,:,0])
        img_output = cv2.cvtColor(image_YUV, cv2.COLOR_YUV2BGR)
    else:
        img_output = cv2.equalizeHist(image)

    return img_output


def _create_mask(image):
    # Create White Image
    mask_image = np.ones((image.shape[0], image.shape[1]), dtype=np.float64)
    # Get total image dimensions
    row_total = image.shape[0]
    col_total = image.shape[1]
    # Determine the length that the fading should be along the edges and Curve-Depth of the fading in the mask
    end_length = row_total / 2
    curve_depth = end_length / 10
    # Create Arrays for columns indexes to calculate the span of pixel fill
    slope_line_values_list = list(range(end_length-1,-1,-1))
    # Helper function to calculate the column indexes that would fall on a parabolic curve
    parabola_values_list = __calculate_parabola_values(curve_depth, end_length)

    # Calculate pixel values from darkest to lightest so we can acheive a fade in the mask
    pixel_values_list = np.arange(0, 0.75, 0.75/end_length)

    # Fill the four corners using the appropriate length to fill and the uniform pixel values
    # Use the linear and parabolic value to determine the span of columns to fill with the pixel values
    # Each corner loop operates on that corner's geometry
    for corner_idx in range(4):
        for idx in range(end_length):
            slope_line_value = slope_line_values_list[idx] #40
            parabola_value = parabola_values_list[idx]
            end_col_idx = int(round(slope_line_value - parabola_value))
            # Top-Right
            for top_right_idx in range(end_col_idx):
                mask_image[idx, top_right_idx] = float(pixel_values_list[top_right_idx])
            # Bottom-Right
            row_num_bottom_right = row_total - idx
            for bottom_right_idx in range(col_total - end_col_idx, col_total-1):
                mask_image[row_num_bottom_right-1, bottom_right_idx] = \
                    float(pixel_values_list[-1 * (bottom_right_idx - (col_total - end_col_idx))])
            # Top-Right
            for top_right_idx in range(col_total - end_col_idx, col_total-1):
                mask_image[idx, top_right_idx] = \
                    float(pixel_values_list[-1 * (top_right_idx - (col_total - end_col_idx))])
            # Bottom-Left
            row_num_bottom_left = row_total - idx
            for bottom_left_idx in range(end_col_idx):
                mask_image[row_num_bottom_left-1, bottom_left_idx] = float(pixel_values_list[bottom_left_idx])
    # Output mask to directory
    mask_display = cv2.normalize(mask_image, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    cv2.imwrite('mask.png', mask_display)


def __calculate_parabola_values(vertex_height, length_total):
    coordinates = {'x1': 0., 'y1':0., 'x2':float(length_total/2), 'y2':float(vertex_height), 'x3':float(length_total)-1, 'y3':0.}
    A1 = (-1*coordinates['x1']**2) + (coordinates['x2']**2)
    B1 = (-1*coordinates['x1']) + (coordinates['x2'])
    D1 = (-1*coordinates['y1']) + (coordinates['y2'])
    A2 = (-1*coordinates['x2']**2) + (coordinates['x3']**2)
    B2 = (-1*coordinates['x2']) + (coordinates['x3'])
    D2 = (-1*coordinates['y2']) + (coordinates['y3'])
    B_multiplier = -1 * (B2/B1)
    A3 = B_multiplier * A1 + A2
    D3 = B_multiplier * D1 + D2

    a = D3/A3
    b = (D1-A1*a) / B1
    c = coordinates['y1'] - (a * coordinates['x1'] ** 2) - (b * coordinates['x1'])

    # Equation: ax2 + bx + c
    parabola_values = []

    for idx in range(int(length_total)):
        y_value = (a * float(idx) ** 2) + (b * float(idx)) + c
        parabola_values.append(y_value)

    return parabola_values
