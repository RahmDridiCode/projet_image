let pathOriginalImage
let mimeType
let originalExtension = null;
let originalFileName = null;
let name=null

let scale = 1;
let rotation = 0;

let currentScale = 1;
const imageElement = document.getElementById('image');
const imageLabel =document.getElementById('imageNameSpan');
document.getElementById('upload').addEventListener('change', function () {   // pour le cacher
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
            name=data.name     
            histogramContainer.style.display = "none";  
            cardcar.style.display = "block";
            const btn = document.getElementById("downloadBtn");
            btn.classList.remove("disabled");
            btn.setAttribute("onclick", "downloadImage()");


          


            
        });

});



function reset(){
    imageElement.src = pathOriginalImage;
}


async function process(action) {
    const typeFiltre = document.getElementById('filterSelect').value; 
    const typecompress = document.getElementById('CompressSelect').value;
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
            formData.append('typecompress', typecompress);


            const response = await fetch(`/process/${action}`, {
                method: 'POST',
                body: formData
            });

            const resultBlob = await response.blob();
            imageElement.src = URL.createObjectURL(resultBlob);
            const newExtension = response.headers.get('X-New-Extension') || originalExtension;

            if (newExtension != originalExtension){
                imageLabel.textContent = name +"." + newExtension;
                originalExtension = newExtension

            }


              
        }, mimeType);
    };

    img.src = imageElement.src;
}


async function compressAsText(method) {
   

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
            formData.append('fileName', originalFileName);
        




            const response = await fetch(`/process/compress-${method}`, {
                method: 'POST',
                body: formData
            });
            if (!response.ok) {
                alert('Erreur lors de la compression');
                return;
            }

            const blobResponse = await response.blob();
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blobResponse);
            link.download = originalFileName + "_" + method + ".txt";
            link.click();



        }, mimeType);
    };

    img.src = imageElement.src;
}

/*
function coderFile(type) {
    const input = document.getElementById("fileInput");
    const selectedFile = input.files[0];

    if (!selectedFile) {
        alert("Veuillez sélectionner un fichier .txt à décompresser.");
        return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);  // Le fichier .txt à décompresser

    fetch(`/process/decompress-huffman/${type}`, {
        method: "POST",
        body: formData
    })
        .then(response => {
            if (!response.ok) throw new Error("Échec de la décompression");
            return response.blob();
        })
        .then(blob => {
            const url = URL.createObjectURL(blob);
            // 🔁 Afficher l'image dans une balise <img>
            imageElement.src = url;
        })
        .catch(err => {
            alert("Erreur : " + err.message);
        });
}

*/


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


