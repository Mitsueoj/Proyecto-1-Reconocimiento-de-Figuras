import cv2 as cv
import numpy as np

def clasificarFigura(contorno):
    # C — Cuadriláteros (cuadrados, rectángulos, rombos, trapezoides)
    # T — Triángulos (equiláteros, isósceles, escalenos, rectángulos)
    # O — Círculos
    # X — Otros (cualquier figura que no caiga en las anteriores)
    if contorno is None or len(contorno) < 3:
        return "X"

    area = cv.contourArea(contorno)
    perimetro = cv.arcLength(contorno, True)
    
    if area == 0 or perimetro == 0:
        return "X"

    _, r = cv.minEnclosingCircle(contorno)
    areaCirculo = np.pi * (r ** 2)
    if areaCirculo > 0 and (area / areaCirculo) >= 0.90:
        return "O"

    approx = cv.approxPolyDP(contorno, 0.025 * perimetro, True)
    vertices = len(approx)

    if vertices == 3:
        return "T"
    elif vertices == 4:
        return "C"
    
    return "X"