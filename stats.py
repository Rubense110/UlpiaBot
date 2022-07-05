import csv
from collections import  namedtuple
from dataclasses import replace
from modulefinder import replacePackageMap
from unittest.mock import CallableMixin
import matplotlib.pyplot as plt
import matplotlib as mat
from posixpath import split

def escribeArchivo(file,peticion):
    '''
    just a simple function which writes the text content of an API request in a determined file
    '''
    with open (file, "w") as f:
        f.write(peticion)
    f.close

def arreglaCSV(csv):
    '''
    fixes some errors from the .csv archive downloaded from skanderbeg
    known issues currently solved:
        -- when the buildings value is zero it is returned as nothing, resulting in a missing "0" element in that country, which is inserted here
        -- sometimes skanderbeg does not know the player of a certain country despite being labeled as a player country, resulting in the "player"
           element being missing, which is solved labeling that player as "undefined"
    '''

    file= open (csv, "r")
    replacement= ""
    i=0
    for line in file:
        line= line.strip()
        cadena= line.split(",")
        if(line == ""):
            pass    
        elif(len(cadena)<17 ):
            if(cadena[1].isdigit()):
                nombre= ",undefined"+str(i)+","
                cambios= line.replace("," ,nombre,1)
                cambios+="\n"
                replacement+=cambios
                i+=1 
            else:
                cadena.insert(12,"0")
                cambios= ",".join(cadena)
                replacement+=cambios+"\n"
        else:
            replacement+=line+"\n"
    file.close()
    fout= open (csv, "w+")
    fout.write(replacement)
    fout.close()

def listaTags(csv):
    file= open (csv, "r")
    res= list()
    for line in file:
        tag = line.split(",")[0]
        res.append(tag)
    return res
    
def escribeTag(csv,tag,tagSustituto):
    file= open (csv, "r")
    replacement= ""
    for line in file:
        linealista=line.split(",")
        if(linealista[0]==tag):
            linealista[0] = tagSustituto
        replacement+= ",".join(linealista)
    file.close()
    fout= open (csv, "w+")
    fout.write(replacement)
    fout.close()


def parsea(File):
    '''
      returns a dicctionary TAG : CountryName from 00_countries.txt
      can be found at C:\Program Files(x86)\Steam\steamapps\common\Europa Universalis IV\common\country_tags
    '''
    dicc = dict()

    with open (File, encoding= "utf-8") as f:
        for line in f:
            if line.startswith("#") == False and len(line.split(" "))>1:
                base= line.split(" ")
                tag= base[0][:3]

                if(len(base))==2:
                    country= base[1].split("/")[1].split(".")[0]
                elif(len(base))==3:
                    country= base[2].split("/")[1].split(".")[0]
                
                if tag not in dicc:
                    dicc[tag] = country
                
    return(dicc)

Payaso= namedtuple("tag", "tag, jugador, desarrolloTotal, fuerzaPais, income, forceLimit, innovacion, manpower, gastoTotal, provincias, fuerzaEjercito, mediaReyes, valorEdificios, clicks, calidad, consejeros,vacio")
countries = "./data/00_countries.txt"
dictags= parsea(countries)

def lee_payasetes(fichero):
    with open(fichero, encoding='utf-8') as f:
        lector = csv.reader(f)
        
        Payasos= []
        for tag, jugador, desarrolloTotal, fuerzaPais, income, forceLimit, innovacion, manpower, gastoTotal, provincias, fuerzaEjercito, mediaReyes, valorEdificios, clicks, calidad, consejeros, vacio in lector:
            tag= dictags[tag]
            jugador= jugador.replace(" ","")
            desarrolloTotal= int(desarrolloTotal)
            fuerzaPais = float(fuerzaPais)
            income = float(income)
            forceLimit = float(forceLimit)
            innovacion = float(innovacion)
            manpower =   int(manpower)
            gastoTotal = float(gastoTotal)
            provincias = int(provincias)
            fuerzaEjercito = float(fuerzaEjercito)
            mediaReyes1= mediaReyes.split()
            mediaReyes= float(mediaReyes1[0])
            valorEdificios = int(valorEdificios)
            clicks = int(clicks)
            calidad = float(calidad)
            consejeros = float(consejeros)
            vacio = str(vacio)

            p= Payaso(tag, jugador, desarrolloTotal, fuerzaPais, income, forceLimit, innovacion, manpower, gastoTotal, provincias, fuerzaEjercito, mediaReyes, valorEdificios, clicks, calidad, consejeros,vacio )
            Payasos.append(p)

    return Payasos

def dev_ordenado(payasete):
    #devuelve el income por pais+jugador ordenado de mayor a menor
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
    ax1.barh(player, dev, height=1, edgecolor= 'black', color= '#42f5a1',align='center')
    
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
    plt.savefig('./data/graphs/dev.png')
    #print (datosPos)
