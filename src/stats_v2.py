import matplotlib.pyplot as plt
import pandas as pd

from aux_funcs import *
from conf import *

dictags = {}
csv_values, stat_names = [], []
old, new = pd.DataFrame(), pd.DataFrame()
tags, players = pd.Series(), pd.Series()

def initialize_data():
    global dictags, csv_values, stat_names, old, new, tags, players

    dictags= parsea(TAGS)
    csv_values = ["tag", "jugador", "desarrolloTotal", "fuerzaPais", "income", "forceLimit",
                "innovacion", "manpower", "gastoTotal", "provincias", "fuerzaEjercito", 
                "mediaReyes", "valorEdificios", "clicks", "calidad", "consejeros","vacio"]

    stat_names = ["Total Development", "Country Strength", "Income", "Force Limit",
                "Innovativeness", "Manpower", "Total Expenses", "Provinces", "Army Strength",
                "Avg Monarch", "Buildings Value", "Dev Clicks", "Quality", "Spent on Advisors"]
    
    old = create_dataframe(OLD_CSV)
    new = create_dataframe(NEW_CSV)

    tags = new["tag"]
    players = new["jugador"]




def create_dataframe(csv):
    df = pd.read_csv(csv, encoding="utf-8",names=csv_values)
    df = df.drop(df.columns[-1],axis=1) # removes the last column from de dataframe as its empty
    df["tag"] = df["tag"].map(dictags).fillna(df["tag"]) # changue tags for full country names
    df['mediaReyes'] = df['mediaReyes'].str.split("<br>").str[1].str.split('/').apply(lambda x: [float(i) for i in x]).tolist()
    df["mediaReyes"] = [sum(val) for val in df["mediaReyes"]]
    return df



def diff_dataframes():
    
    df_diff = pd.DataFrame()
    for i in csv_values[0:len(csv_values)-1]:
        if(i != "tag" and i != "jugador"):
            if(old[i].apply(lambda x: isinstance(x, list)).all()): # comprobamos si la columna es de listas
                diff = [[round(x-y,2) for x,y in zip(ln,lo)] for ln,lo in zip(new[i],old[i])]
                df_diff[i] = pd.Series(diff)
            else:
                old_data = old[i]
                new_data = new[i]
                diff = new_data-old_data
                df_diff[i] = diff
        else:
            df_diff[i] = new[i]


    return df_diff

def flechitas(data_old, data_new, order): 
        
        res = []
        
        tags_loc = new
        tags_loc.set_index("tag",inplace=True)
        tags_loc = tags_loc.loc[order]
        tags_loc.reset_index(inplace=True)
        tags_loc = list(reversed(list(tags_loc["tag"])))
        new.reset_index(inplace=True)


        for tag in tags_loc: 
            
            if data_old.index(tag) > data_new.index(tag) : res.append("↓")
            elif data_old.index(tag) < data_new.index(tag): res.append("↑")
            else: res.append("→")

        return res

def create_stats():
    
    diff = diff_dataframes()   
    diff_fixed = diff.iloc[:,2:]
    
    #print(diff_fixed)
    for col , _ in diff_fixed.items():

        data = new
        data = data.loc[:, [col, "tag", "jugador"]].sort_values(by= col)
        order = (list(data["tag"]))
        
        diff_loc = diff.loc[:,[col,"tag"]]
        diff_loc.set_index("tag", inplace=True)
        diff_loc = diff_loc.loc[order]
        diff_loc = diff_loc.sort_index(axis=1, ascending=False)
        diff_loc.reset_index(inplace=True)

        fig , ax1 = plt.subplots()
        ax1.barh(data["jugador"],data[col] , height=1, edgecolor= 'black', color= '#d1edf2',align='center')
        
        #  -------------------

        num_players = len(data["jugador"])
        xtick= ax1.get_xticks()
        ytick= ax1.get_yticks()
        maxName= max(xtick)*0.4
        local_diff = diff_loc[col]

        #  -------------------

        TextVar= data[col].max() + int(xtick[1])/8
        tag = list(data["tag"])
        TextNumIzq= data[col].max() + int(xtick[1])+1
        old_data = old.loc[:, [col, "tag", "jugador"]].sort_values(by= col)
        color_flecha = list(reversed(flechitas(list(old_data["tag"]), list(data["tag"]), order)))
        data_new = list(data[col])
        vert_diff = len(xtick)*0.015

        #  -------------------    
        
        for i in ax1.patches:


        #//-------- Data 
            plt.text((xtick[1]-xtick[0])/6 ,ytick[ax1.patches.index(i)]-vert_diff,
            round(data_new[ax1.patches.index(i)]), fontweight= 'bold', color= 'Black')
            
        #//-------- Variacion
            if (local_diff[ax1.patches.index(i)] > 0 ):
                plt.text(i.get_width()-i.get_width()+ TextVar,ytick[ax1.patches.index(i)]-vert_diff,
                round(local_diff[ax1.patches.index(i)],1), fontweight= 'bold', color= 'Green',va="bottom")

            else:
                plt.text(i.get_width()-i.get_width()+ TextVar,ytick[ax1.patches.index(i)]-vert_diff,
                round(local_diff[ax1.patches.index(i)],1), fontweight= 'bold', color= 'Red',va="bottom")
                        
        #//-------- Flechas

            color = "Green" if color_flecha[ax1.patches.index(i)] == "↑" else "Red" if color_flecha[ax1.patches.index(i)] == "↓" else "#705d00"
            plt.text(i.get_width()-i.get_width() - maxName - xtick[1]/2.5,ytick[ax1.patches.index(i)]-vert_diff,
            color_flecha[ax1.patches.index(i)], fontweight= '1000', color= color,va="bottom")
            

        #//-------- Numeritos

            plt.text(i.get_width()-i.get_width()+ TextNumIzq,ytick[ax1.patches.index(i)]-vert_diff,
            num_players, fontweight= 'bold', color= 'Black',va="bottom")
            
            # dcha
            plt.text(i.get_width()-i.get_width() - maxName- xtick[1]/4,ytick[ax1.patches.index(i)]-vert_diff,
            num_players, fontweight= 'bold', color= 'Black',va="bottom")

            num_players-=1
        #//-------- Nombres de los paises

            #plt.text(i.get_width()-i.get_width()- maxName,(i.get_y()+ax1.patches.index[i+1].get_y()/2),
            plt.text(i.get_width()-i.get_width()- maxName,ytick[ax1.patches.index(i)]-vert_diff,
            tag[ax1.patches.index(i)],va="bottom")
    
        
        plt.title(stat_names[diff_fixed.columns.get_loc(col)], fontsize= 30, fontweight='bold', color='Black')
        plt.text(TextVar, len(ytick), 'Variation', fontweight='bold', color= 'Black', fontsize= 20)
        ax1.grid(True, color='Gray',linestyle=':', linewidth=0.5)
        ax1.set_xlim(right=max(data[col]))
        plt.subplots_adjust(left=0.2,bottom=0.03, right=0.55,top=0.95)
        fig.set_size_inches(18,8)
        plt.savefig(f"{GRAPHS}/{col}.png",bbox_inches='tight')
        plt.close()

create_stats()