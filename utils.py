import numpy as np
from datetime import datetime, timedelta

# Rampa velocidades
def calcular_velocidades (num_mensajes):
    '''  Devolvemos un array con las velocidades de cada posición
    '''
    velocidades = []
    velocidad = 20
    velocidad_anterior = 20
    tendencia = 1
    for i in range(num_mensajes + 1):
        velocidad = velocidad_anterior + tendencia * np.random.normal(5, 5, size = 1)[0].round(2)
        if velocidad > 110:
            tendencia = -1
        if velocidad < 0:
            velocidad = 0
            tendencia = 1
        velocidad_anterior = velocidad   
        velocidades.append(velocidad)
    
    return velocidades
        
def calcular_posiciones(num_mensajes, origen, destino):
    ''' Hacemos una interferencia lineal y calculamos posiciones uniformemente distribuidas y en línea 
        recta.
    '''
    posiciones = []
    intervalo_lng = (destino[0] - origen[0])/num_mensajes
    intervalo_lat = (destino[1] - origen[1])/num_mensajes
    posicion = {'lng': origen[0], 'lat': origen[1]}
    for i in range(num_mensajes + 1):
        lng = origen[0] + i * intervalo_lng
        lat = origen[1] + i * intervalo_lat
        posicion = {'lng': lng, 'lat': lat}
        posiciones.append(posicion)
    return posiciones

def calcular_tiempos(num_mensajes, tiempo_intervalo):
    ''' Hacemos un array de timedeltas. Cuando montemos el array de mensajes final le sumaremos los timedeltas al 
        momento de inicio de la simulación
    '''
    td = timedelta (seconds = tiempo_intervalo)
    tiempos = []
    for i in range(num_mensajes + 1):
        tiempo = i * td
        tiempos.append(tiempo)
    return tiempos


def generar_1_msg_de_1_eje (settings, eje):
    ''' 1 Mensaje de 1 eje que luego se añade los mensajes de los demás ejes para formar el mensaje de
        circulación correspondiente a 1 posición en la simulación
    '''
    mensaje_eje = {
        'eje': eje,
        'tempa' : settings.temperatura(),
        'tempb' : settings.temperatura(),
        'axMa': settings.aceleraciones_eje('x', 'Max'),
        'axMb': settings.aceleraciones_eje('x', 'Max'),
        'ayMa': settings.aceleraciones_eje('y', 'Max'),
        'ayMb': settings.aceleraciones_eje('y', 'Max'),
        'azMa': settings.aceleraciones_eje('z', 'Max'),
        'azMb': settings.aceleraciones_eje('z', 'Max'),
        'axmeda': settings.aceleraciones_eje('x', 'med'),
        'axmedb': settings.aceleraciones_eje('x', 'med'),
        'aymeda': settings.aceleraciones_eje('y', 'med'),
        'aymedb': settings.aceleraciones_eje('y', 'med'),
        'azmeda': settings.aceleraciones_eje('z', 'med'),
        'azmedb': settings.aceleraciones_eje('z', 'med'),
        'fxa' : settings.aceleraciones_eje('x', 'frec'),
        'fxb' : settings.aceleraciones_eje('x', 'frec'),
        'fya' : settings.aceleraciones_eje('y', 'frec'),
        'fyb' : settings.aceleraciones_eje('y', 'frec'),
        'fza' : settings.aceleraciones_eje('z', 'frec'),
        'fzb' : settings.aceleraciones_eje('z', 'frec'),
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


def mensaje_cambio (settings, eje):
    valores_cambio = settings.valores_cambio()
    mensaje = \
    {
        'eje':eje,
        'inicio':datetime.now(),
        'V':valores_cambio.V,
        'FV':valores_cambio.FV,
        'tdaM':valores_cambio.tdaM,
        'fdaM':valores_cambio.fdaM,
        'ddaM':valores_cambio.ddaM,
        'tcaM':valores_cambio.tcaM,
        'fcaM':valores_cambio.fcaM,
        'dcaM':valores_cambio.dcaM,
        'team':valores_cambio.team,
        'feam':valores_cambio.feam,
        'deam':valores_cambio.deam,
        'tdbM':valores_cambio.tdbM,
        'fdbM':valores_cambio.fdbM,
        'ddbM':valores_cambio.ddbM,
        'tcbM':valores_cambio.tcbM,
        'fcbM':valores_cambio.fcbM,
        'dcbM':valores_cambio.dcbM,
        'tebm':valores_cambio.tebm,
        'febm':valores_cambio.febm,
        'debm':valores_cambio.debm
    }
    return mensaje
