
// Add event listener when page loads
document.addEventListener('DOMContentLoaded', function () {
    const mosaicCheckbox = document.getElementById('show_mosaic');
    if (mosaicCheckbox) {
        mosaicCheckbox.addEventListener('change', toggleMosaic);
    }
});
function toggleGrid() {
    const gridOverlay = document.getElementById('grid-overlay');
    gridOverlay.style.display = document.getElementById('show_grid').checked ? 'grid' : 'none';
}

// function toggleMosaic() {
//     const mosaicOverlay = document.getElementById('mosaic-overlay');
//     mosaicOverlay.style.display = document.getElementById('show_mosaic').checked ? 'grid' : 'none';

// }
function toggleMosaic() {
    const mosaicOverlay = document.getElementById('mosaic-overlay');
    const showMosaic = document.getElementById('show_mosaic').checked;

    if (mosaicOverlay) {
        mosaicOverlay.style.display = showMosaic ? 'grid' : 'none';
    }
}



document.getElementById('mosaic-form').onsubmit = function (e) {
    e.preventDefault();

    const formData = new FormData(this);

    fetch('/create_image_mosaic', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.mosaic_path) {
                document.getElementById('mosaic-result').style.display = 'block';
                document.getElementById('mosaic-image').src = data.mosaic_path;
            }
        });
}  