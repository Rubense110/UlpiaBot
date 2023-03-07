import requests

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
        -- when a country forms another one it must be specified by the user, as this means that cosuntry does not exists in the old data
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

def arreglaPlayers(csvNew,csvOld):
    fileNew= open(csvNew,"r")
    fileOld= open(csvOld,"r")
    replacement=""
    ls= list(i for i in fileNew)
    ls2=list(i for i in fileOld)
    for line in ls:
        for line2 in ls2:
            linealista=line.split(",")
            linealista2=line2.split(",")
            if(linealista[0] == linealista2[0]):
                linealista2[1] = linealista[1]
                cambios =",".join(linealista2)
                replacement+=cambios
    fileNew.close()
    fileOld.close()
    fout=open (csvOld, "w+")
    fout.write(replacement)
    fout.close()

def listaTags(csv):
    '''
    returns a list of the first element from all rows of a csv file
    '''
    file= open (csv, "r")
    res= list()
    for line in file:
        tag = line.split(",")[0]
        res.append(tag)
    return res
    
def escribeTag(csv,tagFormador,formable,apikey,save):
    enlace = "https://skanderbeg.pm/api.php?key="+apikey+"&scope=getCountryData&save="+save+"&country="+tagFormador+"&value=player;total_development;overall_strength;monthly_income;FL;innovativeness;max_manpower;spent_total;provinces;armyStrength;average_monarch;buildings_value;total_mana_spent_on_deving;qualityScore;spent_on_advisors&format=csv"
    peticion = requests.get(enlace).text
    file= open(csv, "r")
    replacement=""
    for line in file:
        linealista=line.split(",")
        if(linealista[0] == formable):
            peticion2= peticion.split(",")
            peticion2[0] = formable
            peticionUpdated= ",".join(peticion2)
            replacement += peticionUpdated
        else:
            replacement+=",".join(linealista)              
    file.close()
    fout= open (csv, "w+")
    fout.write(replacement)
    fout.close()

def copiaTag(csvNew,csvOld,tag):
    file= open(csvNew, "r")
    lineaTag=""
    replacement=""
    
    for line in file:
        linealista= line.split(",")
        if(linealista[0] == tag):
            lineaTag= ",".join(linealista)
    file.close()
    
    file2= open(csvOld,"r")
    for line in file2:
        linealista = line.split(",")
        if(linealista[0] == tag):
            print("if")
            cambios=lineaTag
            replacement+=cambios
        else:
            cambios= ",".join(linealista)
            replacement+=cambios
    print(replacement)
    file2.close
    fout= open (csvOld, "w+")
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