from ast import Await, While
from http.client import InvalidURL
import os
from tkinter import PROJECTING, W
from discord.ext import commands
from discord import *
from dotenv import load_dotenv
from matplotlib.pyplot import title
from stats import *
from bs4 import BeautifulSoup
import requests

load_dotenv()                           #bot token
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='>',help_command=None,activity= Game(name=">help"))  #bot prefix ej: >save
bot.remove_command('help')

# Global section
apikey = "f9944c9936c1fc48b4d3b57bab261710"
save = ""
ia= "&playersOnly=true"
enlace = "https://skanderbeg.pm/api.php?key="+apikey+"&scope=getCountryData&save="+save+"&country=&value=player;total_development;overall_strength;monthly_income;FL;innovativeness;max_manpower;spent_total;provinces;armyStrength;average_monarch;buildings_value;total_mana_spent_on_deving;qualityScore;spent_on_advisors&format=csv&playersOnly=true"
csvNuevo= ("./data/csv/new.csv")
csvAntiguo= ("./data/csv/old.csv")
contries= ("./data/00_countries.txt")
skanderDown= "The savefile with given ID was not foundSkanderbeg's server might be temporarily down.Otherwise, if you tried to upload a save during a downtime you might need to reupload it.Apologies for the inconvenience."
paises=""
def actualizaURL():
    global enlace
    global apikey
    global save
    enlace= "https://skanderbeg.pm/api.php?key="+apikey+"&scope=getCountryData&save="+save+"&country="+paises+"&value=player;total_development;overall_strength;monthly_income;FL;innovativeness;max_manpower;spent_total;provinces;armyStrength;average_monarch;buildings_value;total_mana_spent_on_deving;qualityScore;spent_on_advisors&format=csv"+ia
embedError= Embed(title="Error",colour=Color.blue())
genericError ="Unknown Error. Possible causes: \n->the skanderbeg links aren't from the same game\n->you wrote the links backwards\n->you entered the wrong tag, if that was the case\n->you set a non colonial nation as a colony ('C')\n\n Please if you are having this error and dont know why, contact me on discord (Rubense#6711) for further detail"

@bot.command()
async def help(ctx):
    embed = Embed(
        title="Help", 
        description="This is a simple discord bot that generates some statistics from an EU4 game thanks to the skanderbeg API", 
        colour=Color.blue(),
        )
    embed.add_field(name = ">stats",value=
    """
    >stats (current link) (previous session link) (canal id)

    ex1: >stats https://skanderbeg.pm/browse.php?id=xxxxxx

    ex2: >stats https://skanderbeg.pm/browse.php?id=xxxxxx https://skanderbeg.pm/browse.php?id=yyyyyy

    ex3: >stats https://skanderbeg.pm/browse.php?id=xxxxxx https://skanderbeg.pm/browse.php?id=yyyyyy 992546898487558276

    -receives two skanderbeg links from an eu4 mp game, 
     the first being the current game session and the later being from a previous session, 
     in addition to the server channel id where you want the bot to answer

    -if no channel is specified it will answer in the same channel the command was written

    -you must send two links in order to specify a channel

    -it only requires the current game session link to work but no  difference between that game and the previous session will be displayed 

    -oly collects data from player countries
    """,
    inline=False)
    embed.add_field(name = "Add me to your server!",value = "https://bit.ly/3P92CZl",inline=True)
    embed.add_field(name = "Developed by Rubense#6711",value="contact him if something goes wrong!",inline=True)

    await ctx.send(embed=embed)

# Commands section
@bot.command(name= 'stats') #stats builder
async def stats(ctx,currentLink, oldLink="",canalID="    1"):

    mat.rcParams['figure.figsize'] = (19.2,10.8)
    global enlace
    global save
    global paises
    global ia
    global csvAntiguo
    global csvNuevo
    global apikey
    ctxCommand= ctx
    await ctx.send(embed=Embed(title="Generating graphs...",colour=Color.blue()))
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
            link1= requests.get(currentLink)
            if(str(currentLink).startswith("https://skanderbeg.pm/browse.php?id=") != True):
                embedError.description="That is not a valid skanderbeg link sir :/"
                await ctx.send(embed=embedError)
                raise 

            if(oldLink !=""):
                if(str(oldLink).startswith("https://skanderbeg.pm/browse.php?id=") != True):
                    embedError.description="That is not a valid skanderbeg link sir :/\nRemember that you must specify a second link if you want to introduce a channel ID"
                    await ctx.send(embed=embedError)
                    raise

                link2= requests.get(oldLink)
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
        actualizaURL()
        peticion = requests.get(enlace).text
        escribeArchivo(csvNuevo,peticion)
        arreglaCSV(csvNuevo)
        arreglaCSV(csvNuevo)



        if(oldLink!=""): 
            save= oldLink.split("=")[1]
            paises= ";".join(listaTags(csvNuevo))
            ia=""
            actualizaURL()
        
        peticion = requests.get(enlace).text
        escribeArchivo(csvAntiguo,peticion)
        arreglaCSV(csvAntiguo)
        arreglaCSV(csvAntiguo)
        arreglaPlayers(csvNuevo,csvAntiguo)


        ia="&playersOnly=true"
        paises = ""

    except Exception as e:
        print(type(e),e)
        raise  
    
    b=False
    while(b==False):
        try:
            calculaStats(csvNuevo,csvAntiguo)
            await ctx.send(embed=Embed(title="Done",colour=Color.blue()))
            plt.close("all")
            channel= bot.get_channel(canal)
            listaFotos=["dev","clicks","fuerzaPais","income","FL","innovacion","gastos","provincias","fuerzaEjercito","avg_monarch","valor_edificios","calidad","consejeros"]
            [await ctx.send(file=File('./data/graphs/'+i+'.png')) for i in listaFotos];b=True if canalID=="    1" else [await channel.send(file=File('./data/graphs/'+i+'.png')) for i in listaFotos];b=True

        except ValueError as e:
            
            def check(m):
                return m.channel == ctx.channel and str(m.content).isupper() and len(m.content) == 3 or m.content == "C"
            
            
            if(str(e).strip().startswith("not enough values to unpack") == True):
                print(type(e).__name__, e)
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
                        embedError.description=cadena[0]+" is not present in the previous save\nmost likely it was formed by another tag \n Please insert the tag that formed "+cadena[0]+"\n if this is a colony or you are having problems with this enter 'C' instead of the tag"
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
                                            arreglaPlayers(csvNuevo,csvAntiguo)
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
            embedError.description="I do not have permissions to write in that channel, please retry the command with a valid Channel ID"
            await ctx.send(embed=embedError)
            raise 
        
        except Exception as e:
            #print(type(e).__name__, e)

            raise

bot.run(TOKEN)