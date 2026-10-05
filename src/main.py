from deteccion.detector import procesar_imagen
from interfaz.ventana import crear_interfaz

"""
 Función main que inicializa y construye la interfaz
 gráfica con la función para procesar la imagen como
 parámetro
"""
if __name__ == "__main__":
    app = crear_interfaz(procesar_imagen)
    app.mainloop()