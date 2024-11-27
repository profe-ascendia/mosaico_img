from flask_wtf.csrf import CSRFProtect

from flask import Flask, render_template, request, redirect, jsonify,send_from_directory
import os
from PIL import Image
import numpy as np
# #########################################
import cProfile
import pstats
import io
from functools import wraps

def profile(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            return profile.runcall(func, *args, **kwargs)
        finally:
            ps = pstats.Stats(profile)
            ps.sort_stats('cumulative')
            ps.print_stats()
    return wrapper
# #########################################



app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Add a secret key
csrf = CSRFProtect(app)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

IMG_ORIGEN = '/home/teo/mi_python/mosaico_img/static/img_procesadas'

def get_images_average_colors():
    image_colors = []
    
    for filename in os.listdir(IMG_ORIGEN):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(IMG_ORIGEN, filename)
            
            with Image.open(image_path) as img:
                img = img.convert('RGB')
                img_array = np.array(img)
                avg_color = np.mean(img_array, axis=(0,1)).astype(int)
                #rgb_color = f'rgb({avg_color[0]},{avg_color[1]},{avg_color[2]})'
                rgb_color = [avg_color[0].item(),avg_color[1].item(),avg_color[2].item()]
                image_colors.append((filename, rgb_color))
    
    return image_colors


def find_closest_image_by_color(target_color, image_colors):
    """
    Find image with closest average color to target_color using efficient vectorized operations
    """
    # Convert colors to numpy array directly from image_colors
    colors = np.array([item[1] for item in image_colors])
    
    # Calculate Euclidean distances in one vectorized operation
    distances = np.linalg.norm(colors - target_color, axis=1)
    
    # Get the filename of the closest match
    return image_colors[np.argmin(distances)][0]


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = 'current_image.jpg'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Always calculate average_colors
            average_colors = calculate_average_colors(filepath)
            grid_size=range(len(average_colors))
            
            return render_template('index.html', 
                                image_path=f'uploads/{filename}',
                                average_colors=average_colors,
                                grid_size=grid_size)
    
    # For GET requests, pass empty list instead of None
    return render_template('index.html', average_colors=[])



def calculate_average_colors(image_path, cell_size=20):
    # Open and convert image to RGB
    img = Image.open(image_path)
    img = img.convert('RGB')
    width, height = img.size
    
    # Calculate grid dimensions
    grid_cols = width // cell_size
    grid_rows = height // cell_size
    
    # Convert to numpy array
    img_array = np.array(img)
    average_colors = []
    
    # Process each row
    for i in range(grid_rows):
        row_colors = []
        y_start = i * cell_size
        y_end = min((i + 1) * cell_size, height)
        
        # Process each column
        for j in range(grid_cols):
            x_start = j * cell_size
            x_end = min((j + 1) * cell_size, width)
            
            # Extract cell and calculate average color
            cell = img_array[y_start:y_end, x_start:x_end]
            avg_color = np.mean(cell, axis=(0,1)).astype(int)
            row_colors.append([avg_color[0].item(),avg_color[1].item(),avg_color[2].item()])
        
        average_colors.append(row_colors)
    
    return average_colors


   
# Add this new route
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)




@app.route('/create_image_mosaic', methods=['POST'])
def create_image_mosaic():
    pr = cProfile.Profile()
    pr.enable()
    # Get original image dimensions once
    with Image.open(os.path.join(app.config['UPLOAD_FOLDER'], 'current_image.jpg')) as img:
        width, height = img.size
        
    # Pre-calculate all image colors at once
    image_colors = get_images_average_colors()
    color_arrays = np.array([color for _, color in image_colors])
    
    # Calculate average colors for all cells at once
    average_colors = calculate_average_colors(os.path.join(app.config['UPLOAD_FOLDER'], 'current_image.jpg'))
    
    # Create new image
    mosaic = Image.new('RGB', (width, height))
    cell_width = width // len(average_colors[0])
    cell_height = height // len(average_colors)
    
    # Pre-load and resize all source images
    source_images = {}
    for filename, _ in image_colors:
        img_path = os.path.join(IMG_ORIGEN, filename)
        with Image.open(img_path) as img:
            source_images[filename] = img.resize((cell_width, cell_height))
    
    # Process grid cells
    for i, row in enumerate(average_colors):
        for j, color in enumerate(row):
            closest_image = find_closest_image_by_color(color, image_colors)
            mosaic.paste(source_images[closest_image], (j * cell_width, i * cell_height))
    
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'mosaic_result.jpg')
    mosaic.save(output_path)
    
    # #######################

    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    
    print('Profiling Results:')
    print(s.getvalue())
    # #######################

    return jsonify({'mosaic_path': 'uploads/mosaic_result.jpg'})



if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
