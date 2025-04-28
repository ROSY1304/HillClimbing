import math
import random
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

def distancia(coord1, coord2):
    lat1 = coord1[0]
    lon1 = coord1[1]
    lat2 = coord2[0]
    lon2 = coord2[1]
    # Haciendo la conversión a distancia en kilómetros utilizando la fórmula Haversine
    R = 6371  # Radio de la Tierra en km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # Distancia en km

# Calcular la distancia cubierta por cada ruta
def evalua_ruta(ruta, coord):
    total = 0
    for i in range(0, len(ruta) - 1):
        ciudad1 = ruta[i]
        ciudad2 = ruta[i + 1]
        total += distancia(coord[ciudad1], coord[ciudad2])
    ciudad1 = ruta[-1]  # La última ciudad
    ciudad2 = ruta[0]   # Regresar a la ciudad inicial
    total += distancia(coord[ciudad1], coord[ciudad2])
    return total

def hill_climbing(coord):
    # Crear la ruta inicial aleatoria
    ruta = list(coord.keys())
    random.shuffle(ruta)  # Corregido: shuffle, no suffle

    # Calcula la distancia de la ruta inicial
    dist_actual = evalua_ruta(ruta, coord)

    mejora = True
    while mejora:
        mejora = False
        # Evaluar vecinos
        for i in range(0, len(ruta)):
            if mejora:
                break
            for j in range(0, len(ruta)):
                if i != j:
                    ruta_tmp = ruta[:]
                    # Intercambiar dos ciudades
                    ruta_tmp[i], ruta_tmp[j] = ruta_tmp[j], ruta_tmp[i]
                    dist = evalua_ruta(ruta_tmp, coord)
                    # Asegurarse de que solo se optimicen las rutas, no la distancia
                    if dist < dist_actual:
                        # Se ha encontrado un vecino que mejora la ruta
                        mejora = True
                        ruta = ruta_tmp[:]
                        dist_actual = dist  # Solo actualizamos la distancia si la ruta mejora
                        break
    return ruta, dist_actual

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ruta_optima', methods=['POST'])
def ruta_optima():
    try:
        # Obtener los datos de las ciudades desde el cuerpo de la solicitud
        data = request.json
        coord = {}
        
        for ciudad in data:
            nombre = ciudad['nombre']
            latitud = ciudad['latitud']
            longitud = ciudad['longitud']
            coord[nombre] = (latitud, longitud)
        
        # Calcular la ruta óptima usando Hill Climbing
        ruta, distancia_total = hill_climbing(coord)

        # Retornar la ruta óptima y la distancia total en formato JSON
        return jsonify({
            'ruta_optima': ruta,
            'distancia_total': distancia_total
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
