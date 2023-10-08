import os
from aux_funcs import *
from conf import *
import stats_v2

import traceback
from discord.ext import commands
from discord import *
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import matplotlib as mat
import matplotlib.pyplot as plt
import requests
import xml.etree.ElementTree as ET

#Bot token section
load_dotenv(ENV)                           
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(intents=Intents.all(),command_prefix='>',help_command=None,activity= Game(name=">help"))  #bot prefix ej: >save
bot.remove_command('help')

# Strings
tree = ET.parse('resources\strings.xml')
root = tree.getroot()
help_msg = root.find('help').text
genericError = root.find('unknown_error').text
permissionError = root.find('permission_error').text
skanderDown= root.find('skander_down').text
formationError= root.find('formation_error').text

embedError= Embed(title="Error",colour=Color.blue())

# Global section
apikey = os.getenv("API_KEY")
save = ""
paises=""
ia= "&playersOnly=true"
enlace = actualizaURL(apikey, save, paises, ia)


@bot.command()
async def help(ctx):
    embed = Embed(
        title="Help", 
        description="This is a simple discord bot that generates some statistics from an EU4 game thanks to the skanderbeg API", 
        colour=Color.blue(),
        )
    embed.add_field(name = ">stats",value=help_msg,
    inline=False)
    embed.add_field(name = "Add me to your server!",value = "https://bit.ly/3P92CZl",inline=True)
    embed.add_field(name = "Developed by Rubense#6711",value="contact him if something goes wrong!",inline=True)

    await ctx.send(embed=embed)

