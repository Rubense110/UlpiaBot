from http.client import InvalidURL
import os
from discord.ext import commands
from discord import *
from dotenv import load_dotenv
from stats import *
from bs4 import BeautifulSoup
import requests

load_dotenv()                           #bot token
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='>')  #bot prefix ej: >save

# Global section
apikey = "f9944c9936c1fc48b4d3b57bab261710"
save = ""
enlace = "https://skanderbeg.pm/api.php?key="+apikey+"&scope=getCountryData&save="+save+"&country=&value=player;total_development;overall_strength;monthly_income;FL;innovativeness;max_manpower;spent_total;provinces;armyStrength;average_monarch;buildings_value;total_mana_spent_on_deving;qualityScore;spent_on_advisors&format=csv&playersOnly=true"
csvNuevo= ("./data/csv/new.csv")
csvAntiguo= ("./data/csv/old.csv")
contries= ("./data/00_countries.txt")
skanderDown= "The savefile with given ID was not foundSkanderbeg's server might be temporarily down.Otherwise, if you tried to upload a save during a downtime you might need to reupload it.Apologies for the inconvenience."
def actualizaURL():
    global enlace
    global apikey
    global save
    enlace= "https://skanderbeg.pm/api.php?key="+apikey+"&scope=getCountryData&save="+save+"&country=&value=player;total_development;overall_strength;monthly_income;FL;innovativeness;max_manpower;spent_total;provinces;armyStrength;average_monarch;buildings_value;total_mana_spent_on_deving;qualityScore;spent_on_advisors&format=csv&playersOnly=true"
@bot.command(name='dev')
async def stats(ctx):
    await ctx.send("developed by Rubense#6711, contact him if something goes wrong! :)")

@bot.command(name='invite')
async def stats(ctx):
    await ctx.send("Use this link to add me to your server!\nhttps://discord.com/api/oauth2/authorize?client_id=991088679630028842&permissions=3072&scope=bot")

