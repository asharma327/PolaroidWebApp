import cv2
import numpy as np

import os
import errno

from os import path
from glob import glob

import blend_functions as a6

def viz_pyramid(pyramid):
    """Create a single image by vertically stacking the levels of a pyramid."""
    shape = np.atleast_3d(pyramid[0]).shape[:-1]  # need num rows & cols only
    img_stack = [cv2.resize(layer, shape[::-1],
                            interpolation=3) for layer in pyramid]
    return np.vstack(img_stack).astype(np.uint8)


def run_blend(black_image, white_image, mask):
    """Compute the blend of two images along the boundaries of the mask.

    Assume all images are float dtype, and return a float dtype.
    """

    # Automatically figure out the size; at least 16x16 at the highest level
    min_size = min(black_image.shape)
    depth = int(np.log2(min_size)) - 4

    gauss_pyr_mask = a6.gaussPyramid(mask, depth)
    gauss_pyr_black = a6.gaussPyramid(black_image, depth)
    gauss_pyr_white = a6.gaussPyramid(white_image, depth)

    lapl_pyr_black = a6.laplPyramid(gauss_pyr_black)
    lapl_pyr_white = a6.laplPyramid(gauss_pyr_white)

    outpyr = a6.blend(lapl_pyr_white, lapl_pyr_black, gauss_pyr_mask)
    img = a6.collapse(outpyr)

    return (gauss_pyr_black, gauss_pyr_white, gauss_pyr_mask,
            lapl_pyr_black, lapl_pyr_white, outpyr, [img])


def blend_two_images(black_image, white_image, mask):
    """Apply pyramid blending to each color channel of the input images """

    # Convert to double and normalize the images to the range [0..1]
    # to avoid arithmetic overflow issues
    b_img = np.atleast_3d(black_image).astype(np.float) / 255.
    w_img = np.atleast_3d(white_image).astype(np.float) / 255.
    m_img = np.atleast_3d(mask).astype(np.float) / 255.
    num_channels = b_img.shape[-1]

    imgs = []
    for channel in range(num_channels):
        imgs.append(run_blend(b_img[:, :, channel],
                              w_img[:, :, channel],
                              m_img[:, :, channel]))

    names = ['gauss_pyr_black', 'gauss_pyr_white', 'gauss_pyr_mask',
             'lapl_pyr_black', 'lapl_pyr_white', 'outpyr', 'outimg']

    final_images = {}
    for name, img_stack in zip(names, zip(*imgs)):
        imgs = map(np.dstack, zip(*img_stack))
        stack = [cv2.normalize(img, alpha=0, beta=255,
                               norm_type=cv2.NORM_MINMAX)
                 for img in imgs]
        final_images[name] = viz_pyramid(stack)

    final_image = final_images['outimg']

    return final_image

