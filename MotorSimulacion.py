from settings import Settings
import requests
import folium
from datetime import datetime
import json
from utils import calcular_velocidades, calcular_posiciones, calcular_tiempos, generar_1_mensaje_de_x_ejes, componer_mensaje_circulacion


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Funciones Auxiliares
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!




#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Clases Auxiliares
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
class PuntoRed():
    def __init__(self, set, pk_punto_red):
        self.valido = False
        url = set.url_punto_red + str(pk_punto_red)
        respuesta = requests.get(url, auth = set.auth)
        if respuesta.status_code == requests.codes.ok:
            r = respuesta.json()
            self.codigo = r ['codigo']
            self.lng = r ['lng']
            self.lat = r ['lat']
            self.valido = True

class Vagon():
    def __init__(self, set, pk_vagon):
        self.valido = False
        url = set.url_vagon + str(pk_vagon)
        respuesta = requests.get(url, auth = set.auth)
        if respuesta.status_code == requests.codes.ok:
            r = respuesta.json()
            self.id = r ['id']
            self.codigo = r ['codigo']
            self.valido = True

class Eje():
    def __init__(self, set, pk_eje):
        self.valido = False
        url = set.url_eje + str(pk_eje)
        respuesta = requests.get(url, auth = set.auth)
        if respuesta.status_code == requests.codes.ok:
            r = respuesta.json()
            self.id = r ['id']
            self.codigo = r ['codigo']
            self.valido = True

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Clases Principales
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
class SimuladorCirculacion():
    def __init__(self, vagon, lista_ejes, pk_origen, pk_destino, tiempo_recorrido, tiempo_intervalo):
        self.settings = Settings()
        self.valida = True
        self.error = []
        
        #1. Chequeamos origen:
        self.origen = PuntoRed(self.settings, pk_origen)
        if not self.origen.valido:
            self.valida = False
            self.error.append('El punto de ORIGEN: {}, NO EXISTE.'.format(pk_origen))
        #2. Chequeamos destino:
        self.destino = PuntoRed(self.settings, pk_destino)
        if not self.destino.valido:
            self.valida = False
            self.error.append('El punto de DESTINO: {}, NO EXISTE.'.format(pk_destino))
        # 3. Cargamos info vagones
        self.vagon = Vagon(self.settings, vagon)
        if not self.vagon.valido:
            self.valida = False
            self.error.append('El vagon: {}, NO EXISTE.'.format(vagon))
        # 4. Cargamos info ejes
        self.ejes = []
        for elemento in lista_ejes:
            eje = Eje(self.settings,elemento)
            if not eje.valido:
                self.valida = False
                self.error.append('El eje: {}, NO EXISTE.'.format(elemento))
            else:
                self.ejes.append(eje)
        self.lista_msgs_ejes = []
        self.mensajes_circulacion = []
        # 4. Pasamos el tiempo del recorrido a segundos, dividimos entre el intervalo de mensajes y nos sale el num de mensajes
        self.settings.tiempo_intervalo = tiempo_intervalo
        self.settings.tiempo_recorrido =  int(tiempo_recorrido * 3600)       # nº de Horas * 3600 segundos
        self.settings.num_mensajes = int(self.settings.tiempo_recorrido / self.settings.tiempo_intervalo)

    def calcular(self):
        print ('calculando......')
        self.posiciones = calcular_posiciones(self.settings, self.origen, self.destino)
        self.velocidades = calcular_velocidades (self.settings)
        self.tiempos = calcular_tiempos(self.settings)
        for i in range(self.settings.num_mensajes + 1):
            msg_ejes = generar_1_mensaje_de_x_ejes(self.settings, self.ejes)
            self.lista_msgs_ejes.append(msg_ejes)
        for i in range(self.settings.num_mensajes + 1):
            mensaje_circulacion = componer_mensaje_circulacion (
                        dt = self.tiempos[i],
                        tipo_msg = "CIRC",
                        vagon = self.vagon.codigo,  
                        lng = self.posiciones[i]['lng'],
                        lat = self.posiciones[i]['lat'],
                        vel = self.velocidades[i],
                        msgs_ejes = self.lista_msgs_ejes[i]
                        )
            self.mensajes_circulacion.append(mensaje_circulacion)

    def mostrar(self, mapa):
        print ('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print ('Desde: ' + self.origen.codigo + ': ' + str(self.origen.lng) + ', ' + str(self.origen.lat))
        print ('Hasta: ' + self.destino.codigo + ': ' + str(self.destino.lng) + ', ' + str(self.destino.lat))
        print('Vagon: (' + str(self.vagon.id) +')' + self.vagon.codigo)
        texto = 'Ejes:  ' 
        for eje in self.ejes:
            texto = texto + '(' + str(eje.id) + ')' + eje.codigo + ', '
        print (texto)
        print ('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print('Tiempo de recorrido:  ' + str(self.settings.tiempo_recorrido) + ' segundos')
        print('Número de mensajes de la circulación:  ' + str(self.settings.num_mensajes))
        print ('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        #for msg in self.mensajes_circulacion:
        #    print (msg)
        # Puntos de origen y destino
        location = [self.origen.lat, self.origen.lng]
        html =  '<b>Inicio de la circulación</b>' +\
                '<br><b>Vagón: </b>' + self.vagon.codigo +\
                '<br><b>Latitud: </b>' + str(round(self.mensajes_circulacion[0]['lat'],5)) +\
                '<br><b>Longitud: </b>' + str(round(self.mensajes_circulacion[0]['lng'],5))
        popup = folium.Popup(html = html, max_width=200)
        marker = folium.Marker(location = location, popup = popup, icon = folium.Icon(color="darkblue"))
        marker.add_to(mapa)
        location = [self.destino.lat, self.destino.lng]
        html =  '<b>Final de la circulación</b>' +\
                '<br><b>Vagón: </b>' + self.vagon.codigo +\
                '<br><b>Latitud: </b>' + str(round(self.mensajes_circulacion[-1]['lat'],5)) +\
                '<br><b>Longitud: </b>' + str(round(self.mensajes_circulacion[-1]['lng'],5))
        popup = folium.Popup(html = html, max_width=200)
        marker = folium.Marker(location = location, popup = popup, icon = folium.Icon(color="darkred"))
        marker.add_to(mapa)

        for msg in self.mensajes_circulacion:
            location = [msg['lat'], msg['lng']]
            folium.Circle(
            radius=100,
            location = location,
            popup="posición",
            color="grey",
            fill=False,
            ).add_to(mapa)

    def ejecutar_simulacion(self):
        
        # datetime object containing current date and time
        #now = datetime.now() + self.mensajes_circulacion[0]['dt']
        #dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        #print("date and time =", dt_string)
        #self.mensajes_circulacion[0]['dt'] = dt_string

        #self.mensajes_circulacion[0]['dt'] = '2022-06-01 12:12:12'
        
        #data = json.dumps(self.mensajes_circulacion[0])
        #print(data)

        #respuesta = requests.post(self.settings.url_msg_circ, auth = self.settings.auth, json = self.mensajes_circulacion[0])
        #print (respuesta.status_code)
        #print(respuesta.url)
        
        for msg in self.mensajes_circulacion:
            now = datetime.now() + msg['dt']
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            msg['dt'] = dt_string
            respuesta = requests.post (self.settings.url_msg_circ, auth = self.settings.auth, json = msg)
            print (respuesta.status_code)

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
class SimuladorCambio():
    pass