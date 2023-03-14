from collections import namedtuple
import pandas as pd
import numpy as np
import os

from conf import * 
from aux_funcs import *



Payaso= namedtuple("tag", "tag, jugador, desarrolloTotal, fuerzaPais, income, forceLimit, innovacion, manpower, gastoTotal, provincias, fuerzaEjercito, mediaReyes, valorEdificios, clicks, calidad, consejeros,vacio")
countries = TAGS
dictags= parsea(countries)
csv = NEW_CSV

coso = pd.read_csv(csv, encoding="utf-8",names=["tag", "jugador", "desarrolloTotal", "fuerzaPais", "income", "forceLimit",
                                                "innovacion", "manpower", "gastoTotal", "provincias", "fuerzaEjercito", 
                                                "mediaReyes", "valorEdificios", "clicks", "calidad", "consejeros","vacio"])
coso = coso.drop(coso.columns[-1],axis=1)


print(coso)