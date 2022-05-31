import numpy as np
from datetime import timedelta

# Rampa velocidades
def calcular_velocidades (settings):
    ''' Dividimos en 10 tramos con perfiles de velocidad distintos
        settings nos devuelve vectores de velocidad con el perfil definido y ya "randomizadas"
        Devolvemos un array con las velocidades de cada posición
    '''
    velocidades = []
    velocidad_inicial = 0
    # hacemos 10 tramos
    perfil = ['ACELERACION','MANTENIDA','FRENADA','ACELERACION','MANTENIDA','FRENADA','ACELERACION','FRENADA','ACELERACION','FRENADA']
    # Num puntos por tramo
    ptos_tramo = int(settings.num_mensajes/10)
    for i in range(9):
        vector_velocidades = settings.velocidades(perfil[i], ptos_tramo, velocidad_inicial)
        velocidad_inicial = vector_velocidades[-1]
        velocidades.extend(vector_velocidades)
    # Para asegurar que por un redondeo no se nos quede 1 valor mas o menos, en el último tramo reajustamos 
    # el número de puntos
    ptos_tramo = (settings.num_mensajes - ptos_tramo * 9) + 1
    velocidades.extend(settings.velocidades(perfil[i], ptos_tramo, velocidad_inicial))
    return velocidades
        
def calcular_posiciones(settings, origen, destino):
    ''' Hacemos una interferencia lineal y calculamos posiciones uniformemente distribuidas y en línea 
        recta.
    '''
    posiciones = []
    intervalo_lng = (destino.lng - origen.lng)/settings.num_mensajes
    intervalo_lat = (destino.lat - origen.lat)/settings.num_mensajes
    posicion = {'lng': origen.lng, 'lat': origen.lat}
    for i in range(settings.num_mensajes + 1):
        lng = origen.lng + i * intervalo_lng
        lat = origen.lat + i * intervalo_lat
        posicion = {'lng': lng, 'lat': lat}
        posiciones.append(posicion)
    return posiciones

def calcular_tiempos(settings):
    ''' Hacemos un array de timedeltas. Cuando montemos el array de mensajes final le sumaremos los timedeltas al 
        momento de inicio de la simulación
    '''
    td = timedelta (seconds = settings.tiempo_intervalo)
    tiempos = []
    for i in range(settings.num_mensajes + 1):
        tiempo = i * td
        tiempos.append(tiempo)
    return tiempos

def generar_1_msg_de_1_eje (settings, eje):
    ''' 1 Mensaje de 1 eje que luego se añade los mensajes de los demás ejes para formar el mensaje de
        circulación correspondiente a 1 posición en la simulación
    '''
    tempa = settings.temperatura()
    tempb = settings.temperatura()
    aax = settings.aceleraciones_eje('x')
    aay = settings.aceleraciones_eje('y')
    aaz = settings.aceleraciones_eje('z')
    abx = settings.aceleraciones_eje('x')
    aby = settings.aceleraciones_eje('y')
    abz = settings.aceleraciones_eje('z')
    mensaje_eje = {
        'eje': eje.codigo,
        'tempa' : tempa,
        'tempb' : tempb,
        'aax': aax,
        'aay': aay,
        'aaz': aaz,
        'abx': abx,
        'aby': aby,
        'abz': abz,
    }
    return mensaje_eje

def generar_1_mensaje_de_x_ejes(settings, ejes):  
    ''' Para cada mensaje de circulación generamos un dicionario con los datos de temperaturas y aceleraciones
        de cada uno de los ejes del vagón
    '''
    mensaje_ejes = []
    for eje in ejes:
        mensaje_eje = generar_1_msg_de_1_eje(settings, eje)
        mensaje_ejes.append(mensaje_eje)
    return mensaje_ejes


def componer_mensaje_circulacion (dt,tipo_msg,vagon,lng,lat,vel,msgs_ejes):
    
    mensaje = \
    {
        'dt': dt,
        'tipo_msg': tipo_msg,
        'vagon': vagon,
        'lng': lng,
        'lat': lat,
        'vel': vel,
        'msgs_ejes': msgs_ejes,
    }
    return mensaje