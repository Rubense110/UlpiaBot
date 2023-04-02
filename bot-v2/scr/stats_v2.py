import csv
from collections import  namedtuple
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from aux_funcs import *
from conf import *

dictags= parsea(TAGS)
csv_values = ["tag", "jugador", "desarrolloTotal", "fuerzaPais", "income", "forceLimit",
              "innovacion", "manpower", "gastoTotal", "provincias", "fuerzaEjercito", 
              "mediaReyes", "valorEdificios", "clicks", "calidad", "consejeros","vacio"]

def create_dataframe(csv):
    df = pd.read_csv(csv, encoding="utf-8",names=csv_values)
    df = df.drop(df.columns[-1],axis=1) # removes the last column from de dataframe as its empty
    df["tag"] = df["tag"].map(dictags).fillna(df["tag"]) # changue tags for full country names
    df['mediaReyes'] = df['mediaReyes'].str.split("<br>").str[1].str.split('/').apply(lambda x: [float(i) for i in x]).tolist()

    return df

old = create_dataframe(OLD_CSV)
new = create_dataframe(NEW_CSV)

def diff_dataframes():
    tags = old["tag"]
    for i in csv_values[2:len(csv_values)-1]:
        if(old[i].apply(lambda x: isinstance(x, list)).all()): # comprobamos si la columna es de listas
            diff = [[round(x-y,2) for x,y in zip(ln,lo)] for ln,lo in zip(new[i],old[i])]
            print(pd.concat([tags,pd.Series(diff)], axis=1))
        else:
            old_data = old[i]
            new_data = new[i]
            diff = new_data-old_data
            print(pd.concat([tags,diff], axis=1))

diff_dataframes()

#df = df.iloc[:,[0,1,2]] # select only those columns
#df = df.sort_values(by=["desarrolloTotal"], ascending=False) # sort by dev/income/etc






def dev_ordenado(payasete):
    #devuelve el dev por pais+jugador ordenado de mayor a menor
    res= dict()
    for p in payasete:
        clave1= p.tag
        clave2= p.jugador 
        clave= clave1+ " " + clave2
        if clave not in res:
            res[clave]= p.desarrolloTotal
        else:
            pass
    res= dict(sorted(res.items(), key= lambda x:x[1]))
    return res

"""
def variacion_dev(payasete, payasete1):
    res=  dev_ordenado(payasete)
    despues= dev_ordenado(payasete1)

    #como los diccionarios no siguen el mismo "orden" simplemente reescribimos el del save actual con los datos del anterior
    antes=dict()
    for i in despues:
        antes[i]= res.get(i, 0)

    #creamos dict var, volcamos en el los datos de despues(save actual) y luego ordenamos de mayor a menor
    var={}  
    var.update(despues)
    var= dict(sorted(var.items(), key= lambda x:x[1]))
    
    #a cada pais(key) le asocuamos la variacion (diferencia) de var- antes
    for i in antes.keys():
        var[i]= round( var.get(i, 0) - antes.get(i, 0) , 2)

    return var

def grafico_dev(payasete, payasete1):
    #//--------//Llamada a la función auxiliar para variacíon de income de la sesion pasada a la actual 
    var=variacion_dev(payasete1, payasete)

    #//--------//diccionarios {pais jugador:income} ordenados de mayor a menor income.
    #//--------//res->  sesión actual
    #//--------//res2-> sesión pasada
    res= dev_ordenado(payasete)
    res2=dev_ordenado(payasete1)

    #//--------//separamos el pais del jugador (para el save antiguo no hace falta el player)
    tag_player= list(res.keys())
    tag=[i.split()[0] for i in tag_player ]
    player=[i.split()[1] for i in tag_player]

    tag_player2= list(res2.keys())
    tag2=[i.split()[0] for i in tag_player2 ]

    #//--------//valores de income de la variacion y el save actual
    var1=list(var.values())
    dev= list(res.values())


    #//--------//Empezamos a dibujar
    fig, ax1 = plt.subplots()
    #//--------//Grafico de barras horizontales
    ax1.barh(player, dev, height=1, edgecolor= 'black', color= '#d1edf2',align='center')
    
    #//--------//Variables para los for 
    b=0
    g=0
    h=0
    f=len(player)  
    a=len(player)
    r=0
    xtick= ax1.get_xticks()
    ytick= ax1.get_yticks()

    maximoNombre= max(xtick)*0.4

    
    #//-------- Flechitas
    flechita_var= [tag.index(t)  for t in tag]
    flechita_antiguo=[tag2.index(t) for t in tag]
    color_flecha= [x1 - x2 for (x1, x2) in zip(flechita_var, flechita_antiguo )]


    for i in ax1.patches:
        if color_flecha[r]>0:
            plt.text(i.get_width()-i.get_width() -maximoNombre- xtick[1]/3,i.get_y(),
            "↑", fontweight= '1000', color= 'Green',va="bottom")
            r+=1
        
        elif color_flecha[r]==0:
            plt.text(i.get_width()-i.get_width() -maximoNombre- xtick[1]/3,i.get_y(),
            "→", fontweight= '1000', color= '#705d00',va="bottom")
            r+=1
    
        else:
            plt.text(i.get_width()-i.get_width()-maximoNombre- xtick[1]/3,i.get_y(),
            "↓", fontweight= '1000', color= 'Red',va="bottom")
            r+=1


    #//-------- income
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width() +1 ,i.get_y(),
        dev[b], fontweight= 'bold', color= 'Black')
        b+=1
    #//-------- Nombres de los paises
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width()- maximoNombre,i.get_y(),
        tag[g],va="bottom")
        g+=1

    #//-------- Numeritos Izda
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width() - maximoNombre- xtick[1]/4.5,i.get_y(),
        f, fontweight= 'bold', color= 'Black',va="bottom")
        f-=1
    #//-------- Variacion
    TextVar= max(dev) + int(xtick[1])/8

    for i in ax1.patches:
        if var1[h]>=0:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h],1), fontweight= 'bold', color= 'Green',va="bottom")
            h+=1
        else:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h],1), fontweight= 'bold', color= 'Red',va="bottom")
            h+=1

    #//-------- Numeritos dcha
    TextNumIzq= max(dev) + int(xtick[1])
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width()+ TextNumIzq,i.get_y(),
        a, fontweight= 'bold', color= 'Black',va="bottom")
        a-=1

    #//--------//titulo del grafico, textos auxiliares, y malla (descomentar/comentar .grid para activar/desactivar)
    
    plt.title('Desarrollo Total', fontsize= 30, fontweight='bold', color='Black')
    plt.text(TextVar, len(ytick), 'Variación', fontweight='bold', color= 'Black', fontsize= 20)
    ax1.grid(True, color='Gray',linestyle=':', linewidth=0.5)
    ax1.set_xlim(right=max(dev))
    plt.subplots_adjust(left=0.2,bottom=0.03, right=0.55,top=0.95)
    plt.savefig('./data/graphs/dev.png',bbox_inches='tight')
    #print (datosPos)

def calculaStats(ficheroNuevo,ficheroAntiguo):
    new = lee_payasetes(ficheroNuevo)
    old = lee_payasetes(ficheroAntiguo)

    return(
    grafico_dev(new,old),
    )

if __name__ == "main":
    calculaStats()
"""