import cv2
import numpy as np
import blend


def vintage_blue(image):

    image = np.array(image, dtype=np.float64)

    blue_channel = image[:, :, 0]
    green_channel = image[:, :, 1]
    red_channel = image[:, :, 2]

    blue_channel += 75
    green_channel += 20
    red_channel += 25

    final_image = cv2.merge((blue_channel, green_channel, red_channel))

    merged_norm_image = cv2.normalize(final_image, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    kernel = _get_median_kernel(5)

    dst = cv2.filter2D(merged_norm_image, -1, kernel)

    _create_mask(image)

    masked_image = cv2.imread('mask.png')

    final = blend.blend_two_images(dst, masked_image, masked_image)

    return final


def black_and_white(image):
    image_black_and_white = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    image_noise = _add_salt_pepper_noise(image_black_and_white, 150)
    kernel = _get_median_kernel(5)

    image_final = cv2.filter2D(image_noise, -1, kernel)

    return image_final


def vintage_yellow(image):
    image_boosted_contrast = _increase_contrast(image)

    image = np.array(image_boosted_contrast, dtype=np.float64)

    blue_channel = image[:, :, 0]
    green_channel = image[:, :, 1]
    red_channel = image[:, :, 2]

    green_channel += 75
    red_channel += 75

    final_image = cv2.merge((blue_channel, green_channel, red_channel))

    merged_norm_image = cv2.normalize(final_image, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    return merged_norm_image


# Stack Overflow Code: http://stackoverflow.com/questions/1061093/how-is-a-sepia-tone-created
def sepia(image):
    image = np.array(image, dtype=np.float64)

    blue_channel = image[:, :, 0]
    green_channel = image[:, :, 1]
    red_channel = image[:, :, 2]

    out_red_channel = blue_channel * .189 + green_channel * .769 + red_channel * .393
    out_green_channel = blue_channel * .168 + green_channel * .686 + red_channel * .349
    out_blue_channel = blue_channel * .131 + green_channel * .534 + red_channel * .272

    final_image = cv2.merge((out_blue_channel, out_green_channel, out_red_channel))

    final_output_image = cv2.normalize(final_image, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    return final_output_image


def funky_image(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    blended_image = hsv_image * 0.25 + image * 0.75

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
    # mask_image = np.array(np.copy(image), dtype=np.float64)
    mask_image = cv2.normalize(mask_image, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

    # Get total image dimensions
    row_total = image.shape[0]
    col_total = image.shape[1]

    # Determine End-Length and Curve-Depth
    end_length = row_total / 2
    curve_depth = end_length / 10
    # Create Arrays for stop lengths
    slope_line_values_list = list(range(end_length-1,-1,-1))
    parabola_values_list = __calculate_parabola_values(curve_depth, end_length)

    # Calculate pixel values
    pixel_values_list = np.arange(0, 0.75, 0.75/end_length)

    # Fill the four corners
    for corner_idx in range(4):
        for idx in range(end_length):
            # pixel_values_list = np.arange(0.75, 0, 0.75 / (idx+1))
            slope_line_value = slope_line_values_list[idx] #40
            parabola_value = parabola_values_list[idx]
            end_col_idx = int(round(slope_line_value - parabola_value))
            # Top-Right
            for top_right_idx in range(end_col_idx):
                mask_image[idx, top_right_idx] = float(pixel_values_list[top_right_idx])
            # Bottom-Right
            row_num_bottom_right = row_total - idx
            for bottom_right_idx in range(col_total - end_col_idx, col_total-1):
                mask_image[row_num_bottom_right-1, bottom_right_idx] = float(pixel_values_list[-1 * (bottom_right_idx - (col_total - end_col_idx))])
            # Top-Right
            for top_right_idx in range(col_total - end_col_idx, col_total-1):
                mask_image[idx, top_right_idx] = float(pixel_values_list[-1 * (top_right_idx - (col_total - end_col_idx))])
            # Bottom-Left
            row_num_bottom_left = row_total - idx
            for bottom_left_idx in range(end_col_idx):
                mask_image[row_num_bottom_left-1, bottom_left_idx] = float(pixel_values_list[bottom_left_idx])

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
