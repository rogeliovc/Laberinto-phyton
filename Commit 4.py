import tkinter as tk
from tkinter import simpledialog, messagebox
import time
import winsound  # Esto es para los efectos de sonido, aunque solo funciona en Windows

# Aquí definimos el laberinto. Usamos una matriz 8x8 donde 0 es camino, 1 es pared, 
# 2 es la salida, 111 y 112 son celdas de trivia, 3 y 4 son teletransportes.
laberinto = [
    [0, 1, 1, 1, 0, 0, 1, 1],
    [0, 0, 0, 1, 0, 1, 0, 1],
    [1, 1, 0, 0, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 1, 112, 1, 1],  # Trivia en (4,5)
    [1, 0, 3, 0, 0, 1, 4, 2],    # Teletransportes entre (5,2) y (5,6), salida en (5,7)
    [1, 1, 1, 1, 0, 0, 0, 0],
    [1, 1, 1, 1, 0, 1, 1, 1]
]

# Usamos algunas variables globales. `memo` es para recordar celdas ya visitadas,
# `movimientos` define las direcciones posibles (derecha, abajo, izquierda, arriba).
n = len(laberinto)
memo = [[-1 for _ in range(n)] for _ in range(n)]
movimientos = [(0, 1), (1, 0), (0, -1), (-1, 0)]
direcciones = ["Derecha", "Abajo", "Izquierda", "Arriba"]

# Ahora configuramos las coordenadas de los teletransportes y otras celdas especiales,
# como las celdas que se desbloquean.
teleport_3 = teleport_4 = None
unlock_key_cell = (0, 1)
block_cell = (6, 6)
key_collected = False

# Identificamos las posiciones de los teletransportes 3 y 4.
for i in range(n):
    for j in range(n):
        if laberinto[i][j] == 3:
            teleport_3 = (i, j)
        elif laberinto[i][j] == 4:
            teleport_4 = (i, j)

# Configuramos la ventana de la interfaz gráfica. Usamos una cuadrícula con etiquetas
# que representan las celdas del laberinto.
root = tk.Tk()
root.title("Laberinto GUI Mejorado")
celdas = [[None for _ in range(n)] for _ in range(n)]
contador_pasos = 0

# Mostramos el progreso de exploración del laberinto con esta barra de progreso.
barra_progreso = tk.Label(root, text="Progreso: 0%", fg="black")
barra_progreso.grid(row=n+2, column=0, columnspan=n, sticky="w")

# Creamos la cuadrícula de celdas. Cada celda tiene un color dependiendo de si es
# camino, pared, salida, trivia, etc.
for i in range(n):
    for j in range(n):
        # Dorado claro para caminos, gris oscuro para paredes
        color = "#FFCC00" if laberinto[i][j] == 0 else "#2E2E2E"  # Dorado claro para caminos, gris oscuro para paredes
        if laberinto[i][j] == 2:
            color = "#00FF00"  # Verde brillante para la salida
        elif laberinto[i][j] == 3 or laberinto[i][j] == 4:
            color = "#9370DB"  # Lavanda para teletransportes
        elif laberinto[i][j] == 111 or laberinto[i][j] == 112:
            color = "#FF4500"  # Naranja oscuro para trivia
        elif laberinto[i][j] == 5:
            color = "#A9A9A9"  # Gris medio para celda bloqueada
        celdas[i][j] = tk.Label(root, width=4, height=2, bg=color, borderwidth=1, relief="solid")
        celdas[i][j].grid(row=i, column=j, sticky="nsew")


# Contamos y mostramos los movimientos que hace el explorador.
etiqueta_movimiento = tk.Label(root, text="Movimientos: 0", fg="blue")
etiqueta_movimiento.grid(row=n, column=1, columnspan=n-1, sticky="w")