"""
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
def OverStrenght_ordenado(payasete):
    #devuelve el income por pais+jugador ordenado de mayor a menor
    res= dict()
    for p in payasete:
        clave1= p.tag
        clave2= p.jugador 
        clave= clave1+ " " + clave2
        if clave not in res:
            res[clave]= p.fuerzaPais
        else:
            pass
    res= dict(sorted(res.items(), key= lambda x:x[1]))
    return res

def variacion_OverStrenght(payasete, payasete1):
    res=  OverStrenght_ordenado(payasete)
    despues= OverStrenght_ordenado(payasete1)

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

def grafico_OverStrenght(payasete, payasete1):
    #//--------//Llamada a la función auxiliar para variacíon de income de la sesion pasada a la actual 
    var=variacion_OverStrenght(payasete1, payasete)

    #//--------//diccionarios {pais jugador:income} ordenados de mayor a menor income.
    #//--------//res->  sesión actual
    #//--------//res2-> sesión pasada
    res= OverStrenght_ordenado(payasete)
    res2=OverStrenght_ordenado(payasete1)

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
    ax1.barh(player, dev, height=1, edgecolor= 'black', color= '#42f5a1',align='center')
    
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
        round(dev[b],1), fontweight= 'bold', color= 'Black')
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
    TextVar= max(dev) + int(xtick[1])/5

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
    plt.title('Fuerza De País', fontsize= 30, fontweight='bold', color='Black')
    plt.text(TextVar, len(ytick), 'Variación', fontweight='bold', color= 'Black', fontsize= 20)
    ax1.grid(True, color='Gray',linestyle=':', linewidth=0.5)
    ax1.set_xlim(right=max(dev))
    plt.subplots_adjust(left=0.2,bottom=0.03, right=0.55,top=0.95)
    plt.savefig('./data/graphs/fuerzaPais.png',bbox_inches='tight')    
    #print (datosPos)

"""
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

def income_ordenado(payasete):
    #devuelve el income por pais+jugador ordenado de mayor a menor
    res= dict()
    for p in payasete:
        clave1= p.tag
        clave2= p.jugador 
        clave= clave1+ " " + clave2
        if clave not in res:
            res[clave]= p.income
        else:
            pass
    res= dict(sorted(res.items(), key= lambda x:x[1]))
    return res

def variacion_income(payasete, payasete1):
    res=  income_ordenado(payasete)
    despues= income_ordenado(payasete1)

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

def grafico_income(payasete, payasete1):
    #//--------//Llamada a la función auxiliar para variacíon de income de la sesion pasada a la actual 
    var=variacion_income(payasete1, payasete)

    #//--------//diccionarios {pais jugador:income} ordenados de mayor a menor income.
    #//--------//res->  sesión actual
    #//--------//res2-> sesión pasada
    res= income_ordenado(payasete)
    res2=income_ordenado(payasete1)

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
    ax1.barh(player, dev, height=1, edgecolor= 'black', color= '#42f5a1',align='center')
    
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
        round(dev[b],1), fontweight= 'bold', color= 'Black')
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
    TextVar= max(dev) + int(xtick[1])/6

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
    plt.title('Income', fontsize= 30, fontweight='bold', color='Black')
    plt.text(TextVar, len(ytick), 'Variación', fontweight='bold', color= 'Black', fontsize= 20)
    ax1.grid(True, color='Gray',linestyle=':', linewidth=0.5)
    ax1.set_xlim(right=max(dev))
    plt.subplots_adjust(left=0.2,bottom=0.03, right=0.55,top=0.95)
    plt.savefig('./data/graphs/income.png',bbox_inches='tight')    #print (datosPos)
"""
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

def FL_ordenado(payasete):
    #devuelve el income por pais+jugador ordenado de mayor a menor
    res= dict()
    for p in payasete:
        clave1= p.tag
        clave2= p.jugador 
        clave= clave1+ " " + clave2
        if clave not in res:
            res[clave]= p.forceLimit
        else:
            pass
    res= dict(sorted(res.items(), key= lambda x:x[1]))
    return res

def variacion_FL(payasete, payasete1):
    res=  FL_ordenado(payasete)
    despues= FL_ordenado(payasete1)

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

def grafico_FL(payasete, payasete1):
    #//--------//Llamada a la función auxiliar para variacíon de income de la sesion pasada a la actual 
    var=variacion_FL(payasete1, payasete)

    #//--------//diccionarios {pais jugador:income} ordenados de mayor a menor income.
    #//--------//res->  sesión actual
    #//--------//res2-> sesión pasada
    res= FL_ordenado(payasete)
    res2=FL_ordenado(payasete1)

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
    ax1.barh(player, dev, height=1, edgecolor= 'black', color= '#42f5a1',align='center')
    
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
        round(dev[b]), fontweight= 'bold', color= 'Black')
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
    TextVar= max(dev) + int(xtick[1])/5

    for i in ax1.patches:
        if var1[h]>=0:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h]), fontweight= 'bold', color= 'Green',va="bottom")
            h+=1
        else:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h]), fontweight= 'bold', color= 'Red',va="bottom")
            h+=1

    #//-------- Numeritos dcha
    TextNumIzq= max(dev) + int(xtick[1])
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width()+ TextNumIzq,i.get_y(),
        a, fontweight= 'bold', color= 'Black',va="bottom")
        a-=1

    #//--------//titulo del grafico, textos auxiliares, y malla (descomentar/comentar .grid para activar/desactivar)
    plt.title('Force Limit', fontsize= 30, fontweight='bold', color='Black')
    plt.text(TextVar, len(ytick), 'Variación', fontweight='bold', color= 'Black', fontsize= 20)
    ax1.grid(True, color='Gray',linestyle=':', linewidth=0.5)
    ax1.set_xlim(right=max(dev))
    plt.subplots_adjust(left=0.2,bottom=0.03, right=0.55,top=0.95)
    plt.savefig('./data/graphs/FL.png',bbox_inches='tight')    #print (datosPos)

"""
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

