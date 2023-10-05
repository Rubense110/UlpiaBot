from conf import *
import pandas as pd

csv_values = ["tag", "jugador", "desarrolloTotal", "fuerzaPais", "income", "forceLimit",
            "innovacion", "manpower", "gastoTotal", "provincias", "fuerzaEjercito", 
            "mediaReyes", "valorEdificios", "clicks", "calidad", "consejeros","vacio"]
print(pd.read_csv(OLD_CSV, encoding="utf-8",names=csv_values))