function showHistogram() {
    if (!imageElement.src) {
        alert("Veuillez d'abord télécharger une image.");
        return;
    }

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    img.crossOrigin = "anonymous";

    img.onload = function () {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);

        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;

        // Histogramme sur 256 niveaux
        const histogramR = new Array(256).fill(0);
        const histogramG = new Array(256).fill(0);
        const histogramB = new Array(256).fill(0);

        for (let i = 0; i < data.length; i += 4) {
            histogramR[data[i]]++;
            histogramG[data[i + 1]]++;
            histogramB[data[i + 2]]++;
        }

        // Trouver la valeur max pour normaliser
        const maxCount = Math.max(
            ...histogramR,
            ...histogramG,
            ...histogramB
        );

        // Dimensions de l'histogramme
        const histWidth = 512;   // largeur plus grande (agrandie)
        const histHeight = 200;
        const marginTop = 30;
        const marginLeft = 50;
        const marginBottom = 50;

        // Canvas pour l'histogramme + fond agrandi
        const histCanvas = document.createElement('canvas');
        histCanvas.width = histWidth + marginLeft + 20;
        histCanvas.height = histHeight + marginTop + marginBottom;
        const histCtx = histCanvas.getContext('2d');

        // Fond agrandi clair
        histCtx.fillStyle = "#f0f0f0";
        histCtx.fillRect(0, 0, histCanvas.width, histCanvas.height);

        // Dessiner axes
        histCtx.strokeStyle = "#333";
        histCtx.lineWidth = 1;
        histCtx.beginPath();
        // axe vertical
        histCtx.moveTo(marginLeft, marginTop);
        histCtx.lineTo(marginLeft, histHeight + marginTop);
        // axe horizontal
        histCtx.lineTo(histWidth + marginLeft, histHeight + marginTop);
        histCtx.stroke();

        // Dessiner histogramme
        const barWidth = histWidth / 256;

        for (let i = 0; i < 256; i++) {
            const scaleFactor = 15; // augmente la hauteur, ajuste à ton goût

            const rHeight = Math.min((histogramR[i] / maxCount) * histHeight * scaleFactor, histHeight);
            const gHeight = Math.min((histogramG[i] / maxCount) * histHeight * scaleFactor, histHeight);
            const bHeight = Math.min((histogramB[i] / maxCount) * histHeight * scaleFactor, histHeight);


            // Rouge
            histCtx.fillStyle = 'rgba(255,0,0,0.5)';
            histCtx.fillRect(marginLeft + i * barWidth, histHeight + marginTop - rHeight, barWidth / 3, rHeight);

            // Vert
            histCtx.fillStyle = 'rgba(0,255,0,0.5)';
            histCtx.fillRect(marginLeft + i * barWidth + barWidth / 3, histHeight + marginTop - gHeight, barWidth / 3, gHeight);

            // Bleu
            histCtx.fillStyle = 'rgba(0,0,255,0.5)';
            histCtx.fillRect(marginLeft + i * barWidth + 2 * barWidth / 3, histHeight + marginTop - bHeight, barWidth / 3, bHeight);
        }

        // Ajouter les labels pour chaque couleur
        histCtx.font = '16px Arial';
        histCtx.fillStyle = 'red';
        histCtx.fillText('Rouge', marginLeft + 10, marginTop - 10);
        histCtx.fillStyle = 'green';
        histCtx.fillText('Vert', marginLeft + 100, marginTop - 10);
        histCtx.fillStyle = 'blue';
        histCtx.fillText('Bleu', marginLeft + 170, marginTop - 10);
        

        // Afficher le canvas dans la page
        const histogramImage = document.getElementById('histogram');
        histogramImage.src = histCanvas.toDataURL();
        histogramImage.classList.add('histogram-style');
        histogramContainer.style.display="block";
         // pour l’afficher
    };

    img.src = imageElement.src;
}
document.getElementById("fileInput").addEventListener('change', function () {
    document.querySelectorAll(".decompress").forEach(el => el.disabled = false);
})

function coderFile(type) {
    const input = document.getElementById("fileInput");
    const selectedFile = input.files[0];
  // pour le cacher
        const formData1 = new FormData();
    formData1.append("image", input.files[0]);

    if (!selectedFile) {
        alert("Veuillez sélectionner un fichier .txt à décompresser.");
        return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);  // Le fichier .txt à décompresser

    fetch(`/process/${type}`, {
        method: "POST",
        body: formData
    })
        .then(response => {
            if (!response.ok) throw new Error("Échec de la décompression");
               mimeType = response.headers.get('X-MimeType');
               originalFileName = response.headers.get('X-FileName');
               originalExtension = response.headers.get('X-Extension');
               name = response.headers.get('name');
               imageLabel.textContent = originalFileName;
            return response.blob();
        })
        .then(blob => {
            const url = URL.createObjectURL(blob);
            // 🔁 Afficher l'image dans une balise <img>
            imageElement.src = url;
            cardcar.style.display = "block" 
            document.querySelectorAll('button, select').forEach(el => el.disabled = false);
            histogramContainer.style.display = "none"; 
            cardcar.style.display = "block";
            const btn = document.getElementById("downloadBtn");
            btn.classList.remove("disabled");
            btn.setAttribute("onclick", "downloadImage()");

            
            
            
        })
        .catch(err => {
            alert("Erreur : " + err.message);
        });
}


function downloadImage() {
    
    const url = imageElement.src;

    const a = document.createElement("a");
    a.href = url;
    a.download = imageLabel.textContent || "image.png"; // nom du fichier
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

  

/*
function changeExtention(){
    const returnedExtension = response.headers.get('X-Image-Extension');
    const returnedFileName = response.headers.get('X-Image-fileName');
    document.getElementById('imageNameSpan').textContent = returnedFileName + returnedExtension;
}*/
