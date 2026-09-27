import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def seleccionar_imagen():
    ruta = filedialog.askopenfilename(
        title="Seleccionar imagen",
        filetypes=[("Imagen BMP", "*.bmp")]
    )

    if ruta:
        etiqueta_ruta.config(text=ruta)

        imagen = Image.open(ruta)
        imagen.thumbnail((400, 250))

        imagen_tk = ImageTk.PhotoImage(imagen)

        etiqueta_imagen.config(image=imagen_tk)
        etiqueta_imagen.image = imagen_tk

        boton_analizar.config(state="normal")


def analizar_imagen():
    etiqueta_resultados.config(
        text="Esperando resultados del módulo de reconocimiento..."
    )


ventana = tk.Tk()

ventana.title("Reconocimiento de Figuras")
ventana.geometry("700x700")


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
    wraplength=600
)

etiqueta_ruta.pack(pady=10)


etiqueta_imagen = tk.Label(ventana)

etiqueta_imagen.pack(pady=10)


boton_analizar = tk.Button(
    ventana,
    text="Analizar imagen",
    font=("Arial", 12),
    command=analizar_imagen,
    state="disabled"
)

boton_analizar.pack(pady=15)


etiqueta_resultados = tk.Label(
    ventana,
    text="",
    font=("Arial", 11),
    wraplength=600
)

etiqueta_resultados.pack(pady=10)


ventana.mainloop()