def innovacion_ordenado(payasete):
    #devuelve el income por pais+jugador ordenado de mayor a menor
    res= dict()
    for p in payasete:
        clave1= p.tag
        clave2= p.jugador 
        clave= clave1+ " " + clave2
        if clave not in res:
            res[clave]= p.innovacion
        else:
            pass
    res= dict(sorted(res.items(), key= lambda x:x[1]))
    return res

def variacion_innovacion(payasete, payasete1):
    res=  innovacion_ordenado(payasete)
    despues= innovacion_ordenado(payasete1)

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

def grafico_innovacion(payasete, payasete1):
    #//--------//Llamada a la función auxiliar para variacíon de income de la sesion pasada a la actual 
    var=variacion_innovacion(payasete1, payasete)

    #//--------//diccionarios {pais jugador:income} ordenados de mayor a menor income.
    #//--------//res->  sesión actual
    #//--------//res2-> sesión pasada
    res= innovacion_ordenado(payasete)
    res2=innovacion_ordenado(payasete1)

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
    ax1.barh(player, dev, height=1, edgecolor= 'black', color= '#42f5a1',align='center')
    
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
        round(dev[b]), fontweight= 'bold', color= 'Black')
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
    TextVar= max(dev) + int(xtick[1])/5

    for i in ax1.patches:
        if var1[h]>=0:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h]), fontweight= 'bold', color= 'Green',va="bottom")
            h+=1
        else:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h]), fontweight= 'bold', color= 'Red',va="bottom")
            h+=1

    #//-------- Numeritos dcha
    TextNumIzq= max(dev) + int(xtick[1]*0.5)
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width()+ TextNumIzq,i.get_y(),
        a, fontweight= 'bold', color= 'Black',va="bottom")
        a-=1

    #//--------//titulo del grafico, textos auxiliares, y malla (descomentar/comentar .grid para activar/desactivar)
    plt.title('Innovacion', fontsize= 30, fontweight='bold', color='Black')
    plt.text(TextVar, len(ytick), 'Variación', fontweight='bold', color= 'Black', fontsize= 20)
    ax1.grid(True, color='Gray',linestyle=':', linewidth=0.5)
    ax1.set_xlim(right=max(dev))
    plt.subplots_adjust(left=0.2,bottom=0.03, right=0.55,top=0.95)
    plt.savefig('./data/graphs/innovacion.png',bbox_inches='tight')    #print (datosPos)


"""
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

def manpower_ordenado(payasete):
    #devuelve el income por pais+jugador ordenado de mayor a menor
    res= dict()
    for p in payasete:
        clave1= p.tag
        clave2= p.jugador 
        clave= clave1+ " " + clave2
        if clave not in res:
            res[clave]= p.manpower
        else:
            pass
    res= dict(sorted(res.items(), key= lambda x:x[1]))
    return res

def variacion_manpower(payasete, payasete1):
    res=  manpower_ordenado(payasete)
    despues= manpower_ordenado(payasete1)

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

def grafico_manpower(payasete, payasete1):
    #//--------//Llamada a la función auxiliar para variacíon de income de la sesion pasada a la actual 
    var=variacion_manpower(payasete1, payasete)

    #//--------//diccionarios {pais jugador:income} ordenados de mayor a menor income.
    #//--------//res->  sesión actual
    #//--------//res2-> sesión pasada
    res= manpower_ordenado(payasete)
    res2=manpower_ordenado(payasete1)

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
    ax1.barh(player, dev, height=1, edgecolor= 'black', color= '#42f5a1',align='center')
    
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
        round(dev[b]), fontweight= 'bold', color= 'Black')
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
    TextVar= max(dev) + int(xtick[1])/5

    for i in ax1.patches:
        if var1[h]>=0:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h]), fontweight= 'bold', color= 'Green',va="bottom")
            h+=1
        else:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h]), fontweight= 'bold', color= 'Red',va="bottom")
            h+=1

    #//-------- Numeritos dcha
    TextNumIzq= max(dev) + int(xtick[1])
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width()+ TextNumIzq,i.get_y(),
        a, fontweight= 'bold', color= 'Black',va="bottom")
        a-=1

    #//--------//titulo del grafico, textos auxiliares, y malla (descomentar/comentar .grid para activar/desactivar)
    plt.title('Manpower máximo', fontsize= 30, fontweight='bold', color='Black')
    plt.text(TextVar, len(ytick), 'Variación', fontweight='bold', color= 'Black', fontsize= 20)
    ax1.grid(True, color='Gray',linestyle=':', linewidth=0.5)
    ax1.set_xlim(right=max(dev))
    plt.subplots_adjust(left=0.2,bottom=0.03, right=0.55,top=0.95)
    plt.savefig('./data/graphs/manpower.png',bbox_inches='tight')    #print (datosPos)

"""
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

