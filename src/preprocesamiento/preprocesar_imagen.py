import cv2 as cv
import numpy as np

"""
 Función que permite obtener el color del fondo de una imagen.
 Recibe la imagen y después extrae todos los píxeles de las 4 orillas.
 Después encuentra todos los colores y las frecuencias con las que aparecen.
 Se determina que el color del fondo es aquel color con mayor frecuencia en el arreglo.
 Devuelve el color del fondo
"""
def obtener_color_fondo(imagen):
    borde_imagen = np.vstack([imagen[0, :], imagen[-1, :], imagen[1:-1, 0], imagen[1:-1, -1]])
    colores, frecuencias = np.unique(borde_imagen.reshape(-1, 3), axis=0, return_counts=True)
    return colores[np.argmax(frecuencias)].astype(np.uint8)

"""
 Función que crea la máscara de figuras o imagen binaria.
 Recibe la imagen original y aisla las figuras del fondo usando
 el color del segundo y haciendo una limpieza a los contornos internos
 mediante las diferencias de píxeles adyacentes.
 Devuelve la imagen binaria con el fondo negro y las figuras en blanco.
"""
def crear_mascara_objetos(imagen):
    alto, ancho = imagen.shape[:2]
    fondo = obtener_color_fondo(imagen)

    mascara_fondo = cv.inRange(imagen, fondo, fondo)
    diferencia = cv.bitwise_not(mascara_fondo)

    diferencia_horizontal = cv.absdiff(imagen[:-1, :], imagen[1:, :])
    diferencia_vertical = cv.absdiff(imagen[:, :-1], imagen[:, 1:])

    borde_horizontal = np.any(diferencia_horizontal > 0, axis=2).astype(np.uint8) * 255
    borde_vertical = np.any(diferencia_vertical > 0, axis=2).astype(np.uint8) * 255

    bordes = np.zeros((alto, ancho), dtype=np.uint8)
    bordes[:-1, :] |= borde_horizontal
    bordes[:, :-1] |= borde_vertical

    mascara_objetos = cv.subtract(diferencia, bordes)
    return mascara_objetos