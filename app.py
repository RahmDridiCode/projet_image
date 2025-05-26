from flask import Flask, render_template, request, jsonify,send_file,make_response
from PIL import Image, ImageOps, ImageFilter
import os
from io import BytesIO
from mimetype import mime_types
import matplotlib.pyplot as plt
from compression import huffman_compress, shannon_fano_compress,decode_binary_to_bytes,decode_binary_to_bytes_shanon # Import des fonctions
import ast


app = Flask(__name__)
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/')
def index():
    return render_template('index.html')
@app.route('/traitement-image')
def traitement_image():
    return render_template('traitement.html')

@app.route('/decompression-fichier')
def decompression_fichier():
    return render_template('decompression.html')

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

        return jsonify({'path': path, 'filename': original_filename, 'extention':extension, "mime_type":mimeType, "name":name})
    return jsonify({'error': 'No image uploaded'}), 400


def prepare_image_response(image, extension, fileName,new_extension=None):
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
    if new_extension:
        response.headers['X-New-Extension'] = new_extension
   
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


@app.route('/process/compress', methods=['POST'])
def compresser_image():
    image, extension, fileName, error, status = get_image_from_request()
    typecompress = request.form.get('typecompress')
    if error:
        return error, status

    if typecompress == "compress lossless":
        output = BytesIO()
        image.save(output, format="PNG", optimize=True)
        output.seek(0)
        image = Image.open(output)
        extension = "png"

    elif typecompress == "compress with loss":
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        output = BytesIO()
        image.save(output, format="JPEG", quality=70, optimize=True)
        output.seek(0)
        image = Image.open(output)
        extension = "jpg"

    return prepare_image_response(image, extension, fileName, new_extension=extension)



def get_mime_type_from_extension(extension):
    return mime_types.get(extension.lower(), 'application/octet-stream')


def get_image_bytes_from_request():
    if 'image' not in request.files:
        return None, ("Image not found in request", 400)
    file = request.files['image']
    image_bytes = file.read()
    return image_bytes, None

@app.route('/process/compress-huffman', methods=['POST'])
def compress_huffman_route():
    image_bytes, error = get_image_bytes_from_request()
    if error:
        return error

    encoded_data, code_map = huffman_compress(image_bytes)

    txt_content = f"Encoded Data:\n{encoded_data}\n\nCode Map:\n{code_map}"
    txt_io = BytesIO()
    txt_io.write(txt_content.encode())
    txt_io.seek(0)

    filename = request.form.get('fileName', 'image') + "_huffman.txt"
    return send_file(txt_io,
                     mimetype="text/plain",
                     as_attachment=True,
                     download_name=filename)

@app.route('/process/compress-shannon', methods=['POST'])
def compress_shannon_route():
    image_bytes, error = get_image_bytes_from_request()
    if error:
        return error

    encoded_data, code_map = shannon_fano_compress(image_bytes)

    txt_content = f"Encoded Data:\n{encoded_data}\n\nCode Map:\n{code_map}"
    txt_io = BytesIO()
    txt_io.write(txt_content.encode())
    txt_io.seek(0)

    filename = request.form.get('fileName', 'image') + "_shannon.txt"
    return send_file(txt_io,
                     mimetype="text/plain",
                     as_attachment=True,
                     download_name=filename)


@app.route('/process/decompress-huffman', methods=['POST'])
def decompress_huffman():
    if 'file' not in request.files:
        return "Aucun fichier envoyé", 400
    
    file = request.files['file']
    content = file.read().decode()
    encoded_data_section = content.split("Encoded Data:")[1].split("Code Map:")[0].strip()
    code_map_section = content.split("Code Map:")[1].strip()
        
    code_map = ast.literal_eval(code_map_section)  # Convert string dict to real dict

    decoded_image_bytes = decode_binary_to_bytes(encoded_data_section, code_map)

    # Charger l'image à partir des bytes décodés
    img_io = BytesIO(decoded_image_bytes)
    img_io.seek(0)
    """image = Image.open(img_io)  # Charger l'image correctement

    # Sauvegarder dans un nouveau BytesIO pour l'envoi
    output_io = BytesIO()
    image.save(output_io, format="PNG")  # Choisir le format approprié (PNG, JPEG...)
    output_io.seek(0)"""

    mimetype = "image/png"  # ou utiliser get_mime_type_from_extension si tu as la fonction
    fileName = "decompressed_image"
    extension="png"
     # Ajouter les infos dans les headers HTTP
    
    response = make_response(send_file(
        img_io,
        mimetype=mimetype,
        as_attachment=False,
        download_name=fileName +"."+ extension
    ))
    response.headers['X-MimeType'] = "image/png"
    response.headers['X-FileName'] = "decompressed_image.png"
    response.headers['X-Extension'] = "png"
    response.headers['name'] = "decompressed_image"
    return response
    
@app.route('/process/decompress-shannon', methods=['POST'])
def decompress_shannon():
    if 'file' not in request.files:
        return "Aucun fichier envoyé", 400

    file = request.files['file']
    content = file.read().decode()


    # Extraire les sections du fichier
    encoded_data_section = content.split("Encoded Data:")[1].split("Code Map:")[0].strip()
    code_map_section = content.split("Code Map:")[1].strip()

    # Recréer le dictionnaire code_map
    code_map = ast.literal_eval(code_map_section)

    # Inverser le dictionnaire pour décodage : {"010": "A", "110": "B"} → {"A": "010"} → {"010": "A"}
    
    reverse_map = {v: k for k, v in code_map.items()}

    # Décompression
    decoded_bytes = decode_binary_to_bytes_shanon(encoded_data_section, reverse_map)

    # Retourner l'image
    img_io = BytesIO(decoded_bytes)
    img_io.seek(0)
    mimetype = "image/png"  # ou utiliser get_mime_type_from_extension si tu as la fonction
    fileName = "decompressed_image"
    extension="png"
        # Ajouter les infos dans les headers HTTP
    
    response = make_response(send_file(
    img_io,
    mimetype=mimetype,
    as_attachment=False,
    download_name=fileName +"."+ extension
        ))
    response.headers['X-MimeType'] = "image/png"
    response.headers['X-FileName'] = "decompressed_image.png"
    response.headers['X-Extension'] = "png"
    response.headers['name'] = "decompressed_image"
    return response



if __name__ == '__main__':
    app.run(debug=True)