def gastos_ordenado(payasete):
    #devuelve el income por pais+jugador ordenado de mayor a menor
    res= dict()
    for p in payasete:
        clave1= p.tag
        clave2= p.jugador 
        clave= clave1+ " " + clave2
        if clave not in res:
            res[clave]= p.gastoTotal
        else:
            pass
    res= dict(sorted(res.items(), key= lambda x:x[1]))
    return res

def variacion_gastos(payasete, payasete1):
    res=  gastos_ordenado(payasete)
    despues= gastos_ordenado(payasete1)

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

def grafico_gastos(payasete, payasete1):
    #//--------//Llamada a la función auxiliar para variacíon de income de la sesion pasada a la actual 
    var=variacion_gastos(payasete1, payasete)

    #//--------//diccionarios {pais jugador:income} ordenados de mayor a menor income.
    #//--------//res->  sesión actual
    #//--------//res2-> sesión pasada
    res= gastos_ordenado(payasete)
    res2=gastos_ordenado(payasete1)

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
    ax1.barh(player, dev, height=1, edgecolor= 'black', color= '#42f5a1',align='center')
    
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
        round(dev[b]), fontweight= 'bold', color= 'Black')
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
    TextVar= max(dev) + int(xtick[1])/5

    for i in ax1.patches:
        if var1[h]>=0:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h]), fontweight= 'bold', color= 'Green',va="bottom")
            h+=1
        else:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h]), fontweight= 'bold', color= 'Red',va="bottom")
            h+=1

    #//-------- Numeritos dcha
    TextNumIzq= max(dev) + int(xtick[1]*2)
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width()+ TextNumIzq,i.get_y(),
        a, fontweight= 'bold', color= 'Black',va="bottom")
        a-=1

    #//--------//titulo del grafico, textos auxiliares, y malla (descomentar/comentar .grid para activar/desactivar)
    plt.title('Gasto Total', fontsize= 30, fontweight='bold', color='Black')
    plt.text(TextVar, len(ytick), 'Variación', fontweight='bold', color= 'Black', fontsize= 20)
    ax1.grid(True, color='Gray',linestyle=':', linewidth=0.5)
    ax1.set_xlim(right=max(dev))
    plt.subplots_adjust(left=0.2,bottom=0.03, right=0.55,top=0.95)
    plt.savefig('./data/graphs/gastos.png',bbox_inches='tight')    #print (datosPos)

"""
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

def provincias_ordenado(payasete):
    #devuelve el income por pais+jugador ordenado de mayor a menor
    res= dict()
    for p in payasete:
        clave1= p.tag
        clave2= p.jugador 
        clave= clave1+ " " + clave2
        if clave not in res:
            res[clave]= p.provincias
        else:
            pass
    res= dict(sorted(res.items(), key= lambda x:x[1]))
    return res

def variacion_provincias(payasete, payasete1):
    res=  provincias_ordenado(payasete)
    despues= provincias_ordenado(payasete1)

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

def grafico_provincias(payasete, payasete1):
    #//--------//Llamada a la función auxiliar para variacíon de income de la sesion pasada a la actual 
    var=variacion_provincias(payasete1, payasete)

    #//--------//diccionarios {pais jugador:income} ordenados de mayor a menor income.
    #//--------//res->  sesión actual
    #//--------//res2-> sesión pasada
    res= provincias_ordenado(payasete)
    res2=provincias_ordenado(payasete1)

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
    ax1.barh(player, dev, height=1, edgecolor= 'black', color= '#42f5a1',align='center')
    
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
            plt.text(i.get_width()-i.get_width() -maximoNombre- xtick[1]/2.5,i.get_y(),
            "↑", fontweight= '1000', color= 'Green',va="bottom")
            r+=1
        
        elif color_flecha[r]==0:
            plt.text(i.get_width()-i.get_width() -maximoNombre- xtick[1]/2.5,i.get_y(),
            "→", fontweight= '1000', color= '#705d00',va="bottom")
            r+=1
    
        else:
            plt.text(i.get_width()-i.get_width()-maximoNombre- xtick[1]/2.5,i.get_y(),
            "↓", fontweight= '1000', color= 'Red',va="bottom")
            r+=1


    #//-------- income
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width() +1 ,i.get_y(),
        round(dev[b]), fontweight= 'bold', color= 'Black')
        b+=1
    #//-------- Nombres de los paises
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width()- maximoNombre,i.get_y(),
        tag[g],va="bottom")
        g+=1

    #//-------- Numeritos Izda
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width() - maximoNombre- xtick[1]/4,i.get_y(),
        f, fontweight= 'bold', color= 'Black',va="bottom")
        f-=1
    #//-------- Variacion
    TextVar= max(dev) + int(xtick[1])/5

    for i in ax1.patches:
        if var1[h]>=0:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h]), fontweight= 'bold', color= 'Green',va="bottom")
            h+=1
        else:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h]), fontweight= 'bold', color= 'Red',va="bottom")
            h+=1

    #//-------- Numeritos dcha
    TextNumIzq= max(dev) + int(xtick[1])
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width()+ TextNumIzq,i.get_y(),
        a, fontweight= 'bold', color= 'Black',va="bottom")
        a-=1

    #//--------//titulo del grafico, textos auxiliares, y malla (descomentar/comentar .grid para activar/desactivar)
    plt.title('Provincias', fontsize= 30, fontweight='bold', color='Black')
    plt.text(TextVar, len(ytick), 'Variación', fontweight='bold', color= 'Black', fontsize= 20)
    ax1.grid(True, color='Gray',linestyle=':', linewidth=0.5)
    ax1.set_xlim(right=max(dev))
    plt.subplots_adjust(left=0.2,bottom=0.03, right=0.55,top=0.95)
    plt.savefig('./data/graphs/provincias.png',bbox_inches='tight')    #print (datosPos)

"""
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