# Commands section
@bot.command(name= 'stats') #stats builder
async def stats(ctx,currentLink, oldLink="",canalID="    1"):

    mat.rcParams['figure.figsize'] = (19.2,10.8)
    global enlace; global save; global paises; global ia; global csvAntiguo; global csvNuevo; global apikey

    ctxCommand= ctx
    await ctx.send(embed=Embed(title="Retrieving data...",colour=Color.blue()))
    try:
        canal= int(canalID)
    except Exception as e:
        embedError.description="Incorrect canal Id"
        await ctx.send(embed=embedError)
        raise
    try:
        try:
            hasH1 = False
            hasH2 = False
            print(currentLink)
            link1= reintenta_conexion(currentLink)
            if(str(currentLink).startswith("https://skanderbeg.pm/browse.php?id=") != True):
                embedError.description="That is not a valid skanderbeg link sir :/"
                await ctx.send(embed=embedError)
                raise 

            if(oldLink !=""):
                if(str(oldLink).startswith("https://skanderbeg.pm/browse.php?id=") != True):
                    embedError.description="That is not a valid skanderbeg link sir :/\nRemember that you must specify a second link if you want to introduce a channel ID"
                    await ctx.send(embed=embedError)
                    raise

                link2= reintenta_conexion(oldLink)
                soup2= BeautifulSoup(link2.text, "html.parser")

                hasH1 = True if soup2.h1 != None else False
                if(hasH1  == True):
                    if(soup2.h1.get_text()== skanderDown):
                        embedError.description=str(soup2.h1).replace("<h1>","").replace("</h1>","").replace("<br/>","\n")
                        await ctx.send(embed=embedError)
                        raise

                hasH2 = True if soup2.h2 != None else False
                if(hasH2 == True):
                    if(soup2.h2.get_text().strip()=="No game was set"):
                        embedError.description="Incorrect save ID on second link, check your skanderberg links"
                        await ctx.send(embed=embedError)
                        raise 

        except requests.exceptions.RequestException: 
            embedError.description="Error, at least 1 incorrect URL"
            await ctx.send(embed= embedError)
            raise 

        soup= BeautifulSoup(link1.text, "html.parser")

        if(bot.get_channel(canal) == None and canalID != "    1"):
            embedError.description="Incorrect discord channel ID"
            await ctx.send(embed= embedError)
            raise 

        hasH1 = True if soup.h1 != None else False 
        if(hasH1  == True):
            if(soup.h1.get_text()== skanderDown):
                embedError.description=str(soup.h1).replace("<h1>","").replace("</h1>","").replace("<br/>","\n")
                await ctx.send(embed= embedError)
                raise

        hasH2 = True if soup.h2 != None else False
        if(hasH2 == True):
            if(soup.h2.get_text().strip()=="No game was set"):
                embedError.description="Incorrect save ID on first link check your skanderberg links"
                await ctx.send(embed= embedError)
                raise
        
        save= currentLink.split("=")[1]
        enlace = actualizaURL(apikey, save, paises, ia)
        print(enlace)
        peticion = reintenta_conexion_text(enlace)
        escribeArchivo(csvNuevo,peticion)
        arreglaCSV_v2(csvNuevo)
        arreglaCSV_v2(csvNuevo)


        if(oldLink!=""): 
            save= oldLink.split("=")[1]
            paises= ";".join(listaTags(csvNuevo))
            ia=""
            enlace = actualizaURL(apikey, save, paises, ia)
        
        peticion = reintenta_conexion_text(enlace)
        escribeArchivo(csvAntiguo,peticion)
        arreglaCSV_v2(csvAntiguo)
        arreglaCSV_v2(csvAntiguo)
        arreglaPlayers(csvNuevo,csvAntiguo)


        ia="&playersOnly=true"
        paises = ""

    except Exception as e:
        print(type(e),e)
        raise  
    
    b=False
    await ctx.send(embed=Embed(title="Generating graphs...",colour=Color.blue()))
    while(b==False):
        try:
            
            stats_v2.initialize_data()
            stats_v2.create_stats()
            await ctx.send(embed=Embed(title="Done",colour=Color.blue()))
            plt.close("all")
            channel= bot.get_channel(canal)
            listaFotos=["desarrolloTotal", "fuerzaPais", "income", "forceLimit",
              "innovacion", "manpower", "gastoTotal", "provincias", "fuerzaEjercito", 
              "mediaReyes", "valorEdificios", "clicks", "calidad", "consejeros"]
            [await ctx.send(file=File(f"{GRAPHS}/{i}.png")) for i in listaFotos];
            b=True if canalID=="    1" else [await ctx.send(file=File(f"{GRAPHS}/{i}.png")) 
                                             for i in listaFotos];b=True

        except TypeError as e:
            
            def check(m):
                return m.channel == ctx.channel and str(m.content).isupper() and len(m.content) == 3 or m.content == "C"
            
            
            if(str(e).strip().startswith("not enough values to unpack") == True or
               str(e).strip().startswith("'float' object is not iterable")):
                print("\n#######\n",type(e),type(e).__name__, e,traceback.format_exc(),"\n#######\n")
                res= open(csvAntiguo,"r")
                ls= list(i for i in res)
                for line in ls:
                    line= line.strip()
                    cadena= line.split(",")
                    if(line == ""):
                        pass 
                    elif(len(cadena)==17):
                        pass
                    elif(cadena[2]=="0"):
                        embedError.description=cadena[0]+formationError 
                        await ctx.send(embed=embedError)
                        a=False
                        while(a== False):
                            try:        
                                msg= await bot.wait_for("message",timeout= 30)
                            except:
                                embedError.description="time's out, i can't wait all day >.>"
                                await ctx.send(embed=embedError)
                                raise

                            if(msg.author == ctxCommand.author):
                                a= check(msg)
                                if(a==False):
                                    embedError.description="please insert a valid tag or 'C' for newly formed colonies"
                                    await ctx.send(embed=embedError)
                                else:
                                    if(msg.content == "C"):
                                        copiaTag(csvNuevo,csvAntiguo,cadena[0])
                                    else:
                                        try:
                                            escribeTag(csvAntiguo,msg.content,cadena[0],apikey,save)
                                            arreglaPlayers2(csvNuevo,csvAntiguo)
                                            arreglaCSV_v2(csvAntiguo)
                                            await ctx.send(embed=Embed(title="Generating graphs...",colour=Color.blue()))

                                        except Exception as e:
                                            embedError.description=genericError
                                            await ctx.send(embed=embedError)
                                            raise
                    else:
                        embedError.description=genericError
                        await ctx.send(embed=embedError)
                        raise
            else:
                embedError.description=genericError
                await ctx.send(embed=embedError)
                b=True
                raise  
            

        except Forbidden as e:
            embedError.description=permissionError
            await ctx.send(embed=embedError)
            raise 
        
        except Exception as e:
            #print(type(e).__name__, e)
            raise

bot.run(TOKEN)