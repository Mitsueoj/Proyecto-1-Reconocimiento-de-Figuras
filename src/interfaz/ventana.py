import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2 as cv

def crear_interfaz(funcion_proc):
    ruta_glob = ""

    def seleccionar_imagen():
        nonlocal ruta_glob
        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imagen BMP", "*.bmp")]
        )

        if ruta:
            ruta_glob = ruta
            etiqueta_ruta.config(text=ruta)

            imagen = Image.open(ruta)
            imagen.thumbnail((450, 300))
            imagen_tk = ImageTk.PhotoImage(imagen)

            etiqueta_original.config(image=imagen_tk)
            etiqueta_original.image = imagen_tk

            etiqueta_resultado.config(image="")
            etiqueta_resultado.image = None

            boton_analizar.config(state="normal")

    def analizar_imagen():
        nonlocal ruta_glob
        if not ruta_glob:
            return
        etiqueta_resultados.config(text="Analizando imagen...")
        ventana.update_idletasks()

        resultados, num_resultados, imagen_resultado = funcion_proc(ruta_glob)
        etiqueta_resultados.config(text=f"Resultados: {num_resultados} figuras detectadas")

        if imagen_resultado is not None:
            imagen_rgb = cv.cvtColor(imagen_resultado, cv.COLOR_BGR2RGB)
            imagen_pil = Image.fromarray(imagen_rgb)
            imagen_pil.thumbnail((450, 300))

            imagen_res_tk = ImageTk.PhotoImage(imagen_pil)
            etiqueta_resultado.config(image=imagen_res_tk)
            etiqueta_resultado.image = imagen_res_tk

    ventana = tk.Tk()
    ventana.title("Reconocimiento de Figuras")
    ventana.geometry("1000x600")

    titulo = tk.Label(
        ventana,
        text="Reconocimiento de Figuras",
        font=("Arial", 20)
    )
    titulo.pack(pady=20)

    boton_seleccionar = tk.Button(
        ventana,
        text="Seleccionar imagen",
        font=("Arial", 12),
        command=seleccionar_imagen
    )
    boton_seleccionar.pack(pady=10)

    etiqueta_ruta = tk.Label(
        ventana,
        text="No se ha seleccionado ninguna imagen",
        wraplength=800
    )
    etiqueta_ruta.pack(pady=10)

    boton_analizar = tk.Button(
        ventana,
        text="Analizar imagen",
        font=("Arial", 12),
        command=analizar_imagen,
        state="disabled"
    )
    boton_analizar.pack(pady=15)

    marco_imagenes = tk.Frame(ventana)
    marco_imagenes.pack(pady=10)

    etiqueta_original = tk.Label(marco_imagenes)
    etiqueta_original.pack(side="left", padx=15)

    etiqueta_resultado = tk.Label(marco_imagenes)
    etiqueta_resultado.pack(side="right", padx=15)

    etiqueta_resultados = tk.Label(
        ventana,
        text="",
        font=("Arial", 11),
        wraplength=800
    )
    etiqueta_resultados.pack(pady=10)

    return ventana