# Esta función comprueba si una celda es válida para moverse. Por ejemplo, si la celda
# está bloqueada (como la celda `5`), no se puede cruzar hasta desbloquearla.
def es_valido(x, y):
    if (x, y) == block_cell and not key_collected:
        return False
    return 0 <= x < n and 0 <= y < n and laberinto[x][y] != 1

# Actualizamos el color y el texto de una celda después de cada movimiento.
# También incrementamos el contador de pasos.
def actualizar_celda(x, y, color, movimiento=""):
    global contador_pasos
    celdas[x][y].config(bg=color)
    contador_pasos += 1
    etiqueta_movimiento.config(text=f"Movimientos: {contador_pasos}")
    progreso = (contador_pasos / (n*n)) * 100
    barra_progreso.config(text=f"Progreso: {int(progreso)}%")
    root.update()
    time.sleep(0.2)

# Esta función maneja las preguntas de trivia. Dependiendo del valor de la celda,
# muestra una pregunta u otra.
def celda_trivia(valor):
    while True:
        if valor == 111:
            respuesta = simpledialog.askstring("Pregunta", "¿Cuál es la capital de Francia?")
            if respuesta and respuesta.lower() == "paris":
                winsound.Beep(600, 150)  # Sonido al acertar
                return True
        elif valor == 112:
            respuesta = simpledialog.askstring("Pregunta", "¿Un algoritmo es una serie de pasos lógicos y finitos para resolver un problema?")
            if respuesta and respuesta.lower() in ["verdadero", "true"]:
                winsound.Beep(600, 150)  # Sonido al acertar
                return True
        messagebox.showinfo("Error", "Respuesta incorrecta. Intenta de nuevo.")

# Aquí está el corazón del programa: el algoritmo recursivo que explora el laberinto.
# Si el explorador llega a la salida, se detiene. También maneja celdas especiales
# como los teletransportes y las trivias.
def resolver_laberinto(x, y):
    global key_collected
    if laberinto[x][y] == 2:
        actualizar_celda(x, y, "#0073e6", "Salida encontrada")
        return True
    
    if memo[x][y] != -1:
        return memo[x][y]
    
    if laberinto[x][y] == 3:
        x, y = teleport_4
        actualizar_celda(x, y, "#4682b4", "Teletransportado")
        winsound.Beep(800, 150)
    elif laberinto[x][y] == 4:
        x, y = teleport_3
        actualizar_celda(x, y, "#4682b4", "Teletransportado")
        winsound.Beep(800, 150)
    elif laberinto[x][y] == 111 or laberinto[x][y] == 112:
        celda_trivia(laberinto[x][y])
    elif (x, y) == unlock_key_cell:
        key_collected = True
        celdas[block_cell[0]][block_cell[1]].config(bg="#add8e6")

    memo[x][y] = 0
    actualizar_celda(x, y, "#b0c4de", "Explorando")
    
    for index, (dx, dy) in enumerate(movimientos):
        nx, ny = x + dx, y + dy
        movimiento = direcciones[index]
        if es_valido(nx, ny):
            if resolver_laberinto(nx, ny):
                memo[x][y] = 1
                actualizar_celda(x, y, "#87cefa", f"{movimiento}: con paso")
                return True
            else:
                actualizar_celda(x, y, "#b0c4de", f"{movimiento}: sin paso")
    
    actualizar_celda(x, y, "#708090", "Sin salida")
    return False

# Este botón inicia la exploración del laberinto cuando el usuario lo presiona.
def iniciar_solucion():
    if resolver_laberinto(0, 0):
        tk.Label(root, text="Camino encontrado!", fg="green").grid(row=n+1, column=1, columnspan=n-1)
    else:
        tk.Label(root, text="No se encontró un camino.", fg="red").grid(row=n+1, column=1, columnspan=n-1)

# Aquí creamos el botón que ejecuta la solución.
boton_iniciar = tk.Button(root, text="Iniciar", command=iniciar_solucion)
boton_iniciar.grid(row=n+1, column=0, sticky="w")

root.mainloop()
