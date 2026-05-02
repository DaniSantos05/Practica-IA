# Import required dependencies
import numpy as np
import mdptoolbox

class ControlModule:
    def __init__(self):
        """ Dummy constructor to use the Python Class as a namespace """
        pass

    @staticmethod
    def generate_P(probabilidades: np.ndarray, numero_estados: np.int32, numero_acciones: np.int32) -> np.ndarray:
        """ Function that generates the probabilities (transition) matrix """
        #Creamos la matriz llena de ceros como dice el enunciado siendo: nº acciones x nº estados x nº estados
        matriz_transicion = np.zeros((numero_acciones, numero_estados, numero_estados), dtype=np.float64)
        #Desplazamientos posibles de cada acción correspondientemente, 1º Decrementar, 2º Mantener y 3º Incrementar
        efectos_acciones = [[-2, -1, 0], [-1, 0, 1], [0, 1, 2]]
        #Recorremos  cada acción, cada estado actual y cada posible efecto de esa acción, para cada calculamos el estado al que se llegaría y
        #ponemos en la matriz la probabilidad a la que correspondería el efecto
        for accion in range(numero_acciones):
            for estado_actual in range(numero_estados):
                for indice_efecto, desplazamiento in enumerate(efectos_acciones[accion]):
                    estado_siguiente = estado_actual + desplazamiento
                    #Los bordes, evitar salirnos del rango, para evitar
                    if estado_siguiente < 0:
                        estado_siguiente = 0
                    elif estado_siguiente >= numero_estados:
                        estado_siguiente = numero_estados - 1
                    matriz_transicion[accion, estado_actual, estado_siguiente] += probabilidades[accion, indice_efecto]
        return matriz_transicion



    @staticmethod
    def generate_R() -> np.ndarray:
        """ Function that generates the rewards (costs) matrix """
        ### TO BE COMPLETED BY THE STUDENTS ###
        ...

    @staticmethod
    def control_iteration() -> np.int32:
        """ Function that computes one control-iteration """
        ### TO BE COMPLETED BY THE STUDENTS ###
        ...

    @staticmethod
    def control_loop(demand: np.ndarray, 
                     probs: np.ndarray,
                     n_states: np.int32, 
                     n_actions: np.int32,
                     gamma: np.float64) -> np.ndarray:
        """ Function that computes all the required iterations (control-loop) to satisfy the power demand """
        ### TO BE COMPLETED BY THE STUDENTS ###

        ### DUMMY BEHAVIOUR TO PREVENT CRASHING (MUST BE DELETED AFTER THE FULL IMPLEMENTATION) ###
        return np.zeros_like(a=demand, dtype=np.float64)
        ### ###