def army_ordenado(payasete):
    #devuelve el income por pais+jugador ordenado de mayor a menor
    res= dict()
    for p in payasete:
        clave1= p.tag
        clave2= p.jugador 
        clave= clave1+ " " + clave2
        if clave not in res:
            res[clave]= p.fuerzaEjercito
        else:
            pass
    res= dict(sorted(res.items(), key= lambda x:x[1]))
    return res

def variacion_army(payasete, payasete1):
    res=  army_ordenado(payasete)
    despues= army_ordenado(payasete1)

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

def grafico_army(payasete, payasete1):
    #//--------//Llamada a la función auxiliar para variacíon de income de la sesion pasada a la actual 
    var=variacion_army(payasete1, payasete)

    #//--------//diccionarios {pais jugador:income} ordenados de mayor a menor income.
    #//--------//res->  sesión actual
    #//--------//res2-> sesión pasada
    res= army_ordenado(payasete)
    res2=army_ordenado(payasete1)

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
    ax1.barh(player, dev, height=1, edgecolor= 'black', color= '#42f5a1',align='center')
    
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
            plt.text(i.get_width()-i.get_width() -maximoNombre- xtick[1]/2.8,i.get_y(),
            "↑", fontweight= '1000', color= 'Green',va="bottom")
            r+=1
        
        elif color_flecha[r]==0:
            plt.text(i.get_width()-i.get_width() -maximoNombre- xtick[1]/2.8,i.get_y(),
            "→", fontweight= '1000', color= '#705d00',va="bottom")
            r+=1
    
        else:
            plt.text(i.get_width()-i.get_width()-maximoNombre- xtick[1]/2.8,i.get_y(),
            "↓", fontweight= '1000', color= 'Red',va="bottom")
            r+=1


    #//-------- income
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width() +1 ,i.get_y(),
        round(dev[b]), fontweight= 'bold', color= 'Black')
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
    TextVar= max(dev) + int(xtick[1])/5

    for i in ax1.patches:
        if var1[h]>=0:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h]), fontweight= 'bold', color= 'Green',va="bottom")
            h+=1
        else:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h]), fontweight= 'bold', color= 'Red',va="bottom")
            h+=1

    #//-------- Numeritos dcha
    TextNumIzq= max(dev) + int(xtick[1])
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width()+ TextNumIzq,i.get_y(),
        a, fontweight= 'bold', color= 'Black',va="bottom")
        a-=1

    #//--------//titulo del grafico, textos auxiliares, y malla (descomentar/comentar .grid para activar/desactivar)
    plt.title('Fuerza del Ejército', fontsize= 30, fontweight='bold', color='Black')
    plt.text(TextVar, len(ytick), 'Variación', fontweight='bold', color= 'Black', fontsize= 20)
    ax1.grid(True, color='Gray',linestyle=':', linewidth=0.5)
    ax1.set_xlim(right=max(dev))
    plt.subplots_adjust(left=0.2,bottom=0.03, right=0.55,top=0.95)
    plt.savefig('./data/graphs/fuerzaEjercito.png',bbox_inches='tight')    #print (datosPos)

