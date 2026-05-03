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
                for indice_efecto in range(len(efectos_acciones[accion])):
                    desplazamiento = efectos_acciones[accion][indice_efecto]
                    estado_siguiente = estado_actual + desplazamiento
                    #Los bordes, evitar salirnos del rango, para evitar valores no válidos
                    if estado_siguiente < 0:
                        estado_siguiente = 0
                    elif estado_siguiente >= numero_estados:
                        estado_siguiente = numero_estados - 1
                    matriz_transicion[accion, estado_actual, estado_siguiente] += probabilidades[accion, indice_efecto]
        return matriz_transicion

    @staticmethod
    def generate_R(demanda_actual: np.float64, numero_estados: np.int32, numero_acciones: np.int32) -> np.ndarray:
        """ Function that generates the rewards (costs) matrix """
        #Creamos la matriz llena de ceros como dice el enunciado siendo: nº acciones x nº estados x nº estados
        matriz_recompensas = np.zeros((numero_acciones, numero_estados, numero_estados), dtype=np.float64)
        #Recorremos todas las transiciones del MDP en cada acción, estado actual y siguiente estado vemos la recompensa
        #basandonos en lo cerca que queda el estado siguiente respecto a la demanda que queremos.
        for accion in range(numero_acciones):
            for estado_actual in range(numero_estados):
                for estado_siguiente in range(numero_estados):
                    #Normalizacion de la potencia del estado siguiente
                    potencia_estado_siguiente = estado_siguiente / numero_estados
                    #Definimos lo que falta para la demanda requerida
                    diferencia = demanda_actual - potencia_estado_siguiente
                    #No nos importa si el reactor queda por debajo o encima, la dejamos positiva la diferencia para
                    #evaluar bien cuanta es la diferencia respecto a la demanda
                    coste = np.abs(diferencia)
                    #Normalizacion de la potencia del estado actual para ver si nos alejamos o acercamos a la demanda
                    potencia_estado_actual = estado_actual / numero_estados
                    #Añadimos penalizaciones de las acciones claramente inútiles en base a la demanda que tenemos actualmente
                    if potencia_estado_actual < demanda_actual and accion == 0:
                        coste = coste *2
                    elif potencia_estado_actual > demanda_actual and accion == 2:
                        coste = coste * 2
                    #ASPECTO IMPORTANTE A PREGUNTAR AL PROFESOR: mdptoolbox trabaja con recompensas/costes. Implementamos con recompensas
                    #multiplicamos por menos 1, porque el mdptoolbox trabaja con recompensas
                    #por tanto al hacer esto, cuanto mayor sea el coste, menor sera la recompensa
                    matriz_recompensas[accion, estado_actual, estado_siguiente] = -coste
        return matriz_recompensas

    @staticmethod
    def control_iteration(matriz_transicion: np.ndarray, demanda_actual: np.float64, estado_actual: np.int32, numero_estados: np.int32, numero_acciones: np.int32, factor_descuento: np.float64) -> np.int32:
        """ Function that computes one control-iteration """
        #Una cosa importante para contextualizar: Hemos planteado que supuestamente mdptoolbox trabaja con recompensas y antes ya en generate_R
        #transformamos de costes a recompensas, entonces en el enunciado nos piden minimizar costes y con este enfoque que
        #hemos planteado será basicamente maximizar recompensas.
        #Creamos la matriz de recompensas para la iteración actual en base a la demanda actual
        matriz_recompensas = ControlModule.generate_R(demanda_actual = demanda_actual, numero_estados = numero_estados, numero_acciones = numero_acciones)
        #configuramos el algoritmo de resolucion del MDP mediante esta funcion, que aplica la ecuacion de bellman
        #y ademas genera la politica optima, pero aun no esta inicializado, para que haga todos los calculo
        r = mdptoolbox.mdp.ValueIteration(matriz_transicion,matriz_recompensas,factor_descuento)
        #ejecutamos el algoritmo y nos calcula la politica optima
        r.run()
        #Le pedimos que nos de la politica optima y la guardamos en esta variable
        politica_optima = r.policy
        #pedimos que nos de la politica optima del estado actual
        mejor_accion = politica_optima[estado_actual]
        return np.int32(mejor_accion)

    @staticmethod
    def control_loop(demand: np.ndarray, 
                     probabilidades: np.ndarray,
                     numero_estados: np.int32,
                     numero_acciones: np.int32,
                     factor_descuento: np.float64) -> np.ndarray:
        """ Function that computes all the required iterations (control-loop) to satisfy the power demand """
        ### TO BE COMPLETED BY THE STUDENTS ###

        ### DUMMY BEHAVIOUR TO PREVENT CRASHING (MUST BE DELETED AFTER THE FULL IMPLEMENTATION) ###
        return np.zeros_like(a=demand, dtype=np.float64)
        ### ###
