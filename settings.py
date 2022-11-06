import numpy as np
from datetime import timedelta

TEMPERATURA_MEDIA = 15.0
TEMPERATURA_MINIMA = 10.0
TEMPERATURA_MAXIMA = 50.0

ACC_TIPICA_VEHICULO = 0.05
ACC_TIPICA_EJE_X = 2.1
ACC_TIPICA_EJE_Y = 3.4
ACC_TIPICA_EJE_Z = 5.2
FREC_TIPICA = 12

DESVIACION_TIPICA_ACELERACIONES_X = 0.5
DESVIACION_TIPICA_ACELERACIONES_Y = 0.2
DESVIACION_TIPICA_ACELERACIONES_Z = 1.1
LOCAL = True


class ValoresCambio():
    ''' Clase para calcular/simular y guardar los valores de un cambio de ancho'''
    def __init__(self):              
        self.V = np.random.normal(2.77, 0.3, size = 1)[0].round(2)       # Velocidad de entrada m/s
        self.FV = np.random.normal(200, 75, size = 1)[0].round(2)        # Fuerza Vertical (peso en eje) KN
        # VALORES RUEDA A
        self.tdaM = np.random.normal(5000, 100, size = 1)[0].round(2)   # tiempo (ms) desde inicio punto de F máxima en desencerrojamiento
        self.fdaM = np.random.normal(30, 15, size = 1)[0].round(2)       # fuerza (KN) máxima en desencerrojamiento
        self.ddaM = np.random.normal(20, 15, size = 1)[0].round(2)   # desplazamiento (mm) de disco en punto de f máxima en desencerrojamiento
        self.tcaM = np.random.normal(10000, 150, size = 1)[0].round(2)  # tiempo (ms) desde inicio punto de F máxima en cambio
        self.fcaM = np.random.normal(20, 15, size = 1)[0].round(2)       # fuerza (KN) máxima en desencerrojamiento
        self.dcaM = np.random.normal(70, 15, size = 1)[0].round(2)      # desplazamiento (mm) de rueda en punto de F máxima en cambio
        self.team = np.random.normal(15000, 200, size = 1)[0].round(2)  # tiempo (ms) desde inicio punto de F minima en encerrojamiento
        self.feam = np.random.normal(10, 6, size = 1)[0].round(2)       # fuerza (KN) mínima en encerrojamiento
        self.deam = np.random.normal(20, 5, size = 1)[0].round(2)       # desplazamiento (mm) de disco en punto de F mínima en encerrojamiento
        # VALORES RUEDA B 
        self.tdbM = np.random.normal(25000, 200, size = 1)[0].round(2)  # tiempo (ms) desde inicio punto de F máxima en desencerrojamiento
        self.fdbM = np.random.normal(30, 15, size = 1)[0].round(2)       # fuerza (KN) máxima en desencerrojamiento
        self.ddbM = np.random.normal(30, 15, size = 1)[0].round(2)       # desplazamiento (mm) de disco en punto de f máxima en desencerrojamiento
        self.tcbM = np.random.normal(25000, 200, size = 1)[0].round(2)  # tiempo (ms) desde inicio punto de F máxima en cambio
        self.fcbM = np.random.normal(20, 12, size = 1)[0].round(2)       # fuerza (KN) máxima en desencerrojamiento
        self.dcbM = np.random.normal(70, 15, size = 1)[0].round(2)      # desplazamiento (mm) de rueda en punto de F máxima en cambio
        self.tebm = np.random.normal(25000, 200, size = 1)[0].round(2)  # tiempo (ms) desde inicio punto de F minima en encerrojamiento
        self.febm = np.random.normal(10, 11, size = 1)[0].round(2)       # fuerza (KN) mínima en encerrojamiento
        self.debm = np.random.normal(20, 12, size = 1)[0].round(2)       # desplazamiento (mm) de disco en punto de F mínima en encerrojamiento

class Settings ():
    ''' Está hecho con una clase para poder llevar variables de estado de un módulo a otro sin tener
        que importar un montón de parámetros y funciones. Además podemos simular tendencias como temperatura_subiendo, etc
    '''
    def __init__(self):
        
        if (LOCAL==True):
            self.url_msg_circ = 'http://localhost:8000/streaming/msg_circ'
            self.url_cambio = 'http://localhost:8000/streaming/msg_cambio'
            self.auth=('mercave', 'Mercave2022!')
        else:
            self.url_msg_circ = 'https://mercave-back-23.azurewebsites.net/streaming/msg_circ'
            self.url_cambio = 'https://mercave-back-23.azurewebsites.net/streaming/msg_cambio'
            self.auth=('mercave', 'Mercave2022!')

        self.aceleracion_eje_x = 2.1
        self.aceleracion_eje_y = 3.4
        self.aceleracion_eje_z = 5.6
        self.temp = TEMPERATURA_MEDIA
        self.temp_subiendo = True
        self.tiempo_intervalo = 0
        self.tiempo_recorrido =  0
        self.num_mensajes = 0

    def temperatura(self):
        '''Devuelve un valor de temperatura dentro de una secuencia de subida o bajada pero randomizado'''
        if self.temp_subiendo:
            self.temp = self.temp + 5
        if not self.temp_subiendo:
            self.temp = self.temp - 5
        if self.temp >= TEMPERATURA_MAXIMA:
            self.temp_subiendo = False
        if self.temp <= (TEMPERATURA_MINIMA):
            self.temp_subiendo = True       
        return np.random.normal(self.temp, 5, size = 1)[0].round(2)

    def aceleraciones_eje(self, axis, cat):
        ''' Devuelve un vector de x numero de puntos partiendo de una velocidad inicial y según una tendencia
            Tiene en cuenta los segundos de cada intervalo entre puntos. si el intervalo es más largo, 
            con una aceleración, deceleracion, constantes, la velocidad subirá más en cada intervalo
        '''
        if axis == 'x':
            aceleración_típica = ACC_TIPICA_EJE_X
            desviacion_tipica = DESVIACION_TIPICA_ACELERACIONES_X
        elif axis == 'y':
            aceleración_típica = ACC_TIPICA_EJE_Y
            desviacion_tipica = DESVIACION_TIPICA_ACELERACIONES_Y
        elif axis == 'z':
            aceleración_típica = ACC_TIPICA_EJE_Z
            desviacion_tipica = DESVIACION_TIPICA_ACELERACIONES_Z

        if cat == 'Max':
            aceleración_típica = aceleración_típica * 1.5
            desviacion_tipica = desviacion_tipica * 1.5
        if cat == 'frec':
            aceleración_típica = FREC_TIPICA
            desviacion_tipica = 4

        return np.random.normal(aceleración_típica, desviacion_tipica, size = 1)[0].round(2)
        
    def valores_cambio(self):
        valores = ValoresCambio()
        return valores