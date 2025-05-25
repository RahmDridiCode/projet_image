let pathOriginalImage
let mimeType
let originalExtension = null;
let originalFileName = null;

let scale = 1;
let rotation = 0;

let currentScale = 1;
const imageElement = document.getElementById('image');
const imageLabel =document.getElementById('imageNameSpan');
document.getElementById('upload').addEventListener('change', function () {
    const formData = new FormData();
    formData.append("image", this.files[0]);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            imageElement.src = data.path;

            document.querySelectorAll('button, select').forEach(el => el.disabled = false);
            pathOriginalImage = data.path
            mimeType = data.mime_type
            originalFileName = data.filename
            originalExtension = data.extention
            imageLabel.textContent = originalFileName;
        });
});



function reset(){
    imageElement.src = pathOriginalImage;
}


async function process(action) {
    const typeFiltre = document.getElementById('filterSelect').value; 
    const isBlob = imageElement.src.startsWith("blob:");


    // Créer le canvas
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    img.crossOrigin = "anonymous";

    img.onload = async function () {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);

        // Définir l'extension et le nom de fichier si c’est le premier traitement

        if (!mimeType) {
            alert("Format non supporté !");
            return;
        }

        canvas.toBlob(async function (blob) {
            const formData = new FormData();
            formData.append('image', blob, 'image' + originalExtension);
            formData.append('action', action);
            formData.append('extension', originalExtension);
            formData.append('fileName', originalFileName);
            formData.append('pathOriginalImage', pathOriginalImage);
            formData.append('typeFiltre', typeFiltre);

            const response = await fetch(`/process/${action}`, {
                method: 'POST',
                body: formData
            });

            const resultBlob = await response.blob();
            imageElement.src = URL.createObjectURL(resultBlob);
        }, mimeType);
    };

    img.src = imageElement.src;
}


function zoomIn() {
    currentScale += 0.1; // augmenter le zoom
    updateImageScale();
}

function zoomOut() {
    currentScale = Math.max(0.1, currentScale - 0.1); // diminuer mais pas en dessous de 0.1
    updateImageScale();
}

function updateImageScale() {
    imageElement.style.transform = `scale(${currentScale})`;
    imageElement.style.transition = 'transform 0.3s ease'; // animation fluide
}

/*
function changeExtention(){
    const returnedExtension = response.headers.get('X-Image-Extension');
    const returnedFileName = response.headers.get('X-Image-fileName');
    document.getElementById('imageNameSpan').textContent = returnedFileName + returnedExtension;
}*/
