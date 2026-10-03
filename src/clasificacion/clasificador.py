import cv2 as cv
import numpy as np

"""
 Función que determina qué figura geométrica es a partir de su estructura y propiedades.
 Recibe el contorno de un objeto y devuelve "C" si es un cuadrilátero, "T" si es un
 triángulo, "O" si es un círculo y X si es otra figura.
"""
def clasificar_figura(contorno_exterior, contornos_internos=None):
    if contorno_exterior is None or len(contorno_exterior) < 3:
        return "X"

    if contornos_internos and len(contornos_internos) > 0:
        return 'X'

    area = cv.contourArea(contorno_exterior)
    perimetro = cv.arcLength(contorno_exterior, True)
    
    if area == 0 or perimetro == 0:
        return "X"

    _, r = cv.minEnclosingCircle(contorno_exterior)
    area_circulo = np.pi * (r ** 2)
    if area_circulo > 0 and (area / area_circulo) >= 0.95:
        return "O"

    figura_aproximada = cv.approxPolyDP(contorno_exterior, 0.01 * perimetro, True)
    vertices = len(figura_aproximada)

    if vertices == 3:
        return "T"
    elif vertices == 4:
        return "C"
    
    return "X"