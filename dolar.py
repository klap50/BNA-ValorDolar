import requests
import curses
import time
from datetime import datetime, timedelta
import warnings

# Suprimir advertencias SSL
from requests.packages.urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

# Función para hacer la consulta a la API y devolver los valores de una variable específica
def obtener_valores(id_variable):
    hoy = datetime.now().strftime('%Y-%m-%d')
    hace_7_dias = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    url = f"https://api.bcra.gob.ar/estadisticas/v2.0/datosvariable/{id_variable}/{hace_7_dias}/{hoy}"
    
    intentos = 0
    max_intentos = 3
    while intentos < max_intentos:
        try:
            response = requests.get(url, verify=False)
            response.raise_for_status()  # Verifica si la respuesta es 200 OK
            data = response.json()
            return data['results'][::-1]  # Invertimos el orden de los resultados
        except requests.exceptions.RequestException as e:
            intentos += 1
            print(f"Error de conexión: {e}. Reintentando ({intentos}/{max_intentos})...")
            time.sleep(2)
    
    return None

# Función principal para mostrar en pantalla los valores con colores
def mostrar_valores(screen):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # Color rojo para el valor más reciente
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Color verde para días anteriores

    screen.nodelay(1)  # No bloquear la ejecución con getch

    while True:
        # Limpiamos la pantalla
        screen.clear()

        # Obtenemos los valores para el Dólar BNA (ID 4), Dólar MEP (ID 5), y Reservas Internacionales (ID 1)
        valores_bna = obtener_valores(4)  # ID 4 para el Dólar BNA
        valores_mep = obtener_valores(5)  # ID 5 para el Dólar MEP (reemplazar con el ID correcto)
        reservas = obtener_valores(1)     # ID 1 para Reservas Internacionales

        if valores_bna is None or valores_mep is None or reservas is None:
            screen.addstr(0, 0, "Error: No se pudieron obtener los datos. Presiona F5 para reintentar o Q para salir.")
        else:
            # Obtener el tamaño de la ventana
            max_lines = curses.LINES
            line_count = 0

            # Mostramos los valores del Dólar BNA
            screen.addstr(line_count, 0, "Valores del Dólar BNA:", curses.A_BOLD)
            line_count += 1
            for i, valor in enumerate(valores_bna):
                if line_count >= max_lines - 1:
                    break
                fecha = valor['fecha']
                valor_dolar = valor['valor']
                if i == 0:
                    screen.addstr(line_count, 0, f"Valor del día ({fecha}): {valor_dolar}", curses.color_pair(1))  # Hoy en rojo
                else:
                    screen.addstr(line_count, 0, f"Valor anterior {i} ({fecha}): {valor_dolar}", curses.color_pair(2))  # Anteriores en verde
                line_count += 1

            # Mostramos los valores del Dólar MEP
            if line_count < max_lines - 1:
                screen.addstr(line_count + 1, 0, "Valores del Dólar MEP:", curses.A_BOLD)
                line_count += 2
                for i, valor in enumerate(valores_mep):
                    if line_count >= max_lines - 1:
                        break
                    fecha = valor['fecha']
                    valor_dolar = valor['valor']
                    if i == 0:
                        screen.addstr(line_count, 0, f"Valor del día ({fecha}): {valor_dolar}", curses.color_pair(1))  # Hoy en rojo
                    else:
                        screen.addstr(line_count, 0, f"Valor anterior {i} ({fecha}): {valor_dolar}", curses.color_pair(2))  # Anteriores en verde
                    line_count += 1

            # Mostramos los valores de las Reservas Internacionales
            if line_count < max_lines - 1:
                screen.addstr(line_count + 1, 0, "Reservas Internacionales (en millones de USD):", curses.A_BOLD)
                line_count += 2
                for i, reserva in enumerate(reservas):
                    if line_count >= max_lines - 1:
                        break
                    fecha = reserva['fecha']
                    valor_reserva = reserva['valor']
                    if i == 0:
                        screen.addstr(line_count, 0, f"Valor del día ({fecha}): {valor_reserva}", curses.color_pair(1))  # Hoy en rojo
                    else:
                        screen.addstr(line_count, 0, f"Valor anterior {i} ({fecha}): {valor_reserva}", curses.color_pair(2))  # Anteriores en verde
                    line_count += 1

        # Mostrar mensaje de actualización o salida
        if line_count < max_lines - 1:
            screen.addstr(line_count + 1, 0, "Presiona F5 para actualizar, Q para salir", curses.A_BOLD)

        screen.refresh()

        # Leer entrada del usuario
        key = screen.getch()

        if key == curses.KEY_F5:  # F5 para actualizar
            continue
        elif key == ord('q') or key == ord('Q'):  # 'Q' para salir
            break

        # Pequeño retraso para evitar un bucle rápido
        time.sleep(0.1)

# Iniciar el programa en el modo curses
curses.wrapper(mostrar_valores)