"""
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

def rey_ordenado(payasete):
    #devuelve el income por pais+jugador ordenado de mayor a menor
    res= dict()
    for p in payasete:
        clave1= p.tag
        clave2= p.jugador 
        clave= clave1+ " " + clave2
        if clave not in res:
            res[clave]= p.mediaReyes
        else:
            pass
    res= dict(sorted(res.items(), key= lambda x:x[1]))
    return res

def variacion_rey(payasete, payasete1):
    res=  rey_ordenado(payasete)
    despues= rey_ordenado(payasete1)

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

def grafico_rey(payasete, payasete1):
    #//--------//Llamada a la función auxiliar para variacíon de income de la sesion pasada a la actual 
    var=variacion_rey(payasete1, payasete)

    #//--------//diccionarios {pais jugador:income} ordenados de mayor a menor income.
    #//--------//res->  sesión actual
    #//--------//res2-> sesión pasada
    res= rey_ordenado(payasete)
    res2=rey_ordenado(payasete1)

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
    ax1.barh(player, dev, height=1, edgecolor= 'black', color= '#42f5a1',align='center')
    
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
            plt.text(i.get_width()-i.get_width() -maximoNombre- xtick[1]/2.8,i.get_y(),
            "↑", fontweight= '1000', color= 'Green',va="bottom")
            r+=1
        
        elif color_flecha[r]==0:
            plt.text(i.get_width()-i.get_width() -maximoNombre- xtick[1]/2.8,i.get_y(),
            "→", fontweight= '1000', color= '#705d00',va="bottom")
            r+=1
    
        else:
            plt.text(i.get_width()-i.get_width()-maximoNombre- xtick[1]/2.8,i.get_y(),
            "↓", fontweight= '1000', color= 'Red',va="bottom")
            r+=1


    #//-------- income
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width()+0.1 ,i.get_y(),
        round(dev[b],2), fontweight= 'bold', color= 'Black')
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
    TextVar= max(dev) + int(xtick[1])/5

    for i in ax1.patches:
        if var1[h]>=0:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h],2), fontweight= 'bold', color= 'Green',va="bottom")
            h+=1
        else:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h],2), fontweight= 'bold', color= 'Red',va="bottom")
            h+=1

    #//-------- Numeritos dcha
    TextNumIzq= max(dev) + int(xtick[1])
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width()+ TextNumIzq,i.get_y(),
        a, fontweight= 'bold', color= 'Black',va="bottom")
        a-=1

    #//--------//titulo del grafico, textos auxiliares, y malla (descomentar/comentar .grid para activar/desactivar)
    plt.title('Media de Líderes', fontsize= 30, fontweight='bold', color='Black')
    plt.text(TextVar, len(ytick), 'Variación', fontweight='bold', color= 'Black', fontsize= 20)
    ax1.grid(True, color='Gray',linestyle=':', linewidth=0.5)
    ax1.set_xlim(right=max(dev))
    plt.subplots_adjust(left=0.2,bottom=0.03, right=0.55,top=0.95)
    plt.savefig('./data/graphs/avg_monarch.png',bbox_inches='tight')    #print (datosPos)

"""
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

def edificios_ordenado(payasete):
    #devuelve el income por pais+jugador ordenado de mayor a menor
    res= dict()
    for p in payasete:
        clave1= p.tag
        clave2= p.jugador 
        clave= clave1+ " " + clave2
        if clave not in res:
            res[clave]= p.valorEdificios
        else:
            pass
    res= dict(sorted(res.items(), key= lambda x:x[1]))
    return res

def variacion_edificios(payasete, payasete1):
    res=  edificios_ordenado(payasete)
    despues= edificios_ordenado(payasete1)

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

def grafico_edificios(payasete, payasete1):
    #//--------//Llamada a la función auxiliar para variacíon de income de la sesion pasada a la actual 
    var=variacion_edificios(payasete1, payasete)

    #//--------//diccionarios {pais jugador:income} ordenados de mayor a menor income.
    #//--------//res->  sesión actual
    #//--------//res2-> sesión pasada
    res= edificios_ordenado(payasete)
    res2=edificios_ordenado(payasete1)

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
    ax1.barh(player, dev, height=1, edgecolor= 'black', color= '#42f5a1',align='center')
    
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
        round(dev[b]), fontweight= 'bold', color= 'Black')
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
    TextVar= max(dev) + int(xtick[1])/5

    for i in ax1.patches:
        if var1[h]>=0:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h]), fontweight= 'bold', color= 'Green',va="bottom")
            h+=1
        else:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h]), fontweight= 'bold', color= 'Red',va="bottom")
            h+=1

    #//-------- Numeritos dcha
    TextNumIzq= max(dev) + int(xtick[1])
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width()+ TextNumIzq,i.get_y(),
        a, fontweight= 'bold', color= 'Black',va="bottom")
        a-=1

    #//--------//titulo del grafico, textos auxiliares, y malla (descomentar/comentar .grid para activar/desactivar)
    plt.title('Valor de Edificios', fontsize= 30, fontweight='bold', color='Black')
    plt.text(TextVar, len(ytick), 'Variación', fontweight='bold', color= 'Black', fontsize= 20)
    ax1.grid(True, color='Gray',linestyle=':', linewidth=0.5)
    ax1.set_xlim(right=max(dev))
    plt.subplots_adjust(left=0.2,bottom=0.03, right=0.55,top=0.95)
    plt.savefig('./data/graphs/valor_edificios.png',bbox_inches='tight')    #print (datosPos)
