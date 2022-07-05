import os
from discord.ext import commands
from discord import *
from dotenv import load_dotenv
from stats import *
import requests
import sys

load_dotenv()                           #bot token
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='>')  #bot prefix ej: >save



# Global section
apikey = "place your skanderbeg API key here"
save = ""
enlace = "https://skanderbeg.pm/api.php?key="+apikey+"&scope=getCountryData&save="+save+"&country=&value=player;total_development;overall_strength;monthly_income;FL;innovativeness;max_manpower;spent_total;provinces;armyStrength;average_monarch;buildings_value;total_mana_spent_on_deving;qualityScore;spent_on_advisors&format=csv&playersOnly=true"
csvNuevo= ("./data/csv/new.csv")
csvAntiguo= ("./data/csv/old.csv")
contries= ("./data/00_countries.txt")
def actualizaURL():
    global enlace
    global apikey
    global save
    enlace= "https://skanderbeg.pm/api.php?key="+apikey+"&scope=getCountryData&save="+save+"&country=&value=player;total_development;overall_strength;monthly_income;FL;innovativeness;max_manpower;spent_total;provinces;armyStrength;average_monarch;buildings_value;total_mana_spent_on_deving;qualityScore;spent_on_advisors&format=csv&playersOnly=true"

# Commands section
@bot.event                  # error management
async def on_command_error(ctx,error):
    if isinstance(error,commands.errors.MissingRequiredArgument):
        await ctx.send("invalid input :\n"+str(error))


@bot.command(name= 'stats') #stats builder
async def stats(ctx,currentLink, oldLink="",canalID: int=None):
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
    try:    
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
        await ctx.send("An error ocurred, most likely skanderbeg is down")
        sys.exit(1)
    b=False
    while(b==False):
        try:
            await ctx.send("Generating graphs...")
            calculaStats(csvNuevo,csvAntiguo)
            await ctx.send("Done")
        
        
            plt.close("all")
            channel= bot.get_channel(canalID)
            if(canalID==None):
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
            

            await ctx.send("an error ocurrred\n"+tagError+" is not present in the previous session\nmost likely it was formed by another tag\nPrevious session tag list: \n"+salida)
            await ctx.send("please insert the country tag that '"+tagError+"' replaces from the above selection")

            a= False
            while(a==False):
                msg = await bot.wait_for("message")
                if(msg.author == ctxCommand.author):
                    a=check(msg)
                    if(a==False):
                        await ctx.send("please insert a valid tag from the above list")
                    else:
                        await ctx.send("ok")
                        await ctx.send(tagError+" will replace "+str(msg.content))
                        escribeTag(csvAntiguo,msg.content,tagError)


                
                


bot.run(TOKEN)


    
    
    
    
    
    
    
    
    
    