# Commands section
@bot.command(name= 'stats') #stats builder
async def stats(ctx,currentLink, oldLink="",canalID="    1"):
    """
    >stats (current link) (previous session link) (canal id)

    ex1: >stats https://skanderbeg.pm/browse.php?id=xxxxxx
    ex2: >stats https://skanderbeg.pm/browse.php?id=xxxxxx https://skanderbeg.pm/browse.php?id=yyyyyy
    ex3: >stats https://skanderbeg.pm/browse.php?id=xxxxxx https://skanderbeg.pm/browse.php?id=yyyyyy 992546898487558276

    receives two skanderbeg links from an eu4 mp game, the first being the current game session and the later being from
    a previous session, in addition to the server channel id where you want the bot to answer

    if no channel is specified it will answer in the same channel the command was written

    you must send two links in order to specify a channel

    it only requires the current game session link to work but no  difference between that game and the previous session will be displayed 

    only works for mp links
    """

    mat.rcParams['figure.figsize'] = (19.2,10.8)
    global enlace
    global save
    global csvAntiguo
    global csvNuevo
    ctxCommand= ctx
    await ctx.send("Generating graphs...")
    try:
        canal= int(canalID)
    except Exception as e:
        await ctx.send("Incorrect canal Id")
        raise
    try:
        try:
            hasH1 = False
            hasH2 = False
            link1= requests.get(currentLink)
            if(str(currentLink).startswith("https://skanderbeg.pm/browse.php?id=") != True):
                raise Exception("That is not a valid skanderbeg link sir :/")

            if(oldLink !=""):
                if(str(oldLink).startswith("https://skanderbeg.pm/browse.php?id=") != True):
                    raise Exception("That is not a valid skanderbeg link sir :/\nRemember that you must specify a second link if you want to introduce a channel ID ")

                link2= requests.get(oldLink)
                soup2= BeautifulSoup(link2.text, "html.parser")

                hasH1 = True if soup2.h1 != None else False
                if(hasH1  == True):
                    if(soup2.h1.get_text()== skanderDown):
                        raise Exception(str(soup2.h1).replace("<h1>","").replace("</h1>","").replace("<br/>","\n"))

                hasH2 = True if soup2.h2 != None else False
                if(hasH2 == True):
                    if(soup2.h2.get_text().strip()=="No game was set"):
                        raise Exception("Incorrect save ID on second link, check your skanderberg links")

        except requests.exceptions.RequestException: 
            raise Exception("Error, at least 1 incorrect URL")

        soup= BeautifulSoup(link1.text, "html.parser")

        if(bot.get_channel(canal) == None and canalID != "    1"):
            raise Exception("Incorrect discord channel ID")

        hasH1 = True if soup.h1 != None else False 
        if(hasH1  == True):
            if(soup.h1.get_text()== skanderDown):
                raise Exception(str(soup.h1).replace("<h1>","").replace("</h1>","").replace("<br/>","\n"))

        hasH2 = True if soup.h2 != None else False
        if(hasH2 == True):
            if(soup.h2.get_text().strip()=="No game was set"):
                raise Exception("Incorrect save ID on first link check your skanderberg links")
        
        save= currentLink.split("=")[1]
        actualizaURL()
        peticion = requests.get(enlace).text
        escribeArchivo(csvNuevo,peticion)
        arreglaCSV(csvNuevo)
        arreglaCSV(csvNuevo)

        if(oldLink!=""): save= oldLink.split("=")[1]
        actualizaURL()
        peticion = requests.get(enlace).text
        escribeArchivo(csvAntiguo,peticion)
        arreglaCSV(csvAntiguo)
        arreglaCSV(csvAntiguo)

    except Exception as e:
        await ctx.send(e)
        raise  
    
    b=False
    while(b==False):
        try:
            calculaStats(csvNuevo,csvAntiguo)
            await ctx.send("Done")
        
        
            plt.close("all")
            channel= bot.get_channel(canal)
            if(canalID=="    1"):
                await ctx.send(" Development "              ,file=File('./data/graphs/dev.png')) 
                await ctx.send(" Clicks "                   ,file=File('./data/graphs/clicks.png'))
                await ctx.send(" Overall Strenght"          ,file=File('./data/graphs/fuerzaPais.png'))
                await ctx.send(" Income "                   ,file=File('./data/graphs/income.png'))
                await ctx.send(" Force Limit "              ,file=File('./data/graphs/FL.png'))
                await ctx.send(" Innovation "               ,file=File('./data/graphs/innovacion.png'))
                await ctx.send(" Spent in total "           ,file=File('./data/graphs/gastos.png'))
                await ctx.send(" Provinces "                ,file=File('./data/graphs/provincias.png'))
                await ctx.send(" Army Strenght "            ,file=File('./data/graphs/fuerzaEjercito.png'))
                await ctx.send(" Average Monarch stats "    ,file=File('./data/graphs/avg_monarch.png'))
                await ctx.send(" Buildings value "          ,file=File('./data/graphs/valor_edificios.png'))
                await ctx.send(" Army Quality "             ,file=File('./data/graphs/calidad.png'))
                await ctx.send(" Spent on Advisors "        ,file=File('./data/graphs/consejeros.png'))
            else:
                await channel.send(" Development "              ,file=File('./data/graphs/dev.png')) 
                await channel.send(" Clicks "                   ,file=File('./data/graphs/clicks.png'))
                await channel.send(" Overall Strenght"          ,file=File('./data/graphs/fuerzaPais.png'))
                await channel.send(" Income "                   ,file=File('./data/graphs/income.png'))
                await channel.send(" Force Limit "              ,file=File('./data/graphs/FL.png'))
                await channel.send(" Innovation "               ,file=File('./data/graphs/innovacion.png'))
                await channel.send(" Spent in total "           ,file=File('./data/graphs/gastos.png'))
                await channel.send(" Provinces "                ,file=File('./data/graphs/provincias.png'))
                await channel.send(" Army Strenght "            ,file=File('./data/graphs/fuerzaEjercito.png'))
                await channel.send(" Average Monarch stats "    ,file=File('./data/graphs/avg_monarch.png'))
                await channel.send(" Buildings value "          ,file=File('./data/graphs/valor_edificios.png'))
                await channel.send(" Army Quality "             ,file=File('./data/graphs/calidad.png'))
                await channel.send(" Spent on Advisors "        ,file=File('./data/graphs/consejeros.png'))
            b=True
        except ValueError as e:
            if(len(str(e).split(" ")[0].strip("'"))>3):
                await ctx.send("Those saves are not related or you did put them in the incorrect order, or you may have chosen the incorrect tag to replace if that was the case")
                print(e)
                raise Exception
            def check(m):
                return len(m.content) == 3 and m.content in ls and m.channel == ctx.channel
            tagError= str(e).split(" ")[0].strip("'")

            try:
                ls= listaTags(csvAntiguo)
            except Exception as e:
                print(e)

            salida= ""
            for i in ls:
                salida+= str(i)+"\n"
            
            await ctx.send("an error ocurred\n"+tagError+" is not present in the previous save\nmost likely it was formed by another tag\nPrevious session tag list: \n"+salida)
            await ctx.send("please insert the country tag that '"+tagError+"' replaces from the above selection")

            a= False
            while(a==False):
                try:
                    msg = await bot.wait_for("message",timeout= 30)
                except:
                    await ctx.send("time's out, i can't wait all day >.>")
                    raise
                if(msg.author == ctxCommand.author):
                    a=check(msg)
                    if(a==False):
                        await ctx.send("please insert a valid tag from the above list")
                    else:
                        await ctx.send("ok")
                        await ctx.send(tagError+" will replace "+str(msg.content))
                        escribeTag(csvAntiguo,msg.content,tagError)
                        await ctx.send("Generating graphs...")
        except Forbidden as e:
            await ctx.send("I do not have permissions to write in that channel, please retry the command with a valid Channel ID")
            raise Exception

bot.run(TOKEN)

    
    
    
    
    
    
    
    
    
    

