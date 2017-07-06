import os
import poloroid_convert
import numpy as np
import cv2
import math
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the picture extensions that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'tiff', 'bmp', 'jpeg', 'JPG', 'PNG', 'JPEG', 'BMP'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
@app.route('/index')
def index():
    # If user has selected a radio button, return its values
    if request.method == 'POST':
        selectedValue = request.form['option']
        return selectedValue
    return render_template('index.html')

# Route that will process the file upload, filter selection, text input and image conversion
@app.route('/upload', methods=['POST'])
def upload():
    # Get uploads directory path
    upload_path = os.getcwd() + '/uploads'
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup if it doesn't exist yet
        files_in_upload_folder = os.listdir(upload_path)
        # Only save file if it does not exist
        if filename not in files_in_upload_folder:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Create an image object from its filename
        image = poloroid_convert.imageConvert(filename)
        # Set the filter type to what the user has selected
        image.filter_type = request.form['filters']
        # Set the caption to the user input
        image.write_text = request.form['caption']
        # Convert the image and return the file name and converted image
        polaroid_file_name, polaroid_image = image.main()
        # Render the error message template if polaroid_image is a string
        # We return a string for a failed conversion
        if str(polaroid_image) == polaroid_image:
            return render_template('error_message.html')
        else:
            # If conversion is successful,save the converted file to user desktop and display converted image in browser
            cv2.imwrite(os.path.join(os.path.expanduser('~'), 'Desktop/' + polaroid_file_name), polaroid_image)
            cv2.imwrite(os.path.join(upload_path, polaroid_file_name), polaroid_image)
            return redirect(url_for('uploaded_file', filename=polaroid_file_name))

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to show after the upload
@app.route('/uploads/<filename>', methods=['GET', 'POST'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == '__main__':
    app.run(
        debug=True
    )
