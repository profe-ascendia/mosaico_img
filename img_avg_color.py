import os
from PIL import Image
import numpy as np

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
                rgb_color = f'rgb({avg_color[0]},{avg_color[1]},{avg_color[2]})'
                image_colors.append((filename, rgb_color))
    
    return image_colors

def find_closest_image_by_color(target_color, image_colors):
    """
    Find image with closest average color to target_color
    target_color: string 'rgb(r,g,b)'
    image_colors: list of tuples (filename, 'rgb(r,g,b)')
    """
    # Convert target_color string to RGB values
    target_rgb = [int(x) for x in target_color.strip('rgb()').split(',')]
    target_array = np.array(target_rgb)
    
    min_distance = float('inf')
    closest_image = None
    
    for filename, color in image_colors:
        # Convert color string to RGB values
        current_rgb = [int(x) for x in color.strip('rgb()').split(',')]
        current_array = np.array(current_rgb)
        
        # Calculate Euclidean distance between colors
        distance = np.sqrt(np.sum((target_array - current_array) ** 2))
        
        if distance < min_distance:
            min_distance = distance
            closest_image = filename
            
    return closest_image

# Usage example:
def main():
    colors = get_images_average_colors()
    target = 'rgb(255,0,0)'  # Looking for reddish images
    closest = find_closest_image_by_color(target, colors)
    print(f"Image with closest color to {target}: {closest}")

if __name__ == "__main__":
    main()


# def main():
#     os.makedirs(IMG_ORIGEN, exist_ok=True)
#     colors = get_images_average_colors()
#     for filename, color in colors:
#         print(f"Image: {filename} - Average Color: {color}")

# if __name__ == "__main__":
#     main()
