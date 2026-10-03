import cv2 as cv
from preprocesamiento.preprocesar_imagen import crear_mascara_objetos
from clasificacion.clasificador import clasificar_figura


"""
 Función para convertir un color BGR a hexadecimal
 Recibe el arreglo de tonos B, G y R.
 Devuelve el color en formato hexadecimal
"""
def bgr_a_hex(color_bgr):
    b, g, r = int(color_bgr[0]), int(color_bgr[1]), int(color_bgr[2])
    return f"#{r:02x}{g:02x}{b:02x}"

def dibujar_borde(imagen, contorno, color_bgr):
    alto, ancho = imagen.shape[:2]
    escala = max(1, min(alto, ancho) // 400)
    grosor_fondo = max(5, 5 * escala)
    grosor_linea = max(3, 3 * escala)

    b, g, r = int(color_bgr[0]), int(color_bgr[1]), int(color_bgr[2])
    color_contraste = (255 - b, 255 - g, 255 - r)

    cv.drawContours(imagen, [contorno], -1, (0, 0, 0), grosor_fondo)
    cv.drawContours(imagen, [contorno], -1, color_contraste, grosor_linea)


def procesar_imagen(ruta_imagen):
    imagen = cv.imread(ruta_imagen)
    if imagen is None:
        return [], 0, None

    mascara = crear_mascara_objetos(imagen)

    contornos, jerarquia = cv.findContours(mascara, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)

    resultados = []
    
    if jerarquia is not None:
        for i, c in enumerate(contornos):
            if jerarquia[0][i][3] != -1:
                continue

            contornos_internos = []
            idx_hijo = jerarquia[0][i][2]
            while idx_hijo != -1:
                contornos_internos.append(contornos[idx_hijo])
                idx_hijo = jerarquia[0][idx_hijo][0]

            tipo_figura = clasificar_figura(c, contornos_internos)

            px, py = c[0][0]
            color_bgr = imagen[py, px]
            color_hex = bgr_a_hex(color_bgr)
            b, g, r = int(color_bgr[0]), int(color_bgr[1]), int(color_bgr[2])

            resultados.append({
                'tipo_figura': tipo_figura,
                'hex': color_hex,
                'rgb': (r, g, b),
                'x': px,
                'y': py
            })

            dibujar_borde(imagen, c, color_bgr)

    return resultados, len(resultados), imagen