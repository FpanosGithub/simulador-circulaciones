import numpy as np
from datetime import timedelta

TEMPERATURA_MEDIA = 15.0
TEMPERATURA_MINIMA = 10.0
TEMPERATURA_MAXIMA = 50.0
VELOCIDAD_MEDIA = 15.6
VELOCIDAD_MAXIMA = 27.8
DESVIACION_TIPICA_VELOCIDAD = 2
ACC_TIPICA_VEHICULO = 0.05
ACC_TIPICA_EJE_X = 2.1
ACC_TIPICA_EJE_Y = 3.4
ACC_TIPICA_EJE_Z = 5.2
DESVIACION_TIPICA_ACELERACIONES_X = 0.05
DESVIACION_TIPICA_ACELERACIONES_Y = 0.2
DESVIACION_TIPICA_ACELERACIONES_Z = 1.1
LOCAL = True

class Settings ():
    ''' Está hecho con una clase para poder llevar variables de estado de un módulo a otro sin tener
        que importar un montón de parámetros y funciones. Además podemos simular tendencias como temperatura_subiendo, etc
    '''
    def __init__(self):
        
        if LOCAL:
            self.url_punto_red = 'http://localhost:8000/red_ferr/puntos_red/'
            self.url_vagon = 'http://localhost:8000/material/vagones/'
            self.url_eje = 'http://localhost:8000/material/ejes/'
            self.url_msg_circ = 'http://localhost:8000/streaming/msg_circ'
            self.auth=('admintria', 'admintria')
        else:
            self.url_punto_red = 'https://mercave-backend.azurewebsites.net/red_ferr/puntos_red/'
            self.url_vagon = 'https://mercave-backend.azurewebsites.net/material/vagones/'
            self.url_eje = 'https://mercave-backend.azurewebsites.net/material/ejes/'
            self.url_msg_circ = 'https://mercave-backend.azurewebsites.net/streaming/msg_circ'
            self.auth=('admintria', 'Mercave062023!')
        
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
            self.temp = self.temp + 0.05
        if not self.temp_subiendo:
            self.temp = self.temp - 0.05
        if self.temp >= TEMPERATURA_MAXIMA:
            self.temp_subiendo = False
        if self.temp <= (TEMPERATURA_MINIMA):
            self.temp_subiendo = True       
        return np.random.normal(self.temp, 2, size = 1)[0].round(2)
    
    def velocidades(self, perfil, num_puntos, velocidad_inicial):
        ''' Devuelve un vector de x numero de puntos partiendo de una velocidad inicial y según una tendencia
            Tiene en cuenta los segundos de cada intervalo entre puntos. si el intervalo es más largo, 
            con una aceleración, deceleracion, constantes, la velocidad subirá más en cada intervalo
        '''
        vector_velocidades = []
        if perfil == 'ACELERACION':
            aceleración = ACC_TIPICA_VEHICULO
        elif perfil == 'FRENADA':
            aceleración = (ACC_TIPICA_VEHICULO * -1)
        else:
            aceleración = 0
        velocidad = velocidad_inicial
        for i in range(num_puntos):
            velocidad = velocidad + aceleración * self.tiempo_intervalo
            if velocidad > VELOCIDAD_MAXIMA:
                velocidad = VELOCIDAD_MAXIMA
            if velocidad < 0:
                velocidad = 0
            velocidad_rdm = np.random.normal(velocidad, DESVIACION_TIPICA_VELOCIDAD, size = 1)[0].round(2)
            if velocidad_rdm < 0:
                velocidad_rdm = 0
            vector_velocidades.append(velocidad_rdm)
        return vector_velocidades

    def aceleraciones_eje(self, axis):
        ''' Devuelve un vector de x numero de puntos partiendo de una velocidad inicial y según una tendencia
            Tiene en cuenta los segundos de cada intervalo entre puntos. si el intervalo es más largo, 
            con una aceleración, deceleracion, constantes, la velocidad subirá más en cada intervalo
        '''
        vector_aceleraciones = []
        if axis == 'x':
            aceleración_típica = ACC_TIPICA_EJE_X
            desviacion_tipica = DESVIACION_TIPICA_ACELERACIONES_X
        elif axis == 'y':
            aceleración_típica = ACC_TIPICA_EJE_Y
            desviacion_tipica = DESVIACION_TIPICA_ACELERACIONES_Y
        elif axis == 'z':
            aceleración_típica = ACC_TIPICA_EJE_Z
            desviacion_tipica = DESVIACION_TIPICA_ACELERACIONES_Z

        for i in range(10):
            aceleracion = np.random.normal(aceleración_típica, desviacion_tipica, size = 1)[0].round(2)
            vector_aceleraciones.append(aceleracion)
        
        return vector_aceleraciones