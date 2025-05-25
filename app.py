from flask import Flask, render_template, request, jsonify,send_file,make_response
from PIL import Image, ImageOps, ImageFilter
import os
from io import BytesIO
from mimetype import mime_types

app = Flask(__name__)
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    file = request.files['image']

    if file:
        original_filename = file.filename
        name, extension = os.path.splitext(original_filename)  # name = "photo", extension = ".png"
        extension = extension.replace('.', '').lower()
        path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
        file.save(path)
        mimeType = get_mime_type_from_extension(extension)

        return jsonify({'path': path, 'filename': original_filename, 'extention':extension, "mime_type":mimeType})
    return jsonify({'error': 'No image uploaded'}), 400


def prepare_image_response(image, extension, fileName):
    save_format = extension.upper()
    if save_format == 'JPG':
        save_format = 'JPEG'

    img_io = BytesIO()
    image.save(img_io, format=save_format.upper())
    img_io.seek(0)

    mimetype = get_mime_type_from_extension(extension)

    response = make_response(send_file(
        img_io,
        mimetype=mimetype,
        as_attachment=False,
        download_name=fileName + extension
    ))
    response.headers['X-Image-Extension'] = extension
    response.headers['X-Image-fileName'] = fileName
    return response


def get_image_from_request():
    file = request.files.get('image')
    extension = request.form.get('extension')
    fileName = request.form.get('fileName')

    if not file:
        return None, None, None, "Image manquante", 400

    try:
        image = Image.open(file.stream)
    except Exception as e:
        return None, None, None, f"Erreur lors du chargement de l'image : {e}", 400

    return image, extension, fileName, None, 200


@app.route('/process/gray', methods=['POST'])
def process_greyscale():
    image, extension, fileName, error, status = get_image_from_request()
    if error:
        return error, status

    image = ImageOps.grayscale(image)
    return prepare_image_response(image, extension, fileName)


@app.route('/process/rotate', methods=['POST'])
def process_rotate():
    image, extension, fileName, error, status = get_image_from_request()
    if error:
        return error, status

    image = image.rotate(-90, expand=True)
    return prepare_image_response(image, extension, fileName)





@app.route('/process/filtre', methods=['POST'])
def filter_image():
    image, extension, fileName, error, status = get_image_from_request()
    typeFiltre = request.form.get('typeFiltre')
    if error:
        return error, status
    if typeFiltre == "invert":
        image = ImageOps.invert(image.convert("RGB"))
    
    if typeFiltre == "blur":
        image = image.filter(ImageFilter.BLUR)
    if typeFiltre == "sharpen":
        image = image.filter(ImageFilter.SHARPEN)
    if typeFiltre == "contour":
        image = image.filter(ImageFilter.CONTOUR)



    return prepare_image_response(image, extension, fileName)



def get_mime_type_from_extension(extension):
    return mime_types.get(extension.lower(), 'application/octet-stream')


if __name__ == '__main__':
    app.run(debug=True)
