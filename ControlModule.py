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
        #basándonos en lo cerca que queda el estado siguiente respecto a la demanda que queremos.
        for accion in range(numero_acciones):
            for estado_actual in range(numero_estados):
                for estado_siguiente in range(numero_estados):
                    #Normalización de la potencia del estado siguiente
                    potencia_estado_siguiente = estado_siguiente / numero_estados
                    #Definimos lo que falta para la demanda requerida
                    diferencia = demanda_actual - potencia_estado_siguiente
                    #No nos importa si el reactor queda por debajo o encima, la dejamos positiva la diferencia para
                    #evaluar bien cuanta es la diferencia respecto a la demanda
                    coste = np.abs(diferencia)
                    #Normalización de la potencia del estado actual para ver si nos alejamos o acercamos a la demanda
                    potencia_estado_actual = estado_actual / numero_estados
                    #Añadimos penalizaciones de las acciones claramente inútiles en base a la demanda que tenemos actualmente
                    if potencia_estado_actual < demanda_actual and accion == 0:
                        coste = coste *2
                    elif potencia_estado_actual > demanda_actual and accion == 2:
                        coste = coste * 2
                    #Multiplicamos por menos 1, porque el mdptoolbox trabaja con recompensas
                    #Al hacer esto, cuanto mayor sea el coste, menor será la recompensa
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
        #Ejecutamos el algoritmo y nos calcula la politica optima
        r.run()
        #Le pedimos que nos de la politica optima y la guardamos en esta variable
        politica_optima = r.policy
        #Pedimos que nos de la politica optima del estado actual
        #que será aquella que nos de la maxima recompensa
        mejor_accion = politica_optima[estado_actual]
        return np.int32(mejor_accion)

    @staticmethod
    def control_loop(demand: np.ndarray,
                     probs: np.ndarray,
                     n_states: np.int32,
                     n_actions: np.int32,
                     gamma: np.float64) -> np.ndarray:
        """ Function that computes all the required iterations (control-loop) to satisfy the power demand """
        #Creamos la matriz de transicion P
        matriz_transicion = ControlModule.generate_P(probs, n_states, n_actions)
        #Creamos la lista de ceros donde guardaremos la potencia que entrega el reactor en cada instante.
        respuesta = np.zeros_like(demand, dtype=np.float64)
        #Inicializamos el estado inicial del reactor en el nivel inicial de la demanda y definimos los efectos reales de las acciones.
        estado_actual = int(demand[0] * n_states)
        #realizamos este min, porque la demanda puede tener el valor 1, por tanto al multiplicarlo por 100, si la demanda es 1 nos daria un estado fuera del rango, este min lo usamos para controlar esto
        estado_actual = min(estado_actual, n_states - 1)
        #Efectos: decrease [-2,-1,0], maintain [-1,0,1], increase [0,1,2].
        efectos_acciones = [[-2, -1, 0], [-1, 0, 1], [0, 1, 2]]
        #Recorremos cada punto de la demanda
        for t in range(len(demand)):
            demanda_actual_t = demand[t]
            #El MDP decide que acción es la mejor para el estado y demanda actual.
            accion_optima = ControlModule.control_iteration(matriz_transicion, demanda_actual_t, estado_actual, n_states,n_actions,gamma)
            #El reactor ejecuta la acción, pero con un componente de azar en funcion de las probabilidades de acierto y fallo de la accion elegida
            #con np.random.choice elegimos uno de los 3 efectos posibles según las probabilidades del reactor
            probs_de_la_accion = probs[accion_optima]
            desplazamiento_real = np.random.choice(efectos_acciones[accion_optima], p=probs_de_la_accion)
            #Actualizamos el estado
            estado_actual += desplazamiento_real
            #Comprobamos los límites para no salirnos del rango 0-99
            if estado_actual < 0:
                estado_actual = 0
            elif estado_actual >= n_states:
                estado_actual = n_states - 1
            #Guardamos la potencia normalizada
            respuesta[t] = estado_actual / n_states
        #Devolvemos la serie completa de la respuesta del reactor
        return respuesta
