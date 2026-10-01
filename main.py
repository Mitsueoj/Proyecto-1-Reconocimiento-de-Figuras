from clasificarFigura import figurasYColores
from interfaz import crear_interfaz

if __name__ == "__main__":
    app = crear_interfaz(figurasYColores)
    app.mainloop()