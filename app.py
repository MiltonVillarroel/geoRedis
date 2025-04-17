from flask import Flask, render_template, request, jsonify
import requests
from conexion import r

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/carga')
def carga():
    print('Recibido')
    latitud = request.args.get('latitud')
    longitud = request.args.get('longitud')
    radio = request.args.get('radio')

    url = "http://overpass-api.de/api/interpreter"
    query = f"[out:json][timeout:180];node(around:{radio}, {latitud}, {longitud})['amenity'];out center;"
    response = requests.post(url, data=query)
    data = response.json()
   
    pipe = r.pipeline()
    tipos = set()

    for element in data.get("elements", []):
        tags = element.get("tags", {})
        nombre = tags.get("name")
        tipo = tags.get("amenity")
        latitud = element.get("lat")
        longitud = element.get("lon")
        id = element.get("id")

        if not tipo or not latitud or not longitud or not nombre or not id:
            continue

        miembro = f"{tipo}:{nombre}:{id}"        
        pipe.geoadd("lugares", (longitud, latitud, miembro))
        tipos.add(tipo)

    tipos = sorted(tipos)
    pipe.expire("lugares", 30)
    pipe.execute()
    print('enviado')

    return jsonify(tipos)

@app.route('/buscar', methods=['POST'])
def buscar():
    data = request.get_json()
    lat = float(data['lat'])
    lon = float(data['lon'])
    radio = int(data['radio'])
    tipo = data['tipo']

    lugares = r.georadius('lugares', lon, lat, radio, unit='m', withdist=True, withcoord=True)

    resultados = []
    for lugar in lugares:
        nombre = lugar[0]
        if nombre.startswith(tipo + ":"):
            partes = nombre.split(":", 2)  # tipo:nombre:id
            if len(partes) == 3:
                nombre_real = partes[1]
            else:
                nombre_real = nombre

            resultados.append({
                'nombre': nombre_real,
                'distancia': lugar[1],
                'lat': lugar[2][1],
                'lon': lugar[2][0]
            })

    return jsonify(resultados)

if __name__ == '__main__':
    app.run(debug=True)
