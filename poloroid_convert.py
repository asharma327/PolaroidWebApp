import numpy as np
import cv2
import math
import os
import filters
import datetime


class imageConvert():

    def __init__(self, image_file):
        self.image = cv2.imread(os.path.join(os.getcwd() + '/uploads', image_file))
        self.image_filename = image_file
        # Image Length
        self.rows = self.image.shape[0]
        # Image Width
        self.columns = self.image.shape[1]
        self.shape = self.image.shape
        self.inch_to_pixel = 300
        self.inch_to_mm = 25.4
        self.image_ratio = float(self.rows)/float(self.columns)
        self.filter_type = None
        self.write_text = None
        self.resize_image_dir = {'portrait': [int(73.0/self.inch_to_mm * self.inch_to_pixel),
                                              int(96.0/self.inch_to_mm * self.inch_to_pixel)],
                                 'square': [int(3.1 * self.inch_to_pixel),
                                            int(3.1 * self.inch_to_pixel)]}
        self.rotation_pad_sizes = {'portrait': [70, 215, 278, 278], 'square': [60, 270, 120, 210]}
        self.put_text_params = {'portrait': [1467, 1467 - (70 + 1133), 278, 862],
                                'square': [1260, 1260 - (60 + 930), 120, 930],
                                'landscape': [1200, 180, 53, 1169]}
        self.four_by_six_pad_size = {'portrait': 382, 'square': 540}
        self.cutoff_line_points = {'portrait': [[(0, 198), (1800, 198)], [(1467, 0), (1467, 1200)]],
                                   'square': [[(0, 150), (1800, 150)], [(1260, 0), (1260, 1200)]]}
        self.final_crop_lengths = {'portrait': [0, 1210], 'square': [0, 1200]}

    def rotate_an_image(self, image_to_rotate):
        rows = image_to_rotate.shape[0]
        columns = image_to_rotate.shape[1]
        M = cv2.getRotationMatrix2D((columns / 2, rows / 2), 90, 1)
        final_rotated_image = cv2.warpAffine(image_to_rotate, M, (columns, rows))

        return final_rotated_image

    def _get_text_coordinates(self, total_rows, bottom_padding, left_padding, total_columns):
        y = total_rows - ((bottom_padding - 50)/2)
        x = left_padding + ((total_columns - (len(self.write_text) * 47)) / 2)
        origin = (x, y)

        return origin

    def square_portrait_image_conversion(self, smooth_image, image_type):
        # Resize image to polaroid dimensions
        resize_image = cv2.resize(smooth_image, ((self.resize_image_dir[image_type][0]), self.resize_image_dir[image_type][1]),
                                  interpolation=cv2.INTER_AREA)
        print resize_image.shape[0]
        # Create temporary image border to pad to make whole image a square
        # First step in rotation so corners don't cutoff
        temp_image_border = cv2.copyMakeBorder(resize_image, top=self.rotation_pad_sizes[image_type][0],
                                               bottom=self.rotation_pad_sizes[image_type][1],
                                               left=self.rotation_pad_sizes[image_type][2],
                                               right=self.rotation_pad_sizes[image_type][3],
                                               borderType=cv2.BORDER_CONSTANT,
                                               value=(255, 255, 255, 255))

        # Get text origin
        origin = self._get_text_coordinates(total_rows=self.put_text_params[image_type][0],
                                            bottom_padding=self.put_text_params[image_type][1],
                                            left_padding=self.put_text_params[image_type][2],
                                            total_columns=self.put_text_params[image_type][3])

        # Write Text on Image
        cv2.putText(temp_image_border, self.write_text, origin, fontFace=cv2.FONT_HERSHEY_PLAIN,
                    fontScale=5, color=(0, 0, 0), thickness=2)

        # Rotate padded image 90 degrees counter clockwise about the center
        rotated_image = self.rotate_an_image(temp_image_border)

        # Add border along the length to make image 6 inches
        image_length_full = cv2.copyMakeBorder(rotated_image, 0, 0, 0, self.four_by_six_pad_size[image_type],
                                               cv2.BORDER_CONSTANT,
                                               value=(255, 255, 255, 255))
        # Cut image from the width to 4 inches. Creates 4 by 6 image
        printsize_image = image_length_full[
                          self.final_crop_lengths[image_type][0]:self.final_crop_lengths[image_type][1], :]

        # Draw two lines at the points where to cut the image to make a polaroid
        cv2.line(printsize_image, self.cutoff_line_points[image_type][0][0], self.cutoff_line_points[image_type][0][1],
                 color=0, thickness=1, lineType=4)
        cv2.line(printsize_image, self.cutoff_line_points[image_type][1][0], self.cutoff_line_points[image_type][1][1],
                 color=0, thickness=1, lineType=4)

        return printsize_image

    def convert_an_image(self):
        # Call function from filters.py file that matches filter selected by user in web-app interface
        filter_type = getattr(filters, self.filter_type)
        # Apply filter to input image
        smooth_image = filter_type(self.image)

        # If image is Portrait, follow portrait image creation
        if round(self.image_ratio, 1) == 1.3:
            image_type = 'portrait'
            printsize_image = self.square_portrait_image_conversion(smooth_image, image_type)

        # If image is Square, follow square final image creation
        elif round(self.image_ratio, 1) == 1.0:
            image_type = 'square'
            printsize_image = self.square_portrait_image_conversion(smooth_image, image_type)

        # If Image is landscape follow landscape orientation
        elif 0.7 <= round(self.image_ratio, 1) <= 0.8:
            image_type = 'landscape'
            # Resize image to landscape polaroid size
            resize_image = cv2.resize(smooth_image, (int(99 / self.inch_to_mm * self.inch_to_pixel),
                                                     int(math.ceil(62 / self.inch_to_mm * self.inch_to_pixel))),
                                      interpolation=cv2.INTER_AREA)
            # Add border to make it 4 by 6 image AND give polaroid borders
            printsize_image = cv2.copyMakeBorder(resize_image,
                                                 top=288,bottom=180, left=53, right=577,
                                                 borderType=cv2.BORDER_CONSTANT,
                                                 value=(255, 255, 255, 255))
            # Determine origin point to place text
            origin = self._get_text_coordinates(total_rows=self.put_text_params[image_type][0],
                                                bottom_padding=self.put_text_params[image_type][1],
                                                left_padding=self.put_text_params[image_type][2],
                                                total_columns=self.put_text_params[image_type][3])
            # Write text on pictures
            cv2.putText(printsize_image, self.write_text, origin, fontFace=cv2.FONT_HERSHEY_PLAIN,
                        fontScale=5,
                        color=(0, 0, 0), thickness=2)

            # Draw lines at points where to cut the image to make a polaroid
            cv2.line(printsize_image, (0, 228), (1800, 228), color=0, thickness=1, lineType=4)
            cv2.line(printsize_image, (1276, 0), (1276, 1200), color=0, thickness=1, lineType=4)
        else:
            printsize_image = [0]

        return printsize_image

    def main(self):

        printed_image = self.convert_an_image()

        print self.image_ratio

        if len(printed_image) == 1:
            output_file_name = "Error"
            printed_image = "Error"
        else:
            current_datetime = datetime.datetime.now()
            unique_file_time = current_datetime.strftime("%Y_%m_%d_%H%M%S")
            output_file_name = self.image_filename.rsplit('.', 1)[0] + '_polaroid_' + unique_file_time + '.jpg'
            printed_image = printed_image

        return output_file_name, printed_image

