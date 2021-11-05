from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox import options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from time import sleep
from time import time as get_timestamp
from bs4 import BeautifulSoup
import pandas as pd
import requests



class element_has_css_class(object):
    """
    Espera a que el elemento tenga la clase indicada
    """
    def __init__(self, locator, css_class):
        self.locator = locator
        self.css_class = css_class

    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        if self.css_class in element.get_attribute("class"):
            return element
        else:
            return False


def main():
    min_time=30
    # Obtener cookies de sesion
    session = requests.Session()
    t = get_timestamp()
    session.post("https://fanslaliga.laliga.com/api/v2/loginMail", data=dict(
    email="eduard2207@hotmail.com",
    password="UOC.scraping&"
    ), headers={"AppId": "6457fa17-1224-416a-b21a-ee6ce76e9bc0"})
    r_delay = get_timestamp() - t
    sleep(min_time+r_delay*2)
    
    cookies = session.cookies.get_dict()

    # Hay que instalar el driver geckodriver previamente (Para firefox)
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0")
    driver = webdriver.Firefox(profile)
    
    #Accedemos a la liga antes de poner la cookie para evitar cookie-averse
    t = get_timestamp()
    driver.get("https://www.laliga.com/")
    r_delay = get_timestamp() - t

    for key in cookies:
        driver.add_cookie({"name" : key, "value" : cookies[key]})

    #recargamos la página con la cookie ya añadida
    driver.get("https://www.laliga.com/")
    
    WebDriverWait(driver, 20)\
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                      "#onetrust-accept-btn-handler")))\
    .click()

    categorias = driver.find_elements(By.CSS_SELECTOR,".styled__CompetitionMenuItem-sc-7qz1ev-3>a")
    columns = ["liga","jornada","tipo_partido","posición", "id_equipo","equipo","puntos","pj","pg","pe","pp","gf","gc","dg"]
    df = pd.DataFrame(columns = columns)
    sleep(min_time+r_delay*2)

    for el in categorias:
        try:
            t = get_timestamp()
            wait_spinner_ends(driver)
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable(el)).click()
            r_delay = get_timestamp() - t
            sleep(min_time+r_delay*2)

            submenu = el.find_elements(By.XPATH,"../div/div/span/a")
            for sub_el in submenu:
                if sub_el.get_attribute("innerHTML") == "Clasificación":
                    t = get_timestamp()
                    wait_spinner_ends(driver)
                    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(sub_el)).click()
                    r_delay = get_timestamp() - t
                    sleep(min_time+r_delay*2)
                    break


            jornadas_menu = driver.find_element(By.CSS_SELECTOR,".styled__DropdownContainer-sc-1engvts-6 ul")
            jornadas = jornadas_menu.find_elements(By.XPATH,"./li")
            for jornada in jornadas:
                t = get_timestamp()
                wait_spinner_ends(driver)
                WebDriverWait(driver, 20)\
                .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                ".styled__DropdownContainer-sc-1engvts-6")))\
                .click()
                r_delay = get_timestamp() - t
                sleep(min_time+r_delay*2)

                t = get_timestamp()
                wait_spinner_ends(driver)
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable(jornada)).click()
                r_delay = get_timestamp() - t
                sleep(min_time+r_delay*2)

                wait_table_load(driver)
                page_content = driver.page_source                
                soup = BeautifulSoup(page_content, 'html.parser')
                league = get_league_name(soup)
                game_type_list = get_name_games(soup)
                df_table = get_classification_table(soup,league,jornada.get_attribute("innerHTML"),game_type_list)
                df = df.append(df_table, ignore_index=True)

        except Exception as e:
            print(e)
            pass

    df.to_csv("classification_table.csv",header=True,index=False)
    driver.close()

def wait_spinner_ends(driver):
    WebDriverWait(driver, 20).until(element_has_css_class((By.CSS_SELECTOR, '.styled__SpinnerContainer-uwgd15-0'), "hide"))
    check_spots(driver)

def wait_table_load(driver):
    WebDriverWait(driver, 20).until(element_has_css_class((By.CSS_SELECTOR, '.styled__StandingTableBody-e89col-5'), "cDiDQb"))
        
def check_spots(driver):
    driver.execute_script("""
    var element = document.querySelector('#rctfl-widgets-container');
    if (element)
        element.parentNode.removeChild(element);

    var element = document.getElementsByTagName("body")
    element[0].classList.remove("rctfl-blur-page")

    var element = document.querySelector('#rctfl-block-page');
    if (element)
        element.parentNode.removeChild(element);
    """) 

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

if __name__=="__main__":
    main()