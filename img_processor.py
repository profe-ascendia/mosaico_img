
"""
Esta función toma las imágenes de la carpeta de origen, las redimensiona y 
las guarda en la carpeta de destino.
"""
import os
from PIL import Image

CARPETA_ORIGEN = '/home/teo/mi_python/mosaico_img/static/img_originales'
CARPETA_DESTINO = '/home/teo/mi_python/mosaico_img/static/img_procesadas'
ANCHO = 100
ALTO = 100

def crear_carpetas():
    os.makedirs(CARPETA_ORIGEN, exist_ok=True)
    os.makedirs(CARPETA_DESTINO, exist_ok=True)

def procesar_imagenes():
    for filename in os.listdir(CARPETA_ORIGEN):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            ruta_origen = os.path.join(CARPETA_ORIGEN, filename)
            ruta_destino = os.path.join(CARPETA_DESTINO, filename)
            
            with Image.open(ruta_origen) as img:
                img_redimensionada = img.resize((ANCHO, ALTO))
                img_redimensionada.save(ruta_destino)

def main():
    crear_carpetas()
    procesar_imagenes()
    print(f"Procesamiento completado. Las imágenes redimensionadas están en {CARPETA_DESTINO}")

if __name__ == "__main__":
    main()
