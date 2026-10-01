import cv2 as cv
import numpy as np
import imutils

"""
 Función que determina qué figura geométrica es a partir de cuántos vértices
 tiene.
 Recibe el contorno de cada figura y devuelve "C" si es un cuadrilátero, "T" si es un
 triángulo, "O" si es un círculo y X si es otra figura.
"""
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

"""
 Función para convertir los colores BGR a hexadecimal
 Recibe el arreglo del promedio de tonos B, G y R.
 Devuelve el color en hexadecimal
"""
#Convertimos los colores de BGR a hexadecimal
def convertirHex(bgr):
    b, g, r = int(bgr[0]), int(bgr[1]), int(bgr[2]) 
    #en hexadecimal los valores van en orden contrario a BGR
    return f"#{r:02x}{g:02x}{b:02x}".upper() #:02 para que tenga dos dígitos siempre y x para pasarlo a hexadecimal    


"""
 Función que analiza la imagen y determina qué figuras tiene junto con sus colores.
 Recibe la ruta de la imagen .bmp, después, cambia el tamaño y la convierte en una lista de píxeles.
 Encontramos todos los colores de la imagen y las repeticiones, para después determinar el color del fondo
 encontrando el que tiene mayor número de repeticiones.
 y devuelve
"""
#Función para analizar la imagen. Recibe la ruta del .bmp 
def figurasYColores(ruta_img):
    #leemos la imagen y si falla, regresamos un error
    img = cv.imread(ruta_img) 
    if img is None:
        return "Error: la ruta no es válida. Revisa que exista la imagen", None
        
    
    #Le cambiamos el tamaño a nuestra imagen
    resized = imutils.resize(img, width=800)

    #Transformamos la imagen en una lista plana de píxeles
    pixels = resized.reshape(-1, 3) #El -1 hace que se calcule automáticamente el tamaño para el número de filas
    colores, cantidades = np.unique(pixels, axis=0, return_counts=True) #Checamos qué colores están y cuántas veces se repiten. axis=0 indica las filas (completas)
    fondo = colores[np.argmax(cantidades)].astype(np.int16) #Determinamos el fondo checando con argmax cuál color tuvo más repeticiones. Se usa int16 para evitar desbordamientos

    #Creación Máscara y Separación de Figuras
    imagen16 = resized.astype(np.int16) #Cambiamos el formato de la imagen para poder hacer la resta
    diferencia = np.abs(imagen16 - fondo) #Calculamos cuál es la diferencia de color entre cada píxel con el color del fondo
    diferenciaMax = np.max(diferencia, axis=2) #Para cada píxel, busca las diferencias entre los colores Azul, Verde y Rojo y se queda con el mayor

    _, thresh = cv.threshold(diferenciaMax.astype(np.uint8), 22, 255, cv.THRESH_BINARY) #Creamos la imagen binaria con el arreglo de diferencias máximas convertido a uint8 con un umbral de 22

    lab = cv.cvtColor(resized, cv.COLOR_BGR2LAB) #Convertimos la imagen a lab
    gradientes = [] #Creamos un arreglo para los gradientes

    #Separamos L A B y para cada una usamos el operador Sobel para detectar bordes
    for canal in cv.split(lab):
        sobelx = cv.Sobel(canal, cv.CV_32F, 1, 0, ksize=3) #Bordes horizontales
        sobely = cv.Sobel(canal, cv.CV_32F, 0, 1, ksize=3) #Bordes verticales
        magnitud = cv.magnitude(sobelx, sobely) #Calculamos la magnitud combinando los dos anteriores para saber si hay un borde en cada píxel
        gradientes.append(magnitud) #Lo agregamos al arreglo de gradientes

    gradiente_color = np.maximum.reduce(gradientes) #Comparamos por cada píxel su valor en L A y B calculado anteriormente y nos quedamos con el mayor

    _, bordes_color = cv.threshold(gradiente_color, 20, 255, cv.THRESH_BINARY) #Convertimos el mapeo de gradientes a una imagen binaria
    bordes_color = bordes_color.astype(np.uint8) #Lo convertimos a uint8
    kernel_borde = np.ones((3, 3), np.uint8) #Creamos una matriz de 3x3 llena de 1 de tipo uint8
    bordes_color = cv.dilate(bordes_color, kernel_borde, iterations=1) #Hacemos más gruesos los bordes de la imagen usando kernel_borde para indicar qué tan grade hacer la expansión

    thresh_separado = thresh.copy() #Hacemos una copia de la máscara original de las figuras
    thresh_separado[bordes_color > 0] = 0 #Pintamos de negro todos los bordes gruesos que calculamos para evitar que se junten figuras que estaban muy pegadas en la máscara

    kernel_limpieza = np.ones((2, 2), np.uint8) #Creamos una matriz de 2x2 llena de 1 de tipo uint8
    thresh_separado = cv.morphologyEx(thresh_separado, cv.MORPH_OPEN, kernel_limpieza, iterations=1) #Hacemos una erosión y una dilatación a la imagen para quitar las pequeñas partes blancas que no nos interesaban
    cnts, _ = cv.findContours(thresh_separado.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE) #Encontramos el contorno de nuestras figuras
    resultados_lista = []

    #Recorremos cada contorno
    for c in cnts:
        imAux = np.zeros(resized.shape[:2], dtype="uint8") #Creamos una imagen negra del mismo tamaño que la original
        cv.drawContours(imAux, [c], -1, 255, -1) #Dibuja solamente la figura actual rellenándola de blanco (máscara local)

        color_prom_bgr = cv.mean(resized, mask=imAux)[:3] #Calculamos el promedio de color de la imagen auxiliar en la máscara local solamente
        color_hex = convertirHex(color_prom_bgr) #Pasamos el color a hexadecimal
        tipo_figura = clasificarFigura(c) #Clasificamos la figura
        x, y, w, h = cv.boundingRect(c) #Calculamos las coordenadas x,y, ancho w y alto h de la figura
        texto_resultado = f"{tipo_figura}{color_hex}" #Formato de salida del texto
        resultados_lista.append(texto_resultado) #Lo añadimos a nuestra lista de resultados

        #cv.drawContours(resized, [c], -1, (0, 255, 0), 2) #Si queremos que se dibujen los contornos de cada figura, descomentamos esta línea. Se dibujan en verde
        #pos_y = max(y - 10, 30)
        centro_x = int(x + w /2)
        centro_y = int(y + h /2)

        #cv.putText(resized,texto_resultado,(x, pos_y),cv.FONT_HERSHEY_SIMPLEX,0.6,(255, 255, 255),2) #Coloca el texto arriba de cada figura en la imagen
        cv.putText(resized,texto_resultado,(centro_x - 30, centro_y),cv.FONT_HERSHEY_SIMPLEX,0.6,(255, 255, 255),2) #Coloca el texto en el centro de cada figura en la imagen

    total_fig = f"Total figuras: {len(cnts)}\n" + ", ".join(resultados_lista) #Formato para imprimir cuántas figuras encontamos y el tipo + color
    return total_fig, resized
