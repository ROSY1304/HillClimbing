import math
import itertools
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Coordenadas de las ciudades
coord = {
    'Jiloyork': (19.916012, -99.580580), 'Toluca': (19.289165, -99.655697),
    'Atlacomulco': (19.799520, -99.873844), 'Guadalajara': (20.677754, -103.346253),
    'Monterrey': (25.691611, -100.321838), 'QuintanaRoo': (21.163111, -86.802315),
    'Michoacan': (19.701400, -101.208296), 'Aguascalientes': (21.876410, -102.264386),
    'CDMX': (19.432713, -99.133183), 'QRO': (20.597194, -100.386670)
}

# Calcular distancia entre dos ciudades
def calcular_distancia(ciudad1, ciudad2):
    lat1, lon1 = coord[ciudad1]
    lat2, lon2 = coord[ciudad2]
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

# Evaluar la ruta sin repetir la ciudad inicial
def evalua_ruta(ruta):
    total = sum(calcular_distancia(ruta[i], ruta[i + 1]) for i in range(len(ruta) - 1))
    return total

# Encontrar las mejores rutas
def encontrar_mejor_ruta(ciudad_inicio, ciudad_llegada, ciudades):
    # Verificar si las ciudades están en la lista
    if ciudad_inicio not in ciudades or ciudad_llegada not in ciudades:
        raise ValueError("Las ciudades de inicio o llegada no están en la lista de ciudades seleccionadas.")
    
    # Eliminar las ciudades de la lista
    ciudades.remove(ciudad_inicio)
    ciudades.remove(ciudad_llegada)

    todas_las_rutas = list(itertools.permutations(ciudades))
    rutas_resultados = [{
        "ruta": [ciudad_inicio] + list(ruta) + [ciudad_llegada],
        "distancia": evalua_ruta([ciudad_inicio] + list(ruta) + [ciudad_llegada])
    } for ruta in todas_las_rutas]
    rutas_resultados.sort(key=lambda x: x["distancia"])
    return rutas_resultados[:5]

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/tsp', methods=['POST'])
def tsp():
    data = request.json
    ciudad_inicio = data.get("start_city")
    ciudad_llegada = data.get("end_city")
    selected_cities = data.get("cities")

    if not ciudad_inicio or not ciudad_llegada or not selected_cities or len(selected_cities) < 2:
        return jsonify({"error": "Selecciona una ciudad de inicio, una de llegada y al menos dos ciudades."}), 400

    try:
        rutas_optimas = encontrar_mejor_ruta(ciudad_inicio, ciudad_llegada, selected_cities)
        return jsonify({"rutas_optimas": rutas_optimas})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
