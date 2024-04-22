from flask import Flask, render_template, request
import cv2 as cv
import math
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CAMERA_MATRIX_PATH = 'images/right/camera_matrix.txt'

def load_camera_matrix():
    # Load camera matrix from file
    camera_matrix = []
    with open(CAMERA_MATRIX_PATH, 'r') as f:
        for line in f:
            camera_matrix.append([float(num) for num in line.split()])
    return camera_matrix

def draw_measurement(image, rect_coords, line_coords, diameter_pixels):
    # Draw rectangle and line on the image
    cv.rectangle(image, rect_coords[0], rect_coords[1], (0, 255, 0), 5)
    cv.line(image, line_coords[0], line_coords[1], (0, 0, 255), 8)

    # Draw dimensions result on the image
    font = cv.FONT_HERSHEY_SIMPLEX
    text = f'Diameter: {diameter_pixels:.2f} cm'
    cv.putText(image, text, (10, 30), font, 1, (0, 0, 255), 2, cv.LINE_AA)

def calculate_diameter_in_pixels(image, camera_matrix):
    # Define rectangle and line coordinates
    rect_x, rect_y, rect_width, rect_height = 15, 16, 13, 1
    point1_x, point1_y = rect_x, rect_y
    point2_x, point2_y = rect_x + rect_width, rect_y + rect_height

    # Calculate real-world points
    Z = 320
    FX = camera_matrix[0][0]
    FY = camera_matrix[1][1]
    real_point1_x = Z * (point1_x / FX)
    real_point1_y = Z * (point1_y / FY)
    real_point2_x = Z * (point2_x / FX)
    real_point2_y = Z * (point2_y / FY)

    # Calculate diameter in pixels
    diameter_pixels = math.sqrt((real_point2_y - real_point1_y) ** 2 + (real_point2_x - real_point1_x) ** 2)
    return diameter_pixels

def process_image(image_path):
    # Load the image
    image = cv.imread(image_path)

    # Load camera matrix
    camera_matrix = load_camera_matrix()

    # Calculate diameter in pixels
    diameter_pixels = calculate_diameter_in_pixels(image, camera_matrix)

    # Draw measurements on the image
    draw_measurement(image, [(15, 16), (15 + 13, 16 + 1)], [(15, 16), (15, 16 + 1)], diameter_pixels)

    # Save the image with drawn dimensions
    result_image_path = os.path.join(UPLOAD_FOLDER, 'result_image.jpg')
    cv.imwrite(result_image_path, image)

    return diameter_pixels

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            diameter_cm = process_image(file_path)
            return render_template('result.html', diameter=diameter_cm)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)