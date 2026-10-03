from deteccion.detector import procesar_imagen
from interfaz.ventana import crear_interfaz

if __name__ == "__main__":
    app = crear_interfaz(procesar_imagen)
    app.mainloop()