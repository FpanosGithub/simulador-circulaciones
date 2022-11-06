from settings import Settings
import requests
import folium
from datetime import datetime, timedelta
from utils import calcular_velocidades, calcular_posiciones, calcular_tiempos, generar_1_mensaje_de_x_ejes, mensaje_cambio

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CIRCULACIÓN
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

class CirculacionVagon():
    def __init__(self, vagon, pk_origen, pk_destino, tiempo_recorrido, tiempo_intervalo):
        # URLS y otras constantes
        self.settings = Settings()
        # Valores simulación
        self.origen = pk_origen
        self.destino = pk_destino
        self.vagon = vagon['codigo']
        self.ejes = vagon['ejes']
        self.tiempo_recorrido = tiempo_recorrido
        self.num_mensajes = int(tiempo_recorrido * 3600 / tiempo_intervalo)
        self.posiciones = calcular_posiciones(self.num_mensajes, self.origen, self.destino)
        self.velocidades = calcular_velocidades (self.num_mensajes)
        self.tiempos = calcular_tiempos(self.num_mensajes, tiempo_intervalo)
        
        # Componentes del MENSAJE a enviar
        # Mensajes de ejes. 
        self.lista_msgs_ejes = []
        for i in range(self.num_mensajes + 1):
            msg_ejes = generar_1_mensaje_de_x_ejes(self.settings, self.ejes)
            self.lista_msgs_ejes.append(msg_ejes)
        
        # Para cada posición de la circulación generamos 1 mensaje completo de la circulación y lo guardamos en mensajes_circulacion
        self.mensajes_circulacion = []
        for i in range(self.num_mensajes +1):
            mensaje_circulacion = \
                {
                'dt': self.tiempos[i],
                'tipo_msg': "CIRC",
                'vagon': self.vagon,
                'lng': self.posiciones[i]['lng'],
                'lat': self.posiciones[i]['lat'],
                'vel': self.velocidades[i],
                'msgs_ejes': self.lista_msgs_ejes[i],
                }
            self.mensajes_circulacion.append(mensaje_circulacion)
        # Guardamos un último mensaje para que se genere una parada
        msg_ejes = generar_1_mensaje_de_x_ejes(self.settings, self.ejes)
        mensaje_circulacion = \
                {
                'dt': self.tiempos[i],
                'tipo_msg': "CIRC",
                'vagon': self.vagon,
                'lng': self.posiciones[i]['lng'],
                'lat': self.posiciones[i]['lat'],
                'vel': 0,
                'msgs_ejes': self.lista_msgs_ejes[i],
                }
        self.mensajes_circulacion.append(mensaje_circulacion)

    def mostrar(self, mapa):       
        print('Tiempo de recorrido:  ' + str(self.tiempo_recorrido) + ' horas')
        print('Número de mensajes de la circulación:  ' + str(self.num_mensajes))

        # Puntos de origen y destino
        location = [self.origen[1], self.origen[0]]
        html =  '<b>Inicio de la circulación</b>' +\
                '<br><b>Vagón: </b>' + self.vagon +\
                '<br><b>Latitud: </b>' + str(round(self.origen[1],5)) +\
                '<br><b>Longitud: </b>' + str(round(self.origen[0],5))
        popup = folium.Popup(html = html, max_width=200)
        marker = folium.CircleMarker(location = location, radius = 10, popup = popup, color="green", fill = True, fill_color = "blue")
        marker.add_to(mapa)
        location = [self.destino[1], self.destino[0]]
        html =  '<b>Final de la circulación</b>' +\
                '<br><b>Vagón: </b>' + self.vagon +\
                '<br><b>Latitud: </b>' + str(round(self.destino[1],5)) +\
                '<br><b>Longitud: </b>' + str(round(self.destino[0],5))
        popup = folium.Popup(html = html, max_width=200)
        marker = folium.CircleMarker(location = location, radius = 10, popup = popup, color="darkred", fill = True, fill_color = "red")
        marker.add_to(mapa)

        i = 0
        for msg in self.mensajes_circulacion:
            i  += 1
            if i == 3:
                location = [msg['lat'], msg['lng']]
                folium.Circle(
                radius=5000,
                location = location,
                popup="posición",
                color="grey",
                fill=False,
                ).add_to(mapa)
                i = 0

    def ejecutar_simulacion(self):
        print('Vagón: {}, en: {}'.format(self.vagon, datetime.now()))
        print('url: ' + str(self.settings.url_msg_circ))
        print('auth: ' + str(self.settings.auth))
        print ('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        for msg in self.mensajes_circulacion:
            now = datetime.now() + msg['dt']
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            msg['dt'] = dt_string
            r = requests.post (self.settings.url_msg_circ, auth = self.settings.auth, json = msg)

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

class SimuladorCirculacion ():
    def __init__(self, composicion, pk_origen, pk_destino, tiempo_recorrido, tiempo_intervalo):
        self.composicion = composicion
        self.origen = pk_origen
        self.destino = pk_destino
        self.circulaciones = []
        for vagon in composicion:
            ciculacion_vagon = CirculacionVagon(vagon, pk_origen, pk_destino, tiempo_recorrido, tiempo_intervalo)
            self.circulaciones.append(ciculacion_vagon)

    def mostrar(self, mapa):
        print ('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print ('Desde: ' + str(self.origen[0]) + ', ' + str(self.origen[1]))
        print ('Hasta: ' + str(self.destino[0]) + ', ' + str(self.destino[1]))
        print('Vagones: ')
        for vagon in self.composicion:
            print(str(vagon))
        print ('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        self.circulaciones[0].mostrar(mapa)
    
    def ejecutar_simulacion(self):
        print('Iniciando simulación de circulación en: {}'.format(datetime.now()))
        for circulacion in self.circulaciones:
            circulacion.ejecutar_simulacion()

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CABIO DE ANCHO
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
class SimuladorCambio():
    def __init__(self, composicion, cambiador, sentido):
        self.settings = Settings()
        self.ejes = []
        self.vagones = []
        for vagon in composicion:
            self.vagones.append(vagon['codigo'])
            self.ejes.extend(vagon['ejes'])
        # Cargamos codigo cambiador y sentido del cambio
        self.cambiador = cambiador
        self.sentido = sentido    

        # Componentes del MENSAJE a enviar
        # Mensajes de ejes
        self.msgs_ejes = []
        i = 0
        tiempo_cambio = timedelta (seconds = 21.321)
        # Para cada eje de la composición generamos 1 mensaje y lo guardamos en msg_ejes
        for eje in self.ejes:
            mensaje = mensaje_cambio(self.settings, eje)
            inicio_cambio = datetime.now() + tiempo_cambio *i
            mensaje['inicio'] = inicio_cambio.strftime("%Y-%m-%d %H:%M:%S")
            self.msgs_ejes.append(mensaje)   
            i= i+1
        # Generamos 1 mensaje completo de la operación de cambio
        self.mensaje_cambio = \
            {
            'dt': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'cambiador': self.cambiador,
            'sentido': self.sentido,
            'msgs_ejes': self.msgs_ejes,
            }

    def ejecutar_simulacion(self):
        print('Iniciando simulación de operación de cambio.')
        print('Cambiador: {} - Vagones: {}  - {}'.format(self.cambiador, self.vagones, datetime.now()))
        print('url: ' + str(self.settings.url_msg_circ))
        print('auth: ' + str(self.settings.auth))
        r = requests.post (self.settings.url_cambio, auth = self.settings.auth, json = self.mensaje_cambio)
        print(r.json)
        print(r.status_code)