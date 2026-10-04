import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from PIL import Image, ImageTk
import cv2 as cv


def crear_interfaz(funcion_procesar_imagen):
    ruta_glob = ""
    imagen_resultado_glob = None
    reporte_texto_glob = ""

    def seleccionar_imagen():
        nonlocal ruta_glob, imagen_resultado_glob, reporte_texto_glob

        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imagen BMP", "*.bmp")]
        )

        if ruta:
            ruta_glob = ruta
            imagen_resultado_glob = None
            reporte_texto_glob = ""

            etiqueta_titulo_original.config(text="Imagen Seleccionada")
            etiqueta_titulo_resultado.config(text="")
            etiqueta_ruta.config(text=ruta)

            try:
                imagen_pillow = Image.open(ruta)
                imagen_pillow.thumbnail((450, 300))
                imagen_tk = ImageTk.PhotoImage(imagen_pillow)

                etiqueta_original.config(image=imagen_tk)
                etiqueta_original.image = imagen_tk

                etiqueta_resultado.config(image="")
                etiqueta_resultado.image = None

                etiqueta_resultados.config(
                    text="Imagen cargada. Presione Analizar imagen."
                )

                caja_texto.config(state="normal")
                caja_texto.delete("1.0", tk.END)
                caja_texto.config(state="disabled")

                boton_analizar.config(state="normal")
                boton_descargar.config(state="disabled")
                boton_copiar_reporte.config(state="disabled")

            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"No se pudo cargar la imagen seleccionada:\n{e}"
                )

    def analizar_imagen():
        nonlocal ruta_glob, imagen_resultado_glob, reporte_texto_glob

        if not ruta_glob:
            return

        etiqueta_resultados.config(text="Analizando imagen...")
        ventana.update_idletasks()

        resultados, num_resultados, imagen_resultado = (
            funcion_procesar_imagen(ruta_glob)
        )

        etiqueta_resultados.config(
            text=f"Análisis terminado: {num_resultados} figuras detectadas"
        )

        caja_texto.config(state="normal")
        caja_texto.delete("1.0", tk.END)

        lineas_reporte = [
            f"Figuras detectadas ({num_resultados} Figuras)"
        ]

        for idx, figura in enumerate(resultados, 1):
            linea_terminal = (
                f"#{idx:02d} | "
                f"Tipo: {figura['tipo_figura']} | "
                f"Coordenadas: ({figura['x']}, {figura['y']}) | "
                f"Color Hex: {figura['hex']}"
            )

            lineas_reporte.append(linea_terminal)

            caja_texto.insert(
                tk.END,
                f"#{idx:02d} | Color: "
            )

            nombre_tag = f"color_{idx}"

            caja_texto.tag_config(
                nombre_tag,
                foreground=figura["hex"]
            )

            caja_texto.insert(
                tk.END,
                "■ ",
                nombre_tag
            )

            detalles = (
                f"| Tipo: {figura['tipo_figura']} | "
                f"Coordenadas: ({figura['x']}, {figura['y']}) | "
                f"Hex: {figura['hex']}\n"
            )

            caja_texto.insert(tk.END, detalles)

        caja_texto.config(state="disabled")

        reporte_texto_glob = "\n".join(lineas_reporte)

        if imagen_resultado is not None:
            imagen_resultado_glob = imagen_resultado
            etiqueta_titulo_resultado.config(text="Resultado")

            img_rgb = cv.cvtColor(
                imagen_resultado,
                cv.COLOR_BGR2RGB
            )

            imagen_pillow = Image.fromarray(img_rgb)
            imagen_pillow.thumbnail((450, 300))

            img_res_tk = ImageTk.PhotoImage(imagen_pillow)

            etiqueta_resultado.config(image=img_res_tk)
            etiqueta_resultado.image = img_res_tk

            boton_descargar.config(state="normal")
            boton_copiar_reporte.config(state="normal")

    def imprimir_y_copiar_reporte():
        nonlocal reporte_texto_glob

        if not reporte_texto_glob:
            return

        print("\n" + reporte_texto_glob + "\n")

        ventana.clipboard_clear()
        ventana.clipboard_append(reporte_texto_glob)
        ventana.update()

        etiqueta_resultados.config(
            text="Reporte enviado a terminal y copiado al portapapeles."
        )

    def descargar_imagen_resultado():
        if imagen_resultado_glob is None:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".bmp",
            filetypes=[
                ("BMP files", "*.bmp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            cv.imwrite(
                file_path,
                imagen_resultado_glob
            )

    ventana = tk.Tk()

    ventana.title("Proyecto 1: Reconocimiento de Figuras")
    ventana.geometry("1000x780")
    ventana.configure(bg="#2C2F3B")

    tk.Label(
        ventana,
        text="Proyecto I: Reconocimiento de Figuras",
        font=("Arial", 20),
        bg="#2C2F3B",
        fg="white"
    ).pack(pady=10)

    boton_seleccionar = tk.Button(
        ventana,
        text="Seleccionar imagen",
        font=("Arial", 11),
        bg="#3F4354",
        fg="white",
        relief="flat",
        highlightthickness=0,
        command=seleccionar_imagen
    )

    boton_seleccionar.pack(pady=3)

    etiqueta_ruta = tk.Label(
        ventana,
        text="No se ha seleccionado ninguna imagen",
        wraplength=800,
        bg="#2C2F3B",
        fg="white"
    )

    etiqueta_ruta.pack(pady=3)

    frame_botones = tk.Frame(
        ventana,
        bg="#2C2F3B"
    )

    frame_botones.pack(pady=3)

    boton_analizar = tk.Button(
        frame_botones,
        text="Analizar imagen",
        font=("Arial", 11),
        bg="#3F43C0",
        fg="white",
        relief="flat",
        state="disabled",
        highlightthickness=0,
        command=analizar_imagen
    )

    boton_analizar.pack(
        side="left",
        padx=5
    )

    boton_descargar = tk.Button(
        frame_botones,
        text="Descargar resultado",
        font=("Arial", 11),
        bg="#3F4354",
        fg="white",
        relief="flat",
        state="disabled",
        highlightthickness=0,
        command=descargar_imagen_resultado
    )

    boton_descargar.pack(
        side="left",
        padx=5
    )

    boton_copiar_reporte = tk.Button(
        frame_botones,
        text="Enviar a terminal y copiar reporte",
        font=("Arial", 11),
        bg="#28A745",
        fg="white",
        relief="flat",
        state="disabled",
        highlightthickness=0,
        command=imprimir_y_copiar_reporte
    )

    boton_copiar_reporte.pack(
        side="left",
        padx=5
    )

    frame_imagenes = tk.Frame(
        ventana,
        bg="#2C2F3B"
    )

    frame_imagenes.pack(pady=5)

    frame_izquierdo = tk.Frame(
        frame_imagenes,
        bg="#2C2F3B"
    )

    frame_izquierdo.pack(
        side="left",
        padx=15
    )

    etiqueta_titulo_original = tk.Label(
        frame_izquierdo,
        text="",
        font=("Arial", 11, "bold"),
        bg="#2C2F3B",
        fg="white"
    )

    etiqueta_titulo_original.pack(pady=5)

    etiqueta_original = tk.Label(
        frame_izquierdo,
        bg="#2C2F3B"
    )

    etiqueta_original.pack()

    frame_derecho = tk.Frame(
        frame_imagenes,
        bg="#2C2F3B"
    )

    frame_derecho.pack(
        side="right",
        padx=15
    )

    etiqueta_titulo_resultado = tk.Label(
        frame_derecho,
        text="",
        font=("Arial", 11, "bold"),
        bg="#2C2F3B",
        fg="white"
    )

    etiqueta_titulo_resultado.pack(pady=5)

    etiqueta_resultado = tk.Label(
        frame_derecho,
        bg="#2C2F3B"
    )

    etiqueta_resultado.pack()

    etiqueta_resultados = tk.Label(
        ventana,
        text="Seleccione una imagen y presione Analizar imagen",
        font=("Arial", 11),
        bg="#2C2F3B",
        fg="white",
        wraplength=800
    )

    etiqueta_resultados.pack(pady=3)

    caja_texto = scrolledtext.ScrolledText(
        ventana,
        width=105,
        height=9,
        bg="#3F4354",
        fg="#FFFFFF",
        font=("Arial", 10),
        state="disabled",
        highlightthickness=0,
        relief="flat"
    )

    caja_texto.pack(pady=5)

    return ventana
