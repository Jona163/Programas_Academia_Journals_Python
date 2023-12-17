import requests
import folium

def obtener_ruta(partida, destino, paradas, api_key):
    origin = partida.replace(" ", "+")
    destination = destino.replace(" ", "+")
    waypoints = "|".join(paradas.split(","))
    
    #Acceso a google Maps
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&waypoints={waypoints}&key={api_key}"

    response = requests.get(url)
    data = response.json()

    if data["status"] == "OK" and "routes" in data and len(data["routes"]) > 0:
        # (Mejor ruta)
        route = data["routes"][0]["legs"][0]

        # Extrae la información de la ruta y distancia
        ruta_nombres = [step["html_instructions"] for step in route["steps"]]
        ruta = " → ".join(ruta_nombres)
        distancia = route["distance"]["text"]
        distancia_valor = route["distance"]["value"] / 1000  # Distancia en kilómetros

        return ruta, distancia, distancia_valor, data
    else:
        return None, None, None, None

def obtener_coordenadas(data):
    coordenadas = []

    for step in data["routes"][0]["legs"][0]["steps"]:
        lat, lng = step["start_location"]["lat"], step["start_location"]["lng"]
        coordenadas.append((lat, lng))

    # Agregar la coordenada del destino final
    lat, lng = data["routes"][0]["legs"][0]["steps"][-1]["end_location"]["lat"], data["routes"][0]["legs"][0]["steps"][-1]["end_location"]["lng"]
    coordenadas.append((lat, lng))

    return coordenadas

def calcular_costo_aproximado(distancia, costo_combustible_litro, consumo_litro, costo_peaje, gastos_adicionales): 
    costo_combustible = (distancia / consumo_litro) * costo_combustible_litro
    costo_total = costo_combustible + costo_peaje + gastos_adicionales
    return costo_total


def dibujar_ruta_en_mapa(ruta, coordenadas):
    # Crea un mapa centrado en las coordenadas de la primera parada
    mapa = folium.Map(location=coordenadas[0], zoom_start=10)

    # Agrega marcadores para cada parada en la ruta
    for i, coord in enumerate(coordenadas):
        folium.Marker(coord, popup=f"Parada {i+1}: {ruta[i]}").add_to(mapa)

    # Dibuja la línea que conecta las paradas en la ruta
    folium.PolyLine(locations=coordenadas, color='blue').add_to(mapa)

    # Guarda el mapa en un archivo HTML
    mapa.save("ruta_interactiva.html")
    print("Se ha creado un archivo 'ruta_interactiva.html' con el mapa interactivo.")

# Ejemplo de uso del programa:
partida = input("Ingresa el lugar de partida: ")
destino = input("Ingresa el lugar de destino: ")
paradas = input("Ingresa las paradas intermedias separadas por comas (si no hay, deja en blanco): ")

# clave de API de Google Maps
api_key = "AIzaSyDHCfaevPonfALIk_Jk5M59j76VVEa6zHk"

ruta, distancia, distancia_valor, data = obtener_ruta(partida, destino, paradas, api_key)

if ruta is not None and distancia is not None:
    print(f"La mejor ruta seleccionada es: {ruta}")
    print(f"La distancia total es de {distancia} km.")

    costo_combustible_litro = 20  # Costo del litro de combustible
    consumo_litro = 15  # Consumo promedio del vehículo por litro
    costo_peaje = 150  # Costo total de peajes en el recorrido
    gastos_adicionales = 300  # Otros gastos adicionales

    costo_aproximado = calcular_costo_aproximado(distancia_valor, costo_combustible_litro, consumo_litro, costo_peaje, gastos_adicionales)

    print(f"El costo aproximado del recorrido es de ${costo_aproximado:.2f}.")

    coordenadas = obtener_coordenadas(data)

    dibujar_ruta_en_mapa(ruta, coordenadas)
else:
    print("No se encontró una ruta válida para los destinos seleccionados.")