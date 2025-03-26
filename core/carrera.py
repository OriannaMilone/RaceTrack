import pandas as pd

class Carrera:
    def __init__(self, df: pd.DataFrame):
        """
        Crea una instancia de una carrera a partir de un DataFrame con estructura estándar.
        """
        self.df = df.sort_values(by=["LapNumber", "DriverNumber"]).reset_index(drop=True)
        self.vueltas_totales = int(self.df["LapNumber"].max())
        self.pilotos = self.df["Driver"].unique().tolist()
        self.n_pilotos = len(self.pilotos)
        self.temporada = self.df["Season"].iloc[0] if "Season" in df.columns else None
        self.nombre_gp = self.df["RaceName"].iloc[0] if "RaceName" in df.columns else None

    def get_vuelta(self, n: int) -> pd.DataFrame:
        """
        Devuelve los datos de la vuelta n.
        """
        return self.df[self.df["LapNumber"] == n]

    def get_info_piloto(self, driver_number: int) -> pd.DataFrame:
        """
        Devuelve todos los datos del piloto con el número indicado.
        """
        return self.df[self.df["DriverNumber"] == driver_number]

    def get_clasificacion_vuelta(self, n: int) -> pd.DataFrame:
        """
        Devuelve la clasificación ordenada por posición en la vuelta n.
        """
        vuelta = self.get_vuelta(n)
        return vuelta[["Driver", "Position"]].sort_values(by="Position")

    def get_estadisticas_generales(self) -> dict:
        """
        Devuelve un resumen general de la carrera.
        """
        return {
            "temporada": self.temporada,
            "gran_premio": self.nombre_gp,
            "total_vueltas": self.vueltas_totales,
            "total_pilotos": self.n_pilotos,
        }

    def get_dataframe_completo(self) -> pd.DataFrame:
        """
        Devuelve el DataFrame completo de la carrera.
        """
        return self.df.copy()
