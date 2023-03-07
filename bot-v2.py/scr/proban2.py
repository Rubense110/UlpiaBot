from collections import namedtuple
from aux_funcs import *
import pandas as pd
import numpy as np

Payaso= namedtuple("tag", "tag, jugador, desarrolloTotal, fuerzaPais, income, forceLimit, innovacion, manpower, gastoTotal, provincias, fuerzaEjercito, mediaReyes, valorEdificios, clicks, calidad, consejeros,vacio")
countries = "./data/00_countries.txt"
dictags= parsea(countries)
