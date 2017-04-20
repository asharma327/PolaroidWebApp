import numpy as np
import scipy as sp
import scipy.signal  # one option for a 2D convolution library
import cv2


def generatingKernel(a):
    """Return a 5x5 generating kernel based on an input parameter."""
    # DO NOT CHANGE THE CODE IN THIS FUNCTION
    kernel = np.array([0.25 - a / 2.0, 0.25, a, 0.25, 0.25 - a / 2.0])
    return np.outer(kernel, kernel)


def reduce_layer(image, kernel=generatingKernel(0.4)):
    """Convolve the input image with a generating kernel of parameter of 0.4
    and then reduce its width and height each by a factor of two."""

    image = np.array(image, dtype=np.float64)

    convolve = cv2.filter2D(image, -1, kernel=kernel, borderType=cv2.BORDER_REFLECT)

    final_image = np.array(convolve[::2, ::2], dtype=np.float64)

    return final_image


def expand_layer(image, kernel=generatingKernel(0.4)):
    """Upsample the image to double the row and column dimensions, and then
    convolve it with a generating kernel of a=0.4."""

    double_image = np.zeros((image.shape[0] * 2, image.shape[1]*2), dtype=np.float64)

    image = np.array(image, dtype=np.float64)

    double_image[::2, ::2] = image

    final_image = cv2.filter2D(double_image, -1, kernel=kernel, borderType=cv2.BORDER_REFLECT)

    valid_image = final_image * 4

    return valid_image


def gaussPyramid(image, levels):
    """Construct a pyramid from the image by reducing it by the number of
    levels passed in by the input."""

    g_pyr = []

    for idx in xrange(0, levels+1):
        image = np.array(image, dtype=np.float64)
        g_pyr.append(image)
        image = reduce_layer(image, kernel=generatingKernel(0.4))

    return g_pyr


def laplPyramid(gaussPyr):
    """Construct a Laplacian pyramid from a Gaussian pyramid; the constructed
    pyramid will have the same number of levels as the input."""

    l_pyr = []

    img_start = gaussPyr[-1]

    for image_idx in range(0, len(gaussPyr)-1):
        img_2 = expand_layer(gaussPyr[image_idx+1])
        img_1 = gaussPyr[image_idx]
        img_2_final = np.copy(img_2[0: img_1.shape[0], 0:img_1.shape[1]])
        img_diff = img_1 - img_2_final
        l_pyr.append(img_diff)

    l_pyr.append(img_start)

    return l_pyr


def blend(laplPyrWhite, laplPyrBlack, gaussPyrMask):
    """Blend two laplacian pyramids by weighting them with a gaussian mask."""

    final_list = []

    for img_idx in range(len(laplPyrWhite)):
        final_image = laplPyrWhite[img_idx] * gaussPyrMask[img_idx] + ((1 - gaussPyrMask[img_idx]) * laplPyrBlack[img_idx])
        final_list.append(final_image)

    return final_list


def collapse(pyramid):
    """Collapse an input pyramid."""

    reverse_pyramid = pyramid[::-1]

    for idx in range(len(reverse_pyramid)-1):
        small_image_expand = expand_layer(reverse_pyramid[idx], kernel=generatingKernel(0.4))
        next_image = reverse_pyramid[idx+1]
        if small_image_expand.shape == next_image.shape:
            reverse_pyramid[idx+1] = small_image_expand + next_image
        else:
            reverse_pyramid[idx+1] = next_image + small_image_expand[0:next_image.shape[0], 0:next_image.shape[1]]

    final_image = reverse_pyramid[-1]

    return final_image