"""
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

def clicks1_ordenado(payasete):
    #devuelve el income por pais+jugador ordenado de mayor a menor
    res= dict()
    for p in payasete:
        clave1= p.tag
        clave2= p.jugador 
        clave= clave1+ " " + clave2
        if clave not in res:
            res[clave]= p.clicks
        else:
            pass
    res= dict(sorted(res.items(), key= lambda x:x[1]))
    return res

def variacion_clicks1(payasete, payasete1):
    res=  clicks1_ordenado(payasete)
    despues= clicks1_ordenado(payasete1)

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

def grafico_clicks1(payasete, payasete1):
    #//--------//Llamada a la función auxiliar para variacíon de income de la sesion pasada a la actual 
    var=variacion_clicks1(payasete1, payasete)

    #//--------//diccionarios {pais jugador:income} ordenados de mayor a menor income.
    #//--------//res->  sesión actual
    #//--------//res2-> sesión pasada
    res= clicks1_ordenado(payasete)
    res2=clicks1_ordenado(payasete1)

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
    ax1.barh(player, dev, height=1, edgecolor= 'black', color= '#42f5a1',align='center')
    
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
            plt.text(i.get_width()-i.get_width() -maximoNombre- xtick[1]/2.8,i.get_y(),
            "↑", fontweight= '1000', color= 'Green',va="bottom")
            r+=1
        
        elif color_flecha[r]==0:
            plt.text(i.get_width()-i.get_width() -maximoNombre- xtick[1]/2.8,i.get_y(),
            "→", fontweight= '1000', color= '#705d00',va="bottom")
            r+=1
    
        else:
            plt.text(i.get_width()-i.get_width()-maximoNombre- xtick[1]/2.8,i.get_y(),
            "↓", fontweight= '1000', color= 'Red',va="bottom")
            r+=1


    #//-------- income
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width() +1 ,i.get_y(),
        round(dev[b]), fontweight= 'bold', color= 'Black')
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
    TextVar= max(dev) + int(xtick[1])/5

    for i in ax1.patches:
        if var1[h]>=0:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h]), fontweight= 'bold', color= 'Green',va="bottom")
            h+=1
        else:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h]), fontweight= 'bold', color= 'Red',va="bottom")
            h+=1

    #//-------- Numeritos dcha
    TextNumIzq= max(dev) + int(xtick[1])
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width()+ TextNumIzq,i.get_y(),
        a, fontweight= 'bold', color= 'Black',va="bottom")
        a-=1

    #//--------//titulo del grafico, textos auxiliares, y malla (descomentar/comentar .grid para activar/desactivar)
    plt.title('Puntos en Clicks', fontsize= 30, fontweight='bold', color='Black')
    plt.text(TextVar, len(ytick), 'Variación', fontweight='bold', color= 'Black', fontsize= 20)
    ax1.grid(True, color='Gray',linestyle=':', linewidth=0.5)
    ax1.set_xlim(right=max(dev))
    plt.subplots_adjust(left=0.2,bottom=0.03, right=0.55,top=0.95)
    plt.savefig('./data/graphs/clicks.png',bbox_inches='tight')    #print (datosPos)
    
"""
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

def calidad_ordenado(payasete):
    #devuelve el income por pais+jugador ordenado de mayor a menor
    res= dict()
    for p in payasete:
        clave1= p.tag
        clave2= p.jugador 
        clave= clave1+ " " + clave2
        if clave not in res:
            res[clave]= p.calidad
        else:
            pass
    res= dict(sorted(res.items(), key= lambda x:x[1]))
    return res

def variacion_calidad(payasete, payasete1):
    res=  calidad_ordenado(payasete)
    despues= calidad_ordenado(payasete1)

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

