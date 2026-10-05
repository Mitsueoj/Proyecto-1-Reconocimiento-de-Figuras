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
    return f"#{r:02x}{g:02x}{b:02x}" #El 02 es para que siempre tenga dos dígitos, y la x es para que sea en formato hexadecimal


"""
 Función para dibujar el borde a cada figura de la imagen.
 Recibe la imagen, el contorno exterior, el contorno interno y el arreglo de color bgr.
"""
def dibujar_borde(imagen, contorno_exterior, contornos_internos, color_bgr):
    alto, ancho = imagen.shape[:2]
    escala = max(1, min(alto, ancho) // 500)
    grosor_fondo = max(5, 5 * escala)
    grosor_linea = max(2, 2 * escala)

    b, g, r = int(color_bgr[0]), int(color_bgr[1]), int(color_bgr[2])
    color_contraste = (255 - b, 255 - g, 255 - r) #Calculamos el color que contrasta con el de la figura

    todos_los_contornos = [contorno_exterior] + (contornos_internos if contornos_internos else [])

    for contorno in todos_los_contornos:
        cv.drawContours(imagen, [contorno], -1, (0, 0, 0), grosor_fondo) #Dibuja un contorno de color negro
        cv.drawContours(imagen, [contorno], -1, color_contraste, grosor_linea) #Dibuja el contorno con una línea más delgada para el color de contraste con la figura

"""
 Función que procesa la imagen.
 Recibe la ruta de la imagen .bmp
 Si no existe la imagen o la ruta está mal, devuelve valores vacíos.
 De lo contrario, crea la máscara de los objetos (la imagen binaria) y 
 la usa para encontrar los contornos. Se clasifican en dos, los que estan 
 al exterior y los que están al interior (hueco en las figuras). Para cada uno se hace lo siguiente:
 Si el contorno corresponde a uno interno, seguimos. De lo contrario se verifica si
 el contorno exterior tenía uno interior y, de ser el caso se agrega a una lista.
 A continuación, se clasifica la figura usando la función clasificar_figura y se calculan las coordenadas
 del primer punto del contorno para así extraer su color y convertirlo a hexadecimal. Se añaden a una lista
 los resultados obtenidos: el tipo de figura, color hexadecimal, coordenada "x" y "y". Por último, se dibuja el
 borde a la figura con su color opuesto usando la función dibujar_borde.
 Regresa la lista de todos los resultados, cuántas figuras se encontraron y la imagen ya modificada.
"""
def procesar_imagen(ruta_imagen):
    imagen = cv.imread(ruta_imagen)
    if imagen is None:
        return [], 0, None

    mascara = crear_mascara_objetos(imagen)

    contornos, jerarquia = cv.findContours(mascara, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)

    resultados = []
    if jerarquia is not None:
        for i, contorno in enumerate(contornos):
            if jerarquia[0][i][3] != -1: #Si el contorno es interno, se lo salta
                continue
    
            contornos_internos = []
            idx_hijo = jerarquia[0][i][2] #Se busca si la figura tiene un "hueco" o contorno interno
            while idx_hijo != -1:
                contornos_internos.append(contornos[idx_hijo])
                idx_hijo = jerarquia[0][idx_hijo][0]

            tipo_figura = clasificar_figura(contorno, contornos_internos)

            px, py = contorno[0][0]
            color_bgr = imagen[py, px]
            color_hex = bgr_a_hex(color_bgr)
            
            resultados.append({
                'tipo_figura': tipo_figura,
                'hex': color_hex,
                'x': px,
                'y': py
            })

            dibujar_borde(imagen, contorno, contornos_internos, color_bgr)

    return resultados, len(resultados), imagen