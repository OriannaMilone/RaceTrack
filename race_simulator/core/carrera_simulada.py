import pandas as pd
import time
from core.carrera import Carrera


class SimuladorDeCarrera:
    def __init__(self, carrera: Carrera, tiempo_entre_vueltas: int = 90):
        self.carrera = carrera
        self.vuelta_actual = 0
        self.tiempo_entre_vueltas = tiempo_entre_vueltas
        self.df_simulado = pd.DataFrame()
        self.finalizada = False

    def simular_siguiente_vuelta(self) -> pd.DataFrame:
        """
        Simula la siguiente vuelta y devuelve los datos de esa vuelta.
        """
        if self.finalizada:
            raise Exception("La simulación ya ha finalizado.")

        self.vuelta_actual += 1

        if self.vuelta_actual > self.carrera.vueltas_totales:
            self.finalizada = True
            raise StopIteration("No hay más vueltas que simular.")

        datos_vuelta = self.carrera.get_vuelta(self.vuelta_actual)
        self.df_simulado = pd.concat([self.df_simulado, datos_vuelta], ignore_index=True)

        time.sleep(self.tiempo_entre_vueltas)  # Simula el paso del tiempo real
        return datos_vuelta

    def get_vuelta_actual(self) -> int:
        return self.vuelta_actual

    def get_estado_parcial(self) -> pd.DataFrame:
        """
        Devuelve el estado actual de la simulación (todas las vueltas simuladas hasta ahora).
        """
        return self.df_simulado.copy()

    # def exportar_resultado(self, ruta: str = "SPA_DATA/carrera_simulada.csv"):
    #     self.df_simulado.to_csv(ruta, index=False)

    def esta_finalizada(self) -> bool:
        return self.finalizada
