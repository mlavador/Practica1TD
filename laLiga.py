# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 19:35:57 2021

@author: mlavador, edcogue
"""

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd

def main():
    # Hay que instalar el driver geckodriver previamente (Para firefox)
    driver = webdriver.Firefox()
    driver.get("https://www.laliga.com/")
    WebDriverWait(driver, 20)\
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                      "#onetrust-accept-btn-handler")))\
    .click()

    categorias = driver.find_elements(By.CSS_SELECTOR,".styled__CompetitionMenuItem-sc-7qz1ev-3>a")
    sleep(3)
    columns = ["liga","jornada","tipo_partido","posición", "id_equipo","equipo","puntos","pj","pg","pe","pp","gf","gc","dg"]
    df = pd.DataFrame(columns = columns)
    for el in categorias:
        try:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable(el)).click()
            sleep(5)
            submenu = el.find_elements(By.XPATH,"../div/div/span/a")
            for sub_el in submenu:
                if sub_el.get_attribute("innerHTML") == "Clasificación":
                    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(sub_el)).click()
                    sleep(5)
                    break


            jornadas_menu = driver.find_element(By.CSS_SELECTOR,".styled__DropdownContainer-sc-1engvts-6 ul")
            jornadas = jornadas_menu.find_elements(By.XPATH,"./li")
            for jornada in jornadas:
                WebDriverWait(driver, 20)\
                .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                ".styled__DropdownContainer-sc-1engvts-6")))\
                .click()
                sleep(2)
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable(jornada)).click()
                sleep(5)
                page_content = driver.page_source                
                soup = BeautifulSoup(page_content, 'html.parser')
                league = get_league_name(soup)
                game_type_list = get_name_games(soup)
                df_table = get_classification_table(soup,league,'jornada11',game_type_list)
                df = df.append(df_table, ignore_index=True)

        except Exception as e:
            print(e)
            print("Liga sin jornadas")
            pass
    df.to_csv("classification_table.csv",header=True,index=False)
    sleep(2)
    driver.close()

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

