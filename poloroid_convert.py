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

    def main(self):

        # self.filter_type = filter_name
        # self.write_text = txt_to_write

        printed_image = self.convert_an_image()

        if len(printed_image) == 1:
            output_file_name = "Your picture does not match the desired formats of this program. It needs to be either:\n"
            printed_image = "1.Portrait with ratio of 1.3\n 2.Landspace with ratio of 0.75 \n 3.Square with ratio of 1"
        else:
            current_datetime = datetime.datetime.now()
            unique_file_time = current_datetime.strftime("%Y_%m_%d_%H%M%S")
            output_file_name = self.image_filename.rsplit('.', 1)[0] + '_polaroid_' + unique_file_time + '.jpg'
            printed_image = printed_image

        return output_file_name, printed_image

    def rotate_an_image(self, image_to_rotate):
        rows = image_to_rotate.shape[0]
        columns = image_to_rotate.shape[1]
        M = cv2.getRotationMatrix2D((columns / 2, rows / 2), 90, 1)
        final_rotated_image = cv2.warpAffine(image_to_rotate, M, (columns, rows))

        return final_rotated_image

    def smooth_an_image(self, kernel_value):
        smooth_image = cv2.GaussianBlur(self.image, (kernel_value, kernel_value), 0)

        return smooth_image

    def _get_text_coordinates(self, total_rows, bottom_padding, left_padding, total_columns):
        y = total_rows - ((bottom_padding - 50)/2)
        x = left_padding + ((total_columns - (len(self.write_text) * 47)) / 2)
        origin = (x, y)

        return origin

    def convert_an_image(self):
        # Apply slight blur to smooth the image
        # smooth_image_1 = self.smooth_an_image(kernel_value=5)

        filter_type = getattr(filters, self.filter_type)
        smooth_image = filter_type(self.image)

        if round(self.image_ratio, 1) == 1.3:
            # Resize image to portrait polaroid size
            resize_image = cv2.resize(smooth_image,
                                      (int(73.0 / self.inch_to_mm * self.inch_to_pixel), int(96.0 / self.inch_to_mm * self.inch_to_pixel)),
                                      interpolation=cv2.INTER_AREA)
            # Create temporary image border to pad to make whole image a square. First step in rotation so corners don't cutoff
            temp_image_border = cv2.copyMakeBorder(resize_image, top=70, bottom=215, left=278, right=278, borderType=cv2.BORDER_CONSTANT,
                                                   value=(255, 255, 255, 255))
            bottom_padding = 1467 - (70 + resize_image.shape[0])
            total_rows = 1467
            total_columns = resize_image.shape[1]
            # left_padding = 1200 - (268 + total_columns)
            left_padding = 278
            origin = self._get_text_coordinates(total_rows, bottom_padding, left_padding, total_columns)

            cv2.putText(temp_image_border, self.write_text, origin, fontFace=cv2.FONT_HERSHEY_PLAIN,
                        fontScale=5,
                        color=(0, 0, 0), thickness=2)

            # Get padded image dimensions and rotate it 90 degrees counter clockwise about the center
            rotated_image = self.rotate_an_image(temp_image_border)

            # Add border along the length to make image 6 inches. Cut image from the width to 4 inches. Creates 4 by 6 image
            image_length_full = cv2.copyMakeBorder(rotated_image, 0, 0, 0, 382, cv2.BORDER_CONSTANT,
                                                   value=(255, 255, 255, 255))
            printsize_image = image_length_full[10:1210, :]

            # Draw two lines at the points where to cut the image to make a polaroid
            cv2.line(printsize_image, (0, 198), (1800, 198), color=0, thickness=1, lineType=4)
            cv2.line(printsize_image, (1467, 0), (1467, 1200), color=0, thickness=1, lineType=4)

        # If image is Square, follow square final image creation
        elif round(self.image_ratio, 1) == 1.0:
            # Resize image to portrait polaroid size
            resize_image = cv2.resize(smooth_image, (int(3.1 * self.inch_to_pixel), int(3.1 * self.inch_to_pixel)),
                                      interpolation=cv2.INTER_AREA)
            # Create temporary image border to pad to make whole image a square. First step in rotation so corners don't cutoff
            temp_image_border = cv2.copyMakeBorder(resize_image, 60, 270, 120, 210, cv2.BORDER_CONSTANT,
                                                   value=(255, 255, 255, 255))
            bottom_padding = 1260 - (60 + resize_image.shape[0])
            total_rows = 1260
            total_columns = resize_image.shape[1]
            left_padding = 120
            origin = self._get_text_coordinates(total_rows, bottom_padding, left_padding, total_columns)

            cv2.putText(temp_image_border, self.write_text, origin, fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=5,
                        color=(0, 0, 0), thickness=2)

            # Get padded image dimensions and rotate it 90 degrees counter clockwise about the center
            rotate_image = self.rotate_an_image(temp_image_border)

            # Add border along the length to make image 6 inches. Cut image from the width to 4 inches. Creates 4 by 6 image
            image_length_full = cv2.copyMakeBorder(rotate_image, 0, 0, 0, 540, cv2.BORDER_CONSTANT,
                                                   value=(255, 255, 255, 255))
            printsize_image = image_length_full[0:1200, :]

            # Draw two lines at points where to cut the image to make a polaroid
            cv2.line(printsize_image, (0, 150), (1800, 150), color=0, thickness=1, lineType=4)
            cv2.line(printsize_image, (1260, 0), (1260, 1200), color=0, thickness=1, lineType=4)

        # If Image is landscape follow landscape orientation
        elif 0.7 <= round(self.image_ratio, 1) <= 0.8:
            # Resize image to portrait polaroid size
            resize_image = cv2.resize(smooth_image, (int(99 / self.inch_to_mm * self.inch_to_pixel), int(math.ceil(62 / self.inch_to_mm * self.inch_to_pixel))), interpolation=cv2.INTER_AREA)

            # Add border to make it 4 by 6 image AND give polaroid borders
            printsize_image = cv2.copyMakeBorder(resize_image, 288, 180, 53, 577, cv2.BORDER_CONSTANT,
                                                 value=(255, 255, 255, 255))

            bottom_padding = 180
            total_rows = 1200
            total_columns = resize_image.shape[1]
            left_padding = 53
            origin = self._get_text_coordinates(total_rows, bottom_padding, left_padding, total_columns)

            cv2.putText(printsize_image, self.write_text, origin, fontFace=cv2.FONT_HERSHEY_PLAIN,
                        fontScale=5,
                        color=(0, 0, 0), thickness=2)

            # Draw lines at points where to cut the image to make a polaroid
            cv2.line(printsize_image, (0, 228), (1800, 228), color=0, thickness=1, lineType=4)
            cv2.line(printsize_image, (1276, 0), (1276, 1200), color=0, thickness=1, lineType=4)
        else:
            printsize_image = [0]

        return printsize_image