def grafico_calidad(payasete, payasete1):
    #//--------//Llamada a la función auxiliar para variacíon de income de la sesion pasada a la actual 
    var=variacion_calidad(payasete1, payasete)

    #//--------//diccionarios {pais jugador:income} ordenados de mayor a menor income.
    #//--------//res->  sesión actual
    #//--------//res2-> sesión pasada
    res= calidad_ordenado(payasete)
    res2=calidad_ordenado(payasete1)

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
    ax1.barh(player, dev, height=1, edgecolor= 'black', color= '#42f5a1',align='center')
    
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
            plt.text(i.get_width()-i.get_width() -maximoNombre- xtick[1]/2.8,i.get_y(),
            "↑", fontweight= '1000', color= 'Green',va="bottom")
            r+=1
        
        elif color_flecha[r]==0:
            plt.text(i.get_width()-i.get_width() -maximoNombre- xtick[1]/2.8,i.get_y(),
            "→", fontweight= '1000', color= '#705d00',va="bottom")
            r+=1
    
        else:
            plt.text(i.get_width()-i.get_width()-maximoNombre- xtick[1]/2.8,i.get_y(),
            "↓", fontweight= '1000', color= 'Red',va="bottom")
            r+=1


    #//-------- income
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width() +1 ,i.get_y(),
        round(dev[b],2), fontweight= 'bold', color= 'Black')
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
    TextVar= max(dev) + int(xtick[1])/5

    for i in ax1.patches:
        if var1[h]>=0:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h],2), fontweight= 'bold', color= 'Green',va="bottom")
            h+=1
        else:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h],2), fontweight= 'bold', color= 'Red',va="bottom")
            h+=1

    #//-------- Numeritos dcha
    TextNumIzq= max(dev) + int(xtick[1])
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width()+ TextNumIzq,i.get_y(),
        a, fontweight= 'bold', color= 'Black',va="bottom")
        a-=1

    #//--------//titulo del grafico, textos auxiliares, y malla (descomentar/comentar .grid para activar/desactivar)
    plt.title('Calidad del Ejército', fontsize= 30, fontweight='bold', color='Black')
    plt.text(TextVar, len(ytick), 'Variación', fontweight='bold', color= 'Black', fontsize= 20)
    ax1.grid(True, color='Gray',linestyle=':', linewidth=0.5)
    ax1.set_xlim(right=max(dev))
    plt.subplots_adjust(left=0.2,bottom=0.03, right=0.55,top=0.95)
    plt.savefig('./data/graphs/calidad.png',bbox_inches='tight')    #print (datosPos)

"""
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

def consejeros_ordenado(payasete):
    #devuelve el income por pais+jugador ordenado de mayor a menor
    res= dict()
    for p in payasete:
        clave1= p.tag
        clave2= p.jugador 
        clave= clave1+ " " + clave2
        if clave not in res:
            res[clave]= p.consejeros
        else:
            pass
    res= dict(sorted(res.items(), key= lambda x:x[1]))
    return res

def variacion_consejeros(payasete, payasete1):
    res=  consejeros_ordenado(payasete)
    despues= consejeros_ordenado(payasete1)

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

def grafico_consejeros(payasete, payasete1):

    #//--------//Llamada a la función auxiliar para variacíon de income de la sesion pasada a la actual 
    var=variacion_consejeros(payasete1, payasete)

    #//--------//diccionarios {pais jugador:income} ordenados de mayor a menor income.
    #//--------//res->  sesión actual
    #//--------//res2-> sesión pasada
    res= consejeros_ordenado(payasete)
    res2=consejeros_ordenado(payasete1)

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
    ax1.barh(player, dev, height=1, edgecolor= 'black', color= '#42f5a1',align='center')
    
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
    
        elif color_flecha[r]<0:
            plt.text(i.get_width()-i.get_width()-maximoNombre- xtick[1]/3,i.get_y(),
            "↓", fontweight= '1000', color= 'Red',va="bottom")
            r+=1
        else:
            pass


    #//-------- income
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width() +1 ,i.get_y(),
        round(dev[b]), fontweight= 'bold', color= 'Black')
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
    TextVar= max(dev) + int(xtick[1])/5

    for i in ax1.patches:
        if var1[h]>=0:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h]), fontweight= 'bold', color= 'Green',va="bottom")
            h+=1
        else:
            plt.text(i.get_width()-i.get_width()+ TextVar,i.get_y(),
            round(var1[h]), fontweight= 'bold', color= 'Red',va="bottom")
            h+=1

    #//-------- Numeritos dcha
    TextNumIzq= max(dev) + int(xtick[1])
    for i in ax1.patches:
        plt.text(i.get_width()-i.get_width()+ TextNumIzq,i.get_y(),
        a, fontweight= 'bold', color= 'Black',va="bottom")
        a-=1

    #//--------//titulo del grafico, textos auxiliares, y malla (descomentar/comentar .grid para activar/desactivar)
    plt.title('Gasto en Consejeros', fontsize= 30, fontweight='bold', color='Black')
    plt.text(TextVar, len(ytick), 'Variación', fontweight='bold', color= 'Black', fontsize= 20)
    ax1.grid(True, color='Gray',linestyle=':', linewidth=0.5)
    ax1.set_xlim(right=max(dev))
    plt.subplots_adjust(left=0.2,bottom=0.03, right=0.55,top=0.95)
    plt.savefig('./data/graphs/consejeros.png',bbox_inches='tight')    #print (datosPos)

"""
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

def calculaStats(ficheroNuevo,ficheroAntiguo):
    new = lee_payasetes(ficheroNuevo)
    old = lee_payasetes(ficheroAntiguo)

    return(
    grafico_dev(new,old),
    grafico_OverStrenght(new,old),
    grafico_income(new,old),
    grafico_FL(new,old),
    grafico_innovacion(new,old),
    grafico_gastos(new, old),
    grafico_manpower(new,old),
    grafico_provincias(new,old),
    grafico_army(new,old),
    grafico_rey(new,old),
    grafico_edificios(new,old),
    grafico_clicks1(new,old),
    grafico_calidad(new,old),
    grafico_consejeros(new,old),
    )