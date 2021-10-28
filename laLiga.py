# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 19:35:57 2021

@author: mlavador
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

def main():
    url_pages = ['https://www.laliga.com/laliga-santander/clasificacion',
                 'https://www.laliga.com/laliga-smartbank/clasificacion',
                 'https://www.laliga.com/futbol-femenino/clasificacion']
    columns = ["liga","jornada","tipo_partido","posición", "id_equipo","equipo","puntos","pj","pg","pe","pp","gf","gc","dg"]
    df = pd.DataFrame(columns = columns)
    for url in url_pages:
        soup = get_soup(url)
        league = get_league_name(soup)
        game_type_list = get_name_games(soup)
        df_table = get_classification_table(soup,league,'jornada11',game_type_list)
        df = df.append(df_table, ignore_index=True)
        
    df.to_csv("classification_table.csv",header=True,index=False)

   
def get_soup(url):
    """
    Devuelve un elemento BeautifulSoup

    Dada una url devuelve el arbol DOC del html
    """
    page = requests.get(url).text 
    return BeautifulSoup(page, "lxml")

def get_league_name(soup):
    """
    Devuelve un string

    Recoge el nombre de la liga dado el soup
    """
    league = soup.find('h1', attrs={'class': 'styled__TextHeaderStyled-sc-1edycnf-0 idvFtg'})
    return league.text
    
def get_name_games(soup):
    """
    Devuelve una lista

    Recoge el nombre de las distintas tablas según el tipo de partido
    """
    game_type_list = []
    game_type_row=soup.find('ul', attrs={'class': 'styled__ListTabs-bcjnby-2 jRIEjJ'})
    for game_type in game_type_row.find_all('li'):
        game_type_list.append(game_type.text)
    return game_type_list

def get_drop_down(soup):
    """
    Devuelve una lista

    Recoge las jornadas del drop down.
    Esta función está implementada pero no se usa a la espera de implementar selenium
    """
    dropDown = soup.find('div', attrs={'class': 'styled__DropdownContainer-sc-1engvts-6 iOlTMZ'})
    journeys=[]
    for item in dropDown.findAll('li'):
        journeys.append(item.text)
    return journeys

def get_classification_table(soup,league,journey,game_type_list):
    """
    Devuelve una DataFrame

    Recoge la tabla de clasificación de las diferentes ligas.
    """
    tables = soup.findAll('div', attrs={'class': 'styled__StandingTableBody-e89col-5 cDiDQb'})
    columns = ["liga","jornada","tipo_partido","posición", "id_equipo","equipo","puntos","pj","pg","pe","pp","gf","gc","dg"]
    rows = []
    game_type_number = 0
    for table in tables:
        for row in table.find_all('div', attrs={'class':'styled__ContainerAccordion-e89col-11 HquGF'}):
            data_row=[league,journey,game_type_list[game_type_number]]
            for cell in row.find_all('p'):
                data_row.append(cell.text)
            rows.append(data_row)
        game_type_number=game_type_number + 1
    return pd.DataFrame.from_records(rows,columns=columns)

if __name__ == "__main__":
    main()

