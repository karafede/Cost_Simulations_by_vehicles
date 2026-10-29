

import os

# os.chdir('D:/Federico/Mobility/flask_app/static')
os.environ["PYTHONIOENCODING"] = "utf-8"
path_app = os.getcwd() + "/"

import pandas as pd
import numpy as np
import re
from flask import request

import datetime as dt
from datetime import datetime
import json
import folium
import random
import math
import csv
import requests
import datetime
from os import listdir


"""
## ----- set time zone  ONLY for LINUX machine --- #######
import os, time
time.strftime('%X %x %Z')
os.environ['TZ'] = 'Europe/London'
time.tzset()
time.strftime('%X %x %Z')
"""

print("-------PIPPO -----------------------------")

################################################################
################################################################
################################################################
################################################################
################################################################
################################################################


#### use flask to launch the html file##########################
from flask import Flask, render_template, request, render_template_string, make_response, abort, jsonify, redirect, session
from flask_session import Session

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

import uuid
app.config['SECRET_KEY'] = 'karafede75'




@app.errorhandler(404)
def page_not_found(error):
    return render_template('error_404_page.html'), 404  # 404.html


########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
##### ------------------------------------------------------------------------------------------- ######
####### ---- COSTI CHILOMETRICI  (per Silvia Orchi) -------------------------------------------- #######


@app.route('/')
def root():

    longitude = request.args.get('lng', type=float)
    latitude = request.args.get('latitude', type=float)
    print("latitude--->: ", latitude)
    print("longitude--->: ", longitude)
    markers = [
        {
            'lat': longitude,
            'lon': latitude,
            'popup': 'user input pnt.'
        }
    ]
    print(markers)
    session['COSTI_day'] = '2024-02-11'
    session["FUEL_type_tradizionale"] = '0'
    session["FUEL_type_elettrico"] = '0'
    session["FUEL_type_idrogeno"] = '0'
    return render_template("index_costi_chilometrici.html", longitude=longitude, latitude=latitude)


@app.route('/costi_chilometrici/', methods=['GET', 'POST'])
def costi_chilometrici():
    session['COSTI_day'] = '2024-02-11'
    session["FUEL_type_tradizionale"] = '0'
    session["FUEL_type_elettrico"] = '0'
    session["FUEL_type_idrogeno"] = '0'
    session["AVERAGE_CONSUMPTION_TRADIZIONALE"] = ''
    session["AVERAGE_CONSUMPTION_ELETTRICO"] = ''
    session["AVERAGE_CONSUMPTION_IDROGENO"] = ''
    session['costo_finale_tradizionale_EUR'] = 0
    session['costo_finale_elettrico_EUR'] = 0
    session['costo_finale_idrogeno_EUR'] = 0

    session["CONSUMPTION_TRADIZIONALE"] = 0
    session["CONSUMPTION_ELETTRICO"] = 0
    session["CONSUMPTION_IDROGENO"] = 0

    session["prezzo_carburante_tradizionale_EUR"] = 0
    session["prezzo_carburante_elettrico_EUR"] = 0
    session["prezzo_carburante_idrogeno_EUR"] = 0

    session["footnote_prezzo_carburante_tradizionale"] = 'Prezzo medio per litro di Benzina:....'
    session["footnote_prezzo_elettrico"] = 'Prezzo medio per tipo di ricarica Elettrico Casa (3.3kW):....'
    session["footnote_prezzo_idrogeno"] = 'Prezzo medio per Kg di H2 grigio:....'


    return render_template("index_costi_chilometrici.html", session=session)




@app.route('/day_costi_chilometrici/', methods=['GET', 'POST'])
def day_costi_chilometrici():
    if request.method == "POST":

        ###--->> record the ZMU_day in into the Flask Session
        ## TRY if session exists
        try:
            session["COSTI_day"] = datetime.datetime.strptime(
                request.form.get("COSTI_day"), '%Y-%m-%d')
            selected_COSTI_day = session["COSTI_day"]
            print("gotta!!!----->> sessison exist!----- stored COSTI_day from the session:",
                  session["COSTI_day"].strftime('%Y-%m-%d'))  ##--->> only get date
            selected_COSTI_day = selected_COSTI_day.strftime('%Y-%m-%d')
            selected_COSTI_day = str(selected_COSTI_day)
        except:
            selected_COSTI_day = '2024-02-08'
            selected_COSTI_day = session["COSTI_day"]
            print("using stored variable: ", session["COSTI_day"])

        session["FUEL_type_tradizionale"] = '0'
        session["FUEL_type_elettrico"] = '0'
        session["FUEL_type_idrogeno"] = '10'
        session["AVERAGE_CONSUMPTION_TRADIZIONALE"] = ''
        session["AVERAGE_CONSUMPTION_ELETTRICO"] = ''
        session["AVERAGE_CONSUMPTION_IDROGENO"] = ''
        session['costo_finale_tradizionale_EUR'] = ''
        session['costo_finale_elettrico_EUR'] = ''
        session['costo_finale_idrogeno_EUR'] = ''

        ### ---> save date ----################################################
        print("selected_COSTI_day:", selected_COSTI_day)
        # with open(path_app + "static/params/selected_COSTI_day.txt", "w") as file:
        #    file.write(selected_COSTI_day)

        user = session.sid
        print("user:", user)

        print("session user ID:", session.sid)
        # print("full session:", session)
        return render_template("index_costi_chilometrici.html", var_COSTI_day=selected_COSTI_day,
                               user=user)  # var_ZMU_day=session["ZMU_day"]




@app.route('/tipo_alimentazione_tradizionale/', methods=['GET', 'POST'])
def tipo_alimentazione_tradizionale():
    from re import sub
    from decimal import Decimal

    session["AVERAGE_CONSUMPTION_TRADIZIONALE"] = ''
    session["AVERAGE_CONSUMPTION_ELETTRICO"] = ''
    session["AVERAGE_CONSUMPTION_IDROGENO"] = ''
    session['costo_finale_tradizionale_EUR'] = 0
    session['costo_finale_elettrico_EUR'] = 0
    session['costo_finale_idrogeno_EUR'] = 0

    if request.method == "POST":
        try:
            selected_COSTI_day = session["COSTI_day"].strftime('%Y-%m-%d')
            print("day:", selected_COSTI_day)
        except AttributeError:
            selected_COSTI_day = '2024-02-08'
            selected_COSTI_day = session["COSTI_day"]
            print("using stored variable: ", session["COSTI_day"])


        ## TRY if session exists
        try:
            session["FUEL_type_tradizionale"] = request.form.get("FUEL_type_tradizionale")
            selected_FUEL_type_tradizionale = session["FUEL_type_tradizionale"]
            print("-------------------selected_FUEL_type tradizionale:----------------------------------*********", session["FUEL_type_tradizionale"])
        except:
            session["FUEL_type_tradizionale"] = 2
            selected_FUEL_type_tradizionale = session["FUEL_type_tradizionale"]

        try:
            selected_FUEL_type_elettrico = session["FUEL_type_elettrico"]
            print("-------------------selected_FUEL_type elettrico:----------------------------------*********", session["FUEL_type_elettrico"])
        except:
            session["FUEL_type_elettrico"] = 5
            selected_FUEL_type_elettrico = session["FUEL_type_elettrico"]

        try:
            selected_FUEL_type_idrogeno = session["FUEL_type_idrogeno"]
            print("-------------------selected_FUEL_type idrogeno:----------------------------------*********",
                  session["FUEL_type_idrogeno"])
        except:
            session["FUEL_type_idrogeno"] = 10
            selected_FUEL_type_idrogeno = session["FUEL_type_idrogeno"]


        FUEL_TYPE_tradizionale = "Benzina"
        if selected_FUEL_type_tradizionale == '1':
            FUEL_TYPE_tradizionale = "Benzina"
        elif selected_FUEL_type_tradizionale == '2':
            FUEL_TYPE_tradizionale = "Diesel"
        elif selected_FUEL_type_tradizionale == '3':
            FUEL_TYPE_tradizionale = "GPL"
        elif selected_FUEL_type_tradizionale == '4':
            FUEL_TYPE_tradizionale = "Metano"


        try:
            session["FUEL_TRADIZIONALE"] = FUEL_TYPE_tradizionale
            print("------------FUEL TYPE:----------------", FUEL_TYPE_tradizionale)
        except:
            FUEL_TYPE_tradizionale = "Benzina"


        """
        import httplib2
        from bs4 import BeautifulSoup, SoupStrainer
        from urllib.request import Request, urlopen
        http = httplib2.Http()
        import requests
        import pandas as pd
        import json
        import re
        import urllib.request


        ## --->> get link of Ministero dell'ambiente e della sicurezza energetica (Statistiche energetiche e minerarie)
        ### ---->> web scraping.... find the web text containing all the information about fuel prices
        # url = "https://sisen.mase.gov.it/dgsaie/prezzi-settimanali-carburanti"
        # data = requests.get(url).text
        # soup = BeautifulSoup(data, 'html.parser')

        # tags = soup.find_all(attrs={'class': re.compile(r"^ml-2$")})
        # tags = soup.findAll(True, {"class":["ml-2", "text-right"]})

        # from selenium import webdriver
        # from selenium.webdriver.chrome.options import Options
        # from selenium.webdriver.support.ui import Select
        # from selenium.webdriver.common.by import By
        # from selenium import webdriver
        # from selenium.webdriver.support.ui import WebDriverWait
        # from selenium.webdriver.common.by import By
        import time

        from selenium import webdriver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=chrome_options)


        # options = Options()
        # options.add_argument("--headless")
        # driver = webdriver.Chrome(options=options)
        # driver.set_window_size(1224, 1268)
        # driver.get("https://www.ilportaleofferte.it/portaleOfferte/



        driver.get("https://sisen.mase.gov.it/dgsaie/prezzi-settimanali-carburanti")
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.close()
        driver.quit()

        # print("soup--------------", soup)

        # tags = soup.findAll(True, {"class": ["ms-2", "text-right"]})
        # tags = soup.findAll(True, {"class": ["ms-2", "fw-semibold"]})

        list_FUELS = []
        for tag in soup.findAll(True, {"class": ["ms-2", "fw-semibold"]}):
            # print(tag)
            print(tag.text.strip())
            list_FUELS.append(tag.text.strip())
        """


        #### ---- laod TABELLA CARBURANTI in format .CSV-------- ###############################################
        tabella_carburanti_MASE = pd.read_csv(path_app + "/static/prezzi_carburanti_settimanali_2024_05_20.csv")

        price_Benzina = tabella_carburanti_MASE[tabella_carburanti_MASE['NOME_PRODOTTO'] == "Benzina"]['PREZZO'][0]
        price_Benzina_EUR = float((price_Benzina.split(','))[0])
        print("--price_Benzina_EUR----------------------->>>>:", float(price_Benzina_EUR))
        session['price_Benzina'] = price_Benzina

        price_Diesel = tabella_carburanti_MASE[tabella_carburanti_MASE['NOME_PRODOTTO'] == "Gasolio auto"]['PREZZO'][1]
        price_Diesel_EUR = float((price_Diesel.split(','))[0])
        print("--price_Diesel_EUR----------------------->>>>:", float(price_Diesel_EUR))
        session['price_Diesel'] = price_Diesel

        price_GPL = tabella_carburanti_MASE[tabella_carburanti_MASE['NOME_PRODOTTO'] == "GPL"]['PREZZO'][3]
        price_GPL_EUR = float((price_GPL.split(','))[0])
        print("--price_GPL_EUR----------------------->>>>:", float(price_GPL_EUR))
        session['price_GPL'] = price_GPL

        price_Metano = tabella_carburanti_MASE[tabella_carburanti_MASE['NOME_PRODOTTO'] == "Metano"]['PREZZO'][6]
        price_Metano_EUR = float((price_Metano.split(','))[0])
        print("--price_Metano_EUR----------------------->>>>:", float(price_Metano_EUR))
        session['price_Metano'] = price_Metano


        """
        index_Benzina = list_FUELS.index("Benzina")
        price_Benzina = list_FUELS[index_Benzina + 1]
        print("--price Benzina--->:", price_Benzina)
        price_Benzina_EUR = float((price_Benzina.split(','))[0])
        # price_Benzina_EUR = float(Decimal(sub(r'[^\d.]', '', price_Benzina)))
        print("--price_Benzina_EUR----------------------->>>>:", float(price_Benzina_EUR))
        session['price_Benzina'] = price_Benzina


        index_Diesel = list_FUELS.index("Gasolio auto")
        price_Diesel = list_FUELS[index_Diesel + 1]
        print("--price Diesel--->:", price_Diesel)
        price_Diesel_EUR = float((price_Diesel.split(','))[0])
        # price_Diesel_EUR = float(Decimal(sub(r'[^\d.]', '', price_Diesel)))
        session['price_Diesel'] = price_Diesel

        index_GPL = list_FUELS.index("GPL")
        price_GPL = list_FUELS[index_GPL + 1]
        print("--price GPL--->:", price_GPL)
        price_GPL_EUR = float((price_GPL.split(','))[0]) / 1000
        # price_GPL_EUR = float(Decimal(sub(r'[^\d.]', '', price_GPL)))
        print("---price_GPL_EUR----->:", price_GPL_EUR)
        print("---price_GPL----->:", price_GPL)
        session['price_GPL'] = price_GPL

        index_Metano = list_FUELS.index("Metano")
        price_Metano = list_FUELS[index_Metano + 1]
        print("--price Metano--->:", price_Metano)
        price_Metano_EUR = float((price_Metano.split(','))[0])
        # price_Metano_EUR = float(Decimal(sub(r'[^\d.]', '', price_Metano)))
        session['price_Metano'] = price_Metano
        """

        if FUEL_TYPE_tradizionale == 'Benzina':
            prezzo_carburante =  price_Benzina  #1.83
            session["prezzo_carburante_tradizionale_EUR"] = price_Benzina_EUR
        elif FUEL_TYPE_tradizionale == 'Diesel':
            prezzo_carburante = price_Diesel  #1.73
            session["prezzo_carburante_tradizionale_EUR"] = price_Diesel_EUR
        elif FUEL_TYPE_tradizionale == 'GPL':
            prezzo_carburante = price_GPL  #1.2
            session["prezzo_carburante_tradizionale_EUR"] = price_GPL_EUR
        elif FUEL_TYPE_tradizionale == 'Metano':
            prezzo_carburante = price_Metano  #1.0
            session["prezzo_carburante_tradizionale_EUR"] = price_Metano_EUR


        if (FUEL_TYPE_tradizionale == 'Benzina') | (FUEL_TYPE_tradizionale == 'Diesel') | (FUEL_TYPE_tradizionale == 'GPL'):
            session["prezzo_carburante"] = prezzo_carburante
            print("prezzo_carburante:", prezzo_carburante)
            # session["footnote_prezzo_carburante_tradizionale"] = "Prezzo medio per litro di " + FUEL_TYPE_tradizionale + ": " + str(prezzo_carburante) + " (EUR/1.000 litri) (fonte MASE, valore aggiornato ogni due giorni)"
            # print("footnote_prezzo_carburante_tradizionale----:", session["footnote_prezzo_carburante_tradizionale"])
            session["footnote_prezzo_carburante_tradizionale"] = "litro di " + FUEL_TYPE_tradizionale + ": " + str(prezzo_carburante) + " (EUR/1.000 litri)"

        elif (FUEL_TYPE_tradizionale == 'Metano'):
            session["prezzo_carburante"] = prezzo_carburante
            print("prezzo_carburante:", prezzo_carburante)
            # session["footnote_prezzo_carburante_tradizionale"] = "Prezzo medio per chilogrammo di " + FUEL_TYPE_tradizionale + ": " + str(prezzo_carburante) + " (EUR/1.000 kg) (fonte MASE, valore aggiornato ogni due giorni)"
            # print("footnote_prezzo_carburante_tradizionale----:", session["footnote_prezzo_carburante_tradizionale"])
            session["footnote_prezzo_carburante_tradizionale"] =  "chilogrammo di " + FUEL_TYPE_tradizionale + ": " + str(prezzo_carburante) + " (EUR/1.000 kg)"


        try:
            if session["AVERAGE_CONSUMPTION_TRADIZIONALE"]:
                print("gotta!!")
        except:
            session["AVERAGE_CONSUMPTION_TRADIZIONALE"]= ''

        try:
            if session["AVERAGE_CONSUMPTION_ELETTRICO"]:
                print("gotta!!")
        except:
            session["AVERAGE_CONSUMPTION_ELETTRICO"]= ''

        try:
            if session["AVERAGE_CONSUMPTION_IDROGENO"]:
                print("gotta!!")
        except:
            session["AVERAGE_CONSUMPTION_IDROGENO"] = ''



        data_COSTI = [{
            'consumo_tradizionale': session["AVERAGE_CONSUMPTION_TRADIZIONALE"],
            'COSTO_CHILOMETRICO_TRADIZIONALE': session['costo_finale_tradizionale_EUR'],
            'consumo_elettrico': session["AVERAGE_CONSUMPTION_ELETTRICO"],
            'COSTO_CHILOMETRICO_ELETTRICO': session['costo_finale_elettrico_EUR'],
            'consumo_idrogeno': session["AVERAGE_CONSUMPTION_IDROGENO"],
            'COSTO_CHILOMETRICO_IDROGENO': session['costo_finale_idrogeno_EUR']
        }]


        return render_template("index_costi_chilometrici.html", data_COSTI=data_COSTI,
                               var_COSTI_day=selected_COSTI_day)






@app.route('/tipo_alimentazione_elettrica/', methods=['GET', 'POST'])
def tipo_alimentazione_elettrica():

    session["AVERAGE_CONSUMPTION_TRADIZIONALE"] = ''
    session["AVERAGE_CONSUMPTION_ELETTRICO"] = ''
    session["AVERAGE_CONSUMPTION_IDROGENO"] = ''
    session['costo_finale_tradizionale_EUR'] = 0
    session['costo_finale_elettrico_EUR'] = 0
    session['costo_finale_idrogeno_EUR'] = 0

    if request.method == "POST":
        try:
            selected_COSTI_day = session["COSTI_day"].strftime('%Y-%m-%d')
            print("day:", selected_COSTI_day)
        except AttributeError:
            selected_COSTI_day = '2024-02-08'
            selected_COSTI_day = session["COSTI_day"]
            print("using stored variable: ", session["COSTI_day"])


        ## TRY if session exists
        try:
            selected_FUEL_type_tradizionale = session["FUEL_type_tradizionale"]
            print("-------------------selected_FUEL_type tradizionale:----------------------------------*********", session["FUEL_type_tradizionale"])
        except:
            session["FUEL_type_tradizionale"] = 2
            selected_FUEL_type_tradizionale = session["FUEL_type_tradizionale"]

        try:
            session["FUEL_type_elettrico"] = request.form.get("FUEL_type_elettrico")
            selected_FUEL_type_elettrico = session["FUEL_type_elettrico"]
            print("-------------------selected_FUEL_type elettrico:----------------------------------*********", session["FUEL_type_elettrico"])
        except:
            session["FUEL_type_elettrico"] = 5
            selected_FUEL_type_elettrico = session["FUEL_type_elettrico"]

        try:
            selected_FUEL_type_idrogeno = session["FUEL_type_idrogeno"]
            print("-------------------selected_FUEL_type idrogeno:----------------------------------*********",
                  session["FUEL_type_idrogeno"])
        except:
            session["FUEL_type_idrogeno"] = 15
            selected_FUEL_type_idrogeno = session["FUEL_type_idrogeno"]


        if selected_FUEL_type_elettrico == '5':
            FUEL_TYPE_ELETTRICO = "Elettrico Casa (3.3kW)"
        elif selected_FUEL_type_elettrico == '6':
            FUEL_TYPE_ELETTRICO = "Elettrico Casa (4.5kW)"
        elif selected_FUEL_type_elettrico == '7':
            FUEL_TYPE_ELETTRICO = "Elettrico Casa (6kW)"
        elif selected_FUEL_type_elettrico == '8':
            FUEL_TYPE_ELETTRICO = "Elettrico Pubblico PPU (fino a 22 kW)"
        elif selected_FUEL_type_elettrico == '9':
            FUEL_TYPE_ELETTRICO = "Elettrico Pubblico PPU (fino a 99 kW)"
        elif selected_FUEL_type_elettrico == '10':
            FUEL_TYPE_ELETTRICO = "Elettrico Pubblico PPU (fino a 200 kW)"
        elif selected_FUEL_type_elettrico == '11':
            FUEL_TYPE_ELETTRICO = "Elettrico Pubblico PPU (fino a 350 kW)"
        elif selected_FUEL_type_elettrico == '12':
            FUEL_TYPE_ELETTRICO = "Elettrico Pubblico con Abbonam. Medio"
        elif selected_FUEL_type_elettrico == '13':
            FUEL_TYPE_ELETTRICO = "Elettrico Pubblico con Abbonam. Min"
        elif selected_FUEL_type_elettrico == '14':
            FUEL_TYPE_ELETTRICO = "Elettrico Pubblico con Abbonam. Max"

        try:
            session["FUEL_ELETTRICO"] = FUEL_TYPE_ELETTRICO
            print("------------FUEL TYPE ELETTRICO:----------------", FUEL_TYPE_ELETTRICO)
        except:
            FUEL_TYPE_ELETTRICO = "Elettrico Casa (3kW)"


        if FUEL_TYPE_ELETTRICO == 'Elettrico Casa (3kW)':
            session['prezzo_carburante_elettrico_EUR'] = 0.245
        elif FUEL_TYPE_ELETTRICO == 'Elettrico Casa (3.3kW)':
            session['prezzo_carburante_elettrico_EUR'] = 0.254
        elif FUEL_TYPE_ELETTRICO == 'Elettrico Casa (4.5kW)':
            session['prezzo_carburante_elettrico_EUR'] = 0.264
        elif FUEL_TYPE_ELETTRICO == 'Elettrico Casa (6kW)':
            session['prezzo_carburante_elettrico_EUR'] = 0.264
        elif FUEL_TYPE_ELETTRICO == 'Elettrico Pubblico PPU (fino a 22 kW)':
            session['prezzo_carburante_elettrico_EUR']  = 0.549
        elif FUEL_TYPE_ELETTRICO == 'Elettrico Pubblico PPU (fino a 99 kW)':
            session['prezzo_carburante_elettrico_EUR']  = 0.734
        elif FUEL_TYPE_ELETTRICO == 'Elettrico Pubblico PPU (fino a 200 kW)':
            session['prezzo_carburante_elettrico_EUR'] = 0.812
        elif FUEL_TYPE_ELETTRICO == 'Elettrico Pubblico PPU (fino a 350 kW)':
            session['prezzo_carburante_elettrico_EUR'] = 0.845
        elif FUEL_TYPE_ELETTRICO == 'Elettrico Pubblico con Abbonam. Medio':
            session['prezzo_carburante_elettrico_EUR']  = 0.577
        elif FUEL_TYPE_ELETTRICO == 'Elettrico Pubblico con Abbonam. Min':
            session['prezzo_carburante_elettrico_EUR'] = 0.381
        elif FUEL_TYPE_ELETTRICO == 'Elettrico Pubblico con Abbonam. Max':
            session['prezzo_carburante_elettrico_EUR'] = 0.9


        print(FUEL_TYPE_ELETTRICO)
        print("prezzo ele-----:",  session['prezzo_carburante_elettrico_EUR'])
        session["footnote_prezzo_elettrico"] = FUEL_TYPE_ELETTRICO + ": " + str(session["prezzo_carburante_elettrico_EUR"]) + " (EUR/kWh)"

        try:
            if session["AVERAGE_CONSUMPTION_TRADIZIONALE"]:
                print("gotta!!")
        except:
            session["AVERAGE_CONSUMPTION_TRADIZIONALE"]= ''

        try:
            if session["AVERAGE_CONSUMPTION_ELETTRICO"]:
                print("gotta!!")
        except:
            session["AVERAGE_CONSUMPTION_ELETTRICO"]= ''

        try:
            if session["AVERAGE_CONSUMPTION_IDROGENO"]:
                print("gotta!!")
        except:
            session["AVERAGE_CONSUMPTION_IDROGENO"] = ''


        data_COSTI = [{
            'consumo_tradizionale': session["AVERAGE_CONSUMPTION_TRADIZIONALE"],
            'COSTO_CHILOMETRICO_TRADIZIONALE': session['costo_finale_tradizionale_EUR'],
            'consumo_elettrico': session["AVERAGE_CONSUMPTION_ELETTRICO"],
            'COSTO_CHILOMETRICO_ELETTRICO': session['costo_finale_elettrico_EUR'],
            'consumo_idrogeno': session["AVERAGE_CONSUMPTION_IDROGENO"],
            'COSTO_CHILOMETRICO_IDROGENO': session['costo_finale_idrogeno_EUR']
        }]

        return render_template("index_costi_chilometrici.html", data_COSTI=data_COSTI,
                               var_COSTI_day=selected_COSTI_day)






@app.route('/tipo_alimentazione_idrogeno/', methods=['GET', 'POST'])
def tipo_alimentazione_idrogeno():

    session["AVERAGE_CONSUMPTION_TRADIZIONALE"] = ''
    session["AVERAGE_CONSUMPTION_ELETTRICO"] = ''
    session["AVERAGE_CONSUMPTION_IDROGENO"] = ''
    session['costo_finale_tradizionale_EUR'] = 0
    session['costo_finale_elettrico_EUR'] = 0
    session['costo_finale_idrogeno_EUR'] = 0


    if request.method == "POST":
        try:
            selected_COSTI_day = session["COSTI_day"].strftime('%Y-%m-%d')
            print("day:", selected_COSTI_day)
        except AttributeError:
            selected_COSTI_day = '2024-02-08'
            selected_COSTI_day = session["COSTI_day"]
            print("using stored variable: ", session["COSTI_day"])


        ## TRY if session exists
        try:
            selected_FUEL_type_tradizionale = session["FUEL_type_tradizionale"]
            print("-------------------selected_FUEL_type tradizionale:----------------------------------*********", session["FUEL_type_tradizionale"])
        except:
            session["FUEL_type_tradizionale"] = 2
            selected_FUEL_type_tradizionale = session["FUEL_type_tradizionale"]

        try:
            selected_FUEL_type_elettrico = session["FUEL_type_elettrico"]
            print("-------------------selected_FUEL_type elettrico:----------------------------------*********", session["FUEL_type_elettrico"])
        except:
            session["FUEL_type_elettrico"] = 5
            selected_FUEL_type_elettrico = session["FUEL_type_elettrico"]


        try:
            session["FUEL_type_idrogeno"] = request.form.get("FUEL_type_idrogeno")
            selected_FUEL_type_idrogeno = session["FUEL_type_idrogeno"]
            print("-------------------selected_FUEL_type idrogeno:----------------------------------*********",
                  session["FUEL_type_idrogeno"])
        except:
            session["FUEL_type_idrogeno"] = 15
            selected_FUEL_type_idrogeno = session["FUEL_type_idrogeno"]



        if selected_FUEL_type_idrogeno == '15':
            FUEL_TYPE_HYDROGEN = "H2 grigio"
        elif selected_FUEL_type_idrogeno == '16':
            FUEL_TYPE_HYDROGEN = "H2 blu"
        elif selected_FUEL_type_idrogeno == '17':
            FUEL_TYPE_HYDROGEN = "H2 verde"

        try:
            session["FUEL_HYDROGEN"] = FUEL_TYPE_HYDROGEN
            print("------------FUEL TYPE HYDROGEN:----------------", FUEL_TYPE_HYDROGEN)
        except:
            FUEL_TYPE_HYDROGEN = "H2 blu"



        if FUEL_TYPE_HYDROGEN == 'H2 grigio':
            session['prezzo_carburante_idrogeno_EUR'] = 1.5
        elif FUEL_TYPE_HYDROGEN == 'H2 blu':
            session['prezzo_carburante_idrogeno_EUR'] = 2.5
        elif FUEL_TYPE_HYDROGEN == 'H2 verde':
            session['prezzo_carburante_idrogeno_EUR'] = 4.5


        session["footnote_prezzo_idrogeno"] = "Kg di " + FUEL_TYPE_HYDROGEN + ": " + str(
            session["prezzo_carburante_idrogeno_EUR"]) + " (EUR/kg)"

        try:
            if session["AVERAGE_CONSUMPTION_TRADIZIONALE"]:
                print("gotta!!")
        except:
            session["AVERAGE_CONSUMPTION_TRADIZIONALE"]= ''

        try:
            if session["AVERAGE_CONSUMPTION_ELETTRICO"]:
                print("gotta!!")
        except:
            session["AVERAGE_CONSUMPTION_ELETTRICO"]= ''

        try:
            if session["AVERAGE_CONSUMPTION_IDROGENO"]:
                print("gotta!!")
        except:
            session["AVERAGE_CONSUMPTION_IDROGENO"] = ''


        data_COSTI = [{
            'consumo_tradizionale': session["AVERAGE_CONSUMPTION_TRADIZIONALE"],
            'COSTO_CHILOMETRICO_TRADIZIONALE': session['costo_finale_tradizionale_EUR'],
            'consumo_elettrico': session["AVERAGE_CONSUMPTION_ELETTRICO"],
            'COSTO_CHILOMETRICO_ELETTRICO': session['costo_finale_elettrico_EUR'],
            'consumo_idrogeno': session["AVERAGE_CONSUMPTION_IDROGENO"],
            'COSTO_CHILOMETRICO_IDROGENO': session['costo_finale_idrogeno_EUR']
        }]

        return render_template("index_costi_chilometrici.html", data_COSTI=data_COSTI,
                               var_COSTI_day=selected_COSTI_day)


###########################################################
#####-----consumi------------------------------------------

@app.route('/consumo_medio_tradizionale/', methods=['GET', 'POST'])
def consumo_medio_tradizionale():
    lat = request.form['lat']
    lng = request.form['lng']

    session['costo_finale_tradizionale_EUR'] = 0
    session['costo_finale_elettrico_EUR'] = 0
    session['costo_finale_idrogeno_EUR'] = 0

    try:
        selected_COSTI_day = session["COSTI_day"].strftime('%Y-%m-%d')
        print("day:", selected_COSTI_day)
    except AttributeError:
        selected_COSTI_day = '2024-02-08'
        selected_COSTI_day = session["COSTI_day"]
        print("using stored variable: ", session["COSTI_day"])

    try:
        FUEL_TYPE_tradizionale = session["FUEL_TRADIZIONALE"]
        print("FUEL TYPE:", FUEL_TYPE_tradizionale)
    except KeyError:
        session["FUEL_TRADIZIONALE"] = 'Benzina'
        FUEL_TYPE_tradizionale = 'Benzina'


    if (FUEL_TYPE_tradizionale == 'Benzina') | (FUEL_TYPE_tradizionale == 'Diesel') | (FUEL_TYPE_tradizionale == 'GPL'):
        print("--------------------------OK----------------------------")
        session["CONSUMPTION_TRADIZIONALE"] = request.form.get("consumo_tradizionale")
        consumo_medio_tradizionale = str(session["CONSUMPTION_TRADIZIONALE"] + ' (litri/100km)')   ### this is the value to show in the table
        session["AVERAGE_CONSUMPTION_TRADIZIONALE"] = consumo_medio_tradizionale
        print("consumo (l/100km) -----> ", consumo_medio_tradizionale)
    elif (FUEL_TYPE_tradizionale == 'Metano'):
        print("--------------------------OK----------------------------")
        session["CONSUMPTION_TRADIZIONALE"] = request.form.get("consumo_tradizionale")
        consumo_medio_tradizionale = str(session["CONSUMPTION_TRADIZIONALE"] + ' (kg/100km)')   ### this is the value to show in the table
        session["AVERAGE_CONSUMPTION_TRADIZIONALE"] = consumo_medio_tradizionale
        print("consumo (kg/100km) -----> ", consumo_medio_tradizionale)

    ## if the session already exists.....
    if session["AVERAGE_CONSUMPTION_TRADIZIONALE"]:
        if (session["FUEL_TRADIZIONALE"] == 'Benzina') | (session["FUEL_TRADIZIONALE"] == 'Diesel') | (session["FUEL_TRADIZIONALE"] == 'GPL'):
            session["CONSUMPTION_TRADIZIONALE"] = request.form.get("consumo_tradizionale")
            consumo_medio_tradizionale = str(
                session["CONSUMPTION_TRADIZIONALE"] + ' (litri/100km)')  ### this is the value to show in the table
            session["AVERAGE_CONSUMPTION_TRADIZIONALE"] = consumo_medio_tradizionale
            print("consumo (l/100km) -----> ", consumo_medio_tradizionale)
        elif (session["FUEL_TRADIZIONALE"] == 'Metano'):
            session["CONSUMPTION_TRADIZIONALE"] = request.form.get("consumo_tradizionale")
            consumo_medio_tradizionale = str(session["CONSUMPTION_TRADIZIONALE"] + ' (kg/100km)')   ### this is the value to show in the table
            session["AVERAGE_CONSUMPTION_TRADIZIONALE"] = consumo_medio_tradizionale
            print("consumo (kg/100km) -----> ", consumo_medio_tradizionale)


    try:
        if session["AVERAGE_CONSUMPTION_TRADIZIONALE"]:
            print("gotta!")
    except:
        session["AVERAGE_CONSUMPTION_TRADIZIONALE"] = ''

    try:
        if session["AVERAGE_CONSUMPTION_ELETTRICO"]:
            print("gotta!")
    except:
        session["AVERAGE_CONSUMPTION_ELETTRICO"] = ''

    try:
        if session["AVERAGE_CONSUMPTION_IDROGENO"]:
            print("gotta!")
    except:
        session["AVERAGE_CONSUMPTION_IDROGENO"] = ''


    data_COSTI = [{
        'consumo_tradizionale': session["AVERAGE_CONSUMPTION_TRADIZIONALE"],
        'COSTO_CHILOMETRICO_TRADIZIONALE': session['costo_finale_tradizionale_EUR'],
        'consumo_elettrico': session["AVERAGE_CONSUMPTION_ELETTRICO"],
        'COSTO_CHILOMETRICO_ELETTRICO': session['costo_finale_elettrico_EUR'],
        'consumo_idrogeno': session["AVERAGE_CONSUMPTION_IDROGENO"],
        'COSTO_CHILOMETRICO_IDROGENO': session['costo_finale_idrogeno_EUR']
    }]

    return render_template("index_costi_chilometrici.html", data_COSTI=data_COSTI)




@app.route('/consumo_medio_elettrico/', methods=['GET', 'POST'])
def consumo_medio_elettrico():
    lat = request.form['lat']
    lng = request.form['lng']

    session['costo_finale_tradizionale_EUR'] = 0
    session['costo_finale_elettrico_EUR'] = 0
    session['costo_finale_idrogeno_EUR'] = 0

    try:
        selected_COSTI_day = session["COSTI_day"].strftime('%Y-%m-%d')
        print("day:", selected_COSTI_day)
    except AttributeError:
        selected_COSTI_day = '2024-02-08'
        selected_COSTI_day = session["COSTI_day"]
        print("using stored variable: ", session["COSTI_day"])

    try:
        FUEL_TYPE_ELETTRICO = session["FUEL_ELETTRICO"]
        print("FUEL TYPE ELETTRICO:", FUEL_TYPE_ELETTRICO)
    except KeyError:
        session["FUEL_ELETTRICO"] = 'Elettrico Casa (3kW)'
        FUEL_TYPE_ELETTRICO = 'Elettrico Casa (3kW)'

    session["CONSUMPTION_ELETTRICO"] = request.form.get("consumo_elettrico")
    consumo_medio_elettrico = str(
        session[
            "CONSUMPTION_ELETTRICO"] + ' (kWh/100km)')  ### this is the value that the user must insert in the white box
    session["AVERAGE_CONSUMPTION_ELETTRICO"] = consumo_medio_elettrico
    print("consumo (kWh/100km) -----> ", consumo_medio_elettrico)


    """
    if (FUEL_TYPE_ELETTRICO == 'Elettrico Casa (3kW)') | (FUEL_TYPE_ELETTRICO == 'Elettrico Casa (4.5kW)') | (FUEL_TYPE_ELETTRICO == 'Elettrico Pubblico PPU (fino a 22 kW)') | (
                FUEL_TYPE_ELETTRICO == 'Elettrico Pubblico PPU (fino a 22 kW)') | (
                FUEL_TYPE_ELETTRICO == 'Elettrico Pubblico PPU (fino a 200 kW)') | (
                FUEL_TYPE_ELETTRICO == 'Elettrico Pubblico con Abbonamento'):
        session["CONSUMPTION_ELETTRICO"] = request.form.get("consumo_elettrico")
        consumo_medio_elettrico = str(
            session["CONSUMPTION_ELETTRICO"] + ' (kWh/100km)')  ### this is the value that the user must insert in the white box
        session["AVERAGE_CONSUMPTION_ELETTRICO"] = consumo_medio_elettrico
        print("consumo (kWh/100km) -----> ", consumo_medio_elettrico)
    """

    ## if the session already exists.....
    if session["AVERAGE_CONSUMPTION_ELETTRICO"]:
        session["CONSUMPTION_ELETTRICO"] = request.form.get("consumo_elettrico")
        consumo_medio_elettrico = str(
            session[
                "CONSUMPTION_ELETTRICO"] + ' (kWh/100km)')  ### this is the value that the user must insert in the white box
        session["AVERAGE_CONSUMPTION_ELETTRICO"] = consumo_medio_elettrico


    try:
        if session["AVERAGE_CONSUMPTION_TRADIZIONALE"]:
            print("gotta!")
    except:
        session["AVERAGE_CONSUMPTION_TRADIZIONALE"] = ''

    try:
        if session["AVERAGE_CONSUMPTION_ELETTRICO"]:
            print("gotta!")
    except:
        session["AVERAGE_CONSUMPTION_ELETTRICO"] = ''

    try:
        if session["AVERAGE_CONSUMPTION_IDROGENO"]:
            print("gotta!")
    except:
        session["AVERAGE_CONSUMPTION_IDROGENO"] = ''


    data_COSTI = [{
        'consumo_tradizionale': session["AVERAGE_CONSUMPTION_TRADIZIONALE"],
        'COSTO_CHILOMETRICO_TRADIZIONALE': session['costo_finale_tradizionale_EUR'],
        'consumo_elettrico': session["AVERAGE_CONSUMPTION_ELETTRICO"],
        'COSTO_CHILOMETRICO_ELETTRICO': session['costo_finale_elettrico_EUR'],
        'consumo_idrogeno': session["AVERAGE_CONSUMPTION_IDROGENO"],
        'COSTO_CHILOMETRICO_IDROGENO': session['costo_finale_idrogeno_EUR']
    }]

    return render_template("index_costi_chilometrici.html", data_COSTI=data_COSTI)




@app.route('/consumo_medio_idrogeno/', methods=['GET', 'POST'])
def consumo_medio_idrogeno():
    lat = request.form['lat']
    lng = request.form['lng']

    session['costo_finale_tradizionale_EUR'] = 0
    session['costo_finale_elettrico_EUR'] = 0
    session['costo_finale_idrogeno_EUR'] = 0

    try:
        selected_COSTI_day = session["COSTI_day"].strftime('%Y-%m-%d')
        print("day:", selected_COSTI_day)
    except AttributeError:
        selected_COSTI_day = '2024-02-08'
        selected_COSTI_day = session["COSTI_day"]
        print("using stored variable: ", session["COSTI_day"])

    try:
        FUEL_TYPE_HYDROGEN = session["FUEL_HYDROGEN"]
        print("FUEL TYPE:", FUEL_TYPE_HYDROGEN)
    except KeyError:
        session["FUEL_HYDROGEN"] = 'H2 blu'
        FUEL_TYPE_HYDROGEN = 'H2 blu'


    session["CONSUMPTION_IDROGENO"] = request.form.get("consumo_idrogeno")
    consumo_medio_idrogeno = str(
        session[
            "CONSUMPTION_IDROGENO"] + ' (kg/100km)')  ### this is the value that the user must insert in the white box
    session["AVERAGE_CONSUMPTION_IDROGENO"] = consumo_medio_idrogeno
    print("consumo (kWh/100km) -----> ", consumo_medio_idrogeno)


    """
    if (FUEL_TYPE_HYDROGEN == 'H2 blu') | (FUEL_TYPE_HYDROGEN == 'H2 verde'):
        session["CONSUMPTION_IDROGENO"] = request.form.get("consumo_idrogeno")
        consumo_medio_idrogeno = str(
            session["CONSUMPTION_IDROGENO"] + ' (kg/100km)')  ### this is the value that the user must insert in the white box
        session["AVERAGE_CONSUMPTION_IDROGENO"] = consumo_medio_idrogeno
        print("consumo (kWh/100km) -----> ", consumo_medio_idrogeno)
    """

    ## if the sessio already exists.....
    if session["AVERAGE_CONSUMPTION_IDROGENO"]:
        consumo_medio_idrogeno = str(
            session[
                "CONSUMPTION_IDROGENO"] + ' (kg/100km)')  ### this is the value that the user must insert in the white box
        session["AVERAGE_CONSUMPTION_IDROGENO"] = consumo_medio_idrogeno
        print("consumo (kWh/100km) -----> ", consumo_medio_idrogeno)


    try:
        if session["AVERAGE_CONSUMPTION_TRADIZIONALE"]:
            print("gotta!")
    except:
        session["AVERAGE_CONSUMPTION_TRADIZIONALE"] = ''

    try:
        if session["AVERAGE_CONSUMPTION_ELETTRICO"]:
            print("gotta!")
    except:
        session["AVERAGE_CONSUMPTION_ELETTRICO"] = ''

    try:
        if session["AVERAGE_CONSUMPTION_IDROGENO"]:
            print("gotta!")
    except:
        session["AVERAGE_CONSUMPTION_IDROGENO"] = ''


    data_COSTI = [{
        'consumo_tradizionale': session["AVERAGE_CONSUMPTION_TRADIZIONALE"],
        'COSTO_CHILOMETRICO_TRADIZIONALE': session['costo_finale_tradizionale_EUR'],
        'consumo_elettrico': session["AVERAGE_CONSUMPTION_ELETTRICO"],
        'COSTO_CHILOMETRICO_ELETTRICO': session['costo_finale_elettrico_EUR'],
        'consumo_idrogeno': session["AVERAGE_CONSUMPTION_IDROGENO"],
        'COSTO_CHILOMETRICO_IDROGENO': session['costo_finale_idrogeno_EUR']
    }]

    return render_template("index_costi_chilometrici.html", data_COSTI=data_COSTI)



#########--------##############################
######## COSTI -------#########################


@app.route('/costo_chilometrico_finale/', methods=['GET', 'POST'])
def costo_chilometrico_finale():


    try:
        selected_COSTI_day = session["COSTI_day"].strftime('%Y-%m-%d')
        print("day:", selected_COSTI_day)
    except AttributeError:
        selected_COSTI_day = '2024-02-08'
        selected_COSTI_day = session["COSTI_day"]
        print("using stored variable: ", session["COSTI_day"])


    #### ---- tradizionale ------- ##############################
    try:
        session["costo_chilometrico_tradizionale"] = round( (float(session["CONSUMPTION_TRADIZIONALE"]) * session["prezzo_carburante_tradizionale_EUR"]), 2) ## average gasoline price
        costo_finale_tradizionale = str(session["costo_chilometrico_tradizionale"])
        if session["AVERAGE_CONSUMPTION_TRADIZIONALE"] == '':
            session['costo_finale_tradizionale_EUR'] = 0
            print("----nothing------")
        else:
            # session['costo_finale_tradizionale_EUR'] = costo_finale_tradizionale + " (EUR/100 km)"
            session['costo_finale_tradizionale_EUR'] = costo_finale_tradizionale
    except KeyError:
        session["prezzo_carburante_tradizionale_EUR"] = 0
        session['costo_finale_tradizionale_EUR'] = 0
        session["AVERAGE_CONSUMPTION_TRADIZIONALE"] = ''

    #### ---- elettrico ------- ##############################
    try:
        session["costo_chilometrico_elettrico"] = round(
            (float(session["CONSUMPTION_ELETTRICO"]) * session["prezzo_carburante_elettrico_EUR"]),2)
        costo_finale_elettrico = str(session["costo_chilometrico_elettrico"])
        if session["AVERAGE_CONSUMPTION_ELETTRICO"] == '':
            session['costo_finale_elettrico_EUR'] = 0
        else:
            session['costo_finale_elettrico_EUR'] = costo_finale_elettrico
    except KeyError:
        session["prezzo_carburante_elettrico_EUR"] = 0
        session['costo_finale_elettrico_EUR'] = 0
        session["AVERAGE_CONSUMPTION_ELETTRICO"] = ''

    print(float(session["CONSUMPTION_ELETTRICO"]))
    print(session["prezzo_carburante_elettrico_EUR"])
    print(session['costo_finale_elettrico_EUR'])

        #### ---- idrogeno ------- ##############################
    try:
        session["costo_chilometrico_idrogeno"] = round(
            (float(session["CONSUMPTION_IDROGENO"]) * session["prezzo_carburante_idrogeno_EUR"]), 2)
        costo_finale_idrogeno = str(session["costo_chilometrico_idrogeno"])
        if session["AVERAGE_CONSUMPTION_IDROGENO"] == '':
            session['costo_finale_idrogeno_EUR'] = 0
        else:
            session['costo_finale_idrogeno_EUR'] = costo_finale_idrogeno
    except KeyError:
        session["prezzo_carburante_idrogeno_EUR"] = 0
        session['costo_finale_idrogeno_EUR'] = 0
        session["AVERAGE_CONSUMPTION_IDROGENO"] = ''


    print( "-----------session[costo_finale_tradizionale_EUR]-----:", session["costo_finale_tradizionale_EUR"])
    print("-----------session[costo_finale_elettrico_EUR]-----:", session["costo_finale_elettrico_EUR"])
    print("-----------session[costo_finale_idrogeno_EUR]-----:", session["costo_finale_idrogeno_EUR"])

    data_COSTI_bis = [{
        'consumo_tradizionale': session["AVERAGE_CONSUMPTION_TRADIZIONALE"],
        'COSTO_CHILOMETRICO_TRADIZIONALE': session['costo_finale_tradizionale_EUR'],
        'consumo_elettrico': session["AVERAGE_CONSUMPTION_ELETTRICO"],
        'COSTO_CHILOMETRICO_ELETTRICO': session['costo_finale_elettrico_EUR'],
        'consumo_idrogeno': session["AVERAGE_CONSUMPTION_IDROGENO"],
        'COSTO_CHILOMETRICO_IDROGENO': session['costo_finale_idrogeno_EUR']
    }]

    # print(data_COSTO_CHILOMETRICO)

    # print("-----data_COSTO_CHILOMETRICO----------------:",  costo_finale_EUR)

    return render_template("index_costi_chilometrici.html",
                           data_COSTI_bis=data_COSTI_bis)





############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################
############################################################################################################

'''
@app.route('/alimentazione_elettrica/', methods=['GET', 'POST'])
def alimentazione_elettrica():
    if request.method == "POST":
        try:
            selected_COSTI_day = session["COSTI_day"].strftime('%Y-%m-%d')
            print("day:", selected_COSTI_day)
        except AttributeError:
            selected_COSTI_day = '2024-02-08'
            selected_COSTI_day = session["COSTI_day"]
            print("using stored variable: ", session["COSTI_day"])

        ## TRY if session exists
        try:
            session["ELECTRIC_type"] = request.form.get("ELECTRIC_type")
            selected_ELECTRIC_type = session["ELECTRIC_type"]
            print("selected_ELECTRIC_type:", selected_ELECTRIC_type)
            # selected_ELECTRIC_type = str(selected_ELECTRIC_type)
        except:
            session["ELECTRIC_type"] = 2
            selected_ELECTRIC_type = session["ELECTRIC_type"]
            print("using stored variable: ", session["ELECTRIC_type"])

        CHARGING_POINT = "Elettrico Casa (3kW)"
        if selected_ELECTRIC_type == '0':
            CHARGING_POINT = "Elettrico Casa (3kW)"
        elif selected_ELECTRIC_type == '1':
            CHARGING_POINT = "Elettrico Casa (4.5kW)"
        elif selected_ELECTRIC_type == '2':
            CHARGING_POINT = "Elettrico Pubblico PPU (fino a 22 kW)"
        elif selected_ELECTRIC_type == '3':
            CHARGING_POINT = "Elettrico Pubblico PPU (fino a 200 kW)"
        elif selected_ELECTRIC_type == '4':
            CHARGING_POINT = "Elettrico Pubblico con Abbonamento"

        session["CHARGING_POINT"] = CHARGING_POINT
        print("CHARGING_POINT:", CHARGING_POINT)

        with open(path_app + "static/params/selected_ELECTRIC_type.txt", "w") as file:
            file.write(selected_ELECTRIC_type)
            # print(session['id'])



        """
        ##############################################################################################
        ###------- Ricava Prezzo Energia Elettrica Domestica per consumo annuo di circa 5500 kWh -----

        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.support.ui import Select
        from selenium.webdriver.common.by import By
        from selenium import webdriver
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import Select
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import time

        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1224, 1268)
        driver.get("https://www.ilportaleofferte.it/portaleOfferte/")
        # driver.get_screenshot_as_file("capture.png")

        dropdown_offerta = driver.find_element(By.XPATH, "//*[@name='tipoOfferta']")
        # Take a screenshot before entering a value
        # driver.save_screenshot("screenshot-dropdown_offerta.png")
        ## choose "energiaElettrica"
        dropdown_offerta.send_keys("energiaElettrica")
        dropdown_offerta = Select(driver.find_element(By.ID, "tipoOfferta"))
        driver.save_screenshot("screenshot-dropdown_offerta_selected.png")

        input_comune = driver.find_element(By.NAME, 'cap-comune')
        # Take a screenshot before entering a value
        # driver.save_screenshot("screenshot_insert_comune.png")
        ## choose "058091"   ### this is the ISTAT code of Comune di ROMA
        input_comune.send_keys("Roma")
        # dropdown_comune = Select(driver.find_element(By.NAME, "cap-comune"))
        driver.save_screenshot("screenshot_insert_selected_comune.png")

        # submit contents
        driver.find_element(By.XPATH, '//input[@value="INIZIA ORA"]').click()
        driver.save_screenshot("screenshot_submit_inizia_ora.png")
        # time.sleep(5)

        ##### ---->>> NEXT page ------->>>>>>>
        offerta_energia = driver.find_element(By.XPATH, '//input[@id="gas"]')
        ## choose "energiaElettrica"
        driver.save_screenshot("screenshot_offerta_energia_radio.png")

        comune = driver.find_element(By.NAME, 'capComuneDescr')
        driver.save_screenshot("screenshot_input_comune_again.png")

        offerta_casa = driver.find_element(By.XPATH, '//label[@for="casa"]')
        offerta_casa = driver.find_element(By.NAME, 'dove')
        offerta_casa.send_keys("casa")
        offerta_casa.click()
        driver.save_screenshot("screenshot_input_casa.png")

        prezzo_fisso_variabile = driver.find_element(By.XPATH, '//label[@for="prezzoFisso"]')
        prezzo_fisso_variabile = driver.find_element(By.NAME, 'tipoOfferta')
        prezzo_fisso_variabile.send_keys("prezzoFisso")
        prezzo_fisso_variabile.click()
        driver.save_screenshot("screenshot_prezzo_fisso.png")

        residenza = driver.find_element(By.XPATH, '//label[@for="residenteSI"]')
        residenza = driver.find_element(By.NAME, 'residente')
        residenza.send_keys("residenteSI")
        residenza.click()
        driver.save_screenshot("screenshot_residenza.png")

        # ----->>>> submit contents
        driver.find_element(By.XPATH, "//a[@class='btn btn-default btn-medium gray link_btn']").click()
        driver.save_screenshot("screenshot_AVANTI.png")

        #### ----->>> next page....POTENZA
        dropdown_potenza = driver.find_element(By.XPATH, "//*[@name='potenza']")


        if selected_ELECTRIC_type == '0':
            CHARGING_POINT = "Elettrico Casa (3kW)"
            ## choose "3 kW"
            # dropdown_potenza = Select(driver.find_element(By.ID, "scegliPotenza"))
            dropdown_potenza = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.ID, "scegliPotenza"))
            )
            dropdown_potenza.send_keys("3")
            driver.save_screenshot("screenshot_dropdown_potenza.png")
        if selected_ELECTRIC_type == '1':
            CHARGING_POINT = "Elettrico Casa (4.5kW)"
            ## choose "4.5 kW"
            # dropdown_potenza = Select(driver.find_element(By.ID, "scegliPotenza"))
            dropdown_potenza = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.ID, "scegliPotenza"))
            )
            dropdown_potenza.send_keys("4.5")
            driver.save_screenshot("screenshot_dropdown_potenza.png")

        dropdown_fascia = driver.find_element(By.XPATH, "//*[@name='tipoTariffa']")
        ## choose "Fasce"
        dropdown_fascia.send_keys("Fasce")
        dropdown_fascia = Select(driver.find_element(By.ID, "tipoTariffa"))
        driver.save_screenshot("screenshot_dropdown_fascia.png")

        energia_rinnovabile = driver.find_element(By.XPATH, '//label[@for="ferNO"]')
        energia_rinnovabile = driver.find_element(By.NAME, 'fer')
        energia_rinnovabile.send_keys("ferNO")
        energia_rinnovabile.click()
        driver.save_screenshot("screenshot_energia_rinnovabile.png")

        consumo = driver.find_element(By.XPATH, '//label[@for="consumoSI"]')
        consumo = driver.find_element(By.NAME, 'conosci')
        consumo.send_keys("consumoSI")
        consumo.click()
        driver.save_screenshot("screenshot_consumo.png")

        ### --- inserisci valore consumo annuo......(kWh)
        input_valore_consumo_annuo = driver.find_element(By.NAME, 'consumoAnnuoSomma')
        input_valore_consumo_annuo.send_keys("5500")
        driver.save_screenshot("screenshot_consumo_annuo.png")

        #### submito form and "confronta"
        driver.find_element(By.XPATH, "//input[@class='btn btn-default btn-medium']").click()
        driver.save_screenshot("screenshot_CONFRONTA_PREZZI.png")
        # time.sleep(3)

        #################################################
        ##### ----exctract values and make averages --###

        import httplib2
        from bs4 import BeautifulSoup, SoupStrainer
        from urllib.request import Request, urlopen

        http = httplib2.Http()
        import requests
        import pandas as pd
        import json
        import re

        # https://medium.com/analytics-vidhya/web-scraping-google-search-results-with-selenium-and-beautifulsoup-4c534817ad88
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        search = soup.find_all('div',
                               class_="boxElement prezzoOfferta padding-bottom-10 col-lg-4 col-md-4 col-sm-12 col-xs-12")

        list_offerte_annuali = []
        for tag in soup.findAll(True, {
            "class": ["boxElement prezzoOfferta padding-bottom-10 col-lg-4 col-md-4 col-sm-12 col-xs-12"]}):
            # print(tag)
            # print(tag.text.strip())
            offer = tag.text.strip()
            offer = offer.split(" ")[0]
            offer = offer.split(",")[0]
            offer = float(offer.replace('.', ''))
            list_offerte_annuali.append(offer)

        ### make an average of all the prices into the list
        def Average(lst):
            return sum(lst) / len(lst)

        try:
            average_prezzo_casa_3kW = round(Average(list_offerte_annuali), 2)   ### prezzo in kWh per anno
            print("-----average_prezzo_casa_3kW----:", average_prezzo_casa_3kW)
            prezzo_carburante_ele = round(average_prezzo_casa_3kW / 5500 , 2)   ## prezzo (EUR/kWh)
        except ZeroDivisionError:
            prezzo_carburante_ele = 0.6

        driver.close()


        #####################################################################################
        """

        if CHARGING_POINT == 'Elettrico Casa (3kW)':
            # session['prezzo_carburante_ele'] = prezzo_carburante_ele
            session['prezzo_carburante_ele'] = 0.31
            print("prezzo_carburante_ele:", session["prezzo_carburante_ele"])
            session["footnote_prezzo_carburante_ele"] = CHARGING_POINT + ": " + str(
                session["prezzo_carburante_ele"]) + " (EUR/kWh) (fonte ARERA per consumo medio annuo di 5500 kWh) "
        elif CHARGING_POINT == 'Elettrico Casa (4.5kW)':
            # session['prezzo_carburante_ele'] = prezzo_carburante_ele
            session['prezzo_carburante_ele'] = 0.34
            print("prezzo_carburante_ele:", session["prezzo_carburante_ele"])
            session["footnote_prezzo_carburante_ele"] = CHARGING_POINT + ": " + str(
                session["prezzo_carburante_ele"]) + " (EUR/kWh) (fonte ARERA per consumo medio annuo di 5500 kWh) "
        elif CHARGING_POINT == 'Elettrico Pubblico PPU (fino a 22 kW)':
            session['prezzo_carburante_ele'] = 0.69
            print("prezzo_carburante_ele:", session["prezzo_carburante_ele"])
            session["footnote_prezzo_carburante_ele"] = CHARGING_POINT + ": " + str(
                session["prezzo_carburante_ele"]) + " (EUR/kWh) (fonte **** per consumo medio annuo di 5500 kWh) "
        elif CHARGING_POINT == 'Elettrico Pubblico PPU (fino a 200 kW)':
            session['prezzo_carburante_ele'] = 0.8
            print("prezzo_carburante_ele:", session["prezzo_carburante_ele"])
            session["footnote_prezzo_carburante_ele"] = CHARGING_POINT + ": " + str(
                session["prezzo_carburante_ele"]) + " (EUR/kWh) (fonte **** per consumo medio annuo di 5500 kWh) "
        elif CHARGING_POINT == 'Elettrico Pubblico con Abbonamento':
            session['prezzo_carburante_ele'] = 0.99
            print("prezzo_carburante_ele:", session["prezzo_carburante_ele"])
            session["footnote_prezzo_carburante_ele"] = CHARGING_POINT + ": " + str(
                session["prezzo_carburante_ele"]) + " (EUR/kWh) (fonte **** per consumo medio annuo di 5500 kWh) "


        data_COSTI_ELETTRICO = [{
            'COSTI_day': selected_COSTI_day,
            'tipo_ricarica': CHARGING_POINT,
            'consumption': 'seleziona consumo medio'
        }]

        return render_template("index_costi_chilometrici_elettrico.html", data_COSTI_ELETTRICO=data_COSTI_ELETTRICO,
                               var_COSTI_day=selected_COSTI_day, var_FUEL_type=selected_ELECTRIC_type)



@app.route('/consumo_medio_elettrico_old/', methods=['GET', 'POST'])
def consumo_medio_elettrico_old():
    lat = request.form['lat']
    lng = request.form['lng']

    try:
        selected_COSTI_day = session["COSTI_day"].strftime('%Y-%m-%d')
        print("day:", selected_COSTI_day)
    except AttributeError:
        selected_COSTI_day = '2024-02-08'
        selected_COSTI_day = session["COSTI_day"]
        print("using stored variable: ", session["COSTI_day"])

    try:
        CHARGING_POINT = session["CHARGING_POINT"]
        print("CHARGING_POINT:", CHARGING_POINT)
    except KeyError:
        CHARGING_POINT = "Elettrico Casa (3kW)"

    # if (CHARGING_POINT == 'Benzina') | (CHARGING_POINT == 'Diesel') | (CHARGING_POINT == 'GPL') | (FUEL_TYPE == 'Elettrica') | (FUEL_TYPE == 'H2'):
    #    print("--------------------------OK----------------------------")
    session["CONSUMPTION"] = request.form.get("consumo")
    consumo_medio = str(session["CONSUMPTION"] + ' (kWh/100km)')   ### this is the value that the user must insert in the white box
    print("consumo (kWh/100km) -----> ", consumo_medio)
    # elif (FUEL_TYPE == 'Metano'):
    #    print("--------------------------OK----------------------------")
    #    session["CONSUMPTION"] = request.form.get("consumo")
    #    consumo_medio = str(session["CONSUMPTION"] + ' (kg/100km)')   ### this is the value to show in the table
    #    print("consumo (kg/100km) -----> ", consumo_medio)
    session["AVERAGE_CONSUMPTION_TRADIZIONALE"] = consumo_medio



    try:
        prezzo_carburante_ele = session['prezzo_carburante_ele']
        print("footnote_prezzo_carburante----:", session["footnote_prezzo_carburante_ele"])
    except KeyError:
        abort(404)


    data_COSTI_ELETTRICO = [{
        'COSTI_day': selected_COSTI_day,
        'tipo_ricarica': CHARGING_POINT,
        'consumption': consumo_medio
    }]

    print("-----data_COSTI_ELETTRICO----------------:",  data_COSTI_ELETTRICO)

    return render_template("index_costi_chilometrici_elettrico.html", data_COSTI_ELETTRICO=data_COSTI_ELETTRICO)




@app.route('/costo_chilometrico_elettrico/', methods=['GET', 'POST'])
def costo_chilometrico_elettrico():
    try:
        selected_COSTI_day = session["COSTI_day"].strftime('%Y-%m-%d')
        print("day:", selected_COSTI_day)
    except AttributeError:
        selected_COSTI_day = '2024-02-08'
        selected_COSTI_day = session["COSTI_day"]
        print("using stored variable: ", session["COSTI_day"])

    try:
        selected_consumption_value = session["CONSUMPTION"]
        print("selected_consumption_value:------->", selected_consumption_value)
    except AttributeError:
        abort(404)


    try:
        consumo_medio = session["AVERAGE_CONSUMPTION_TRADIZIONALE"]
        print("consumo_medio:------------------------------------------->", consumo_medio)
    except AttributeError:
        abort(404)

    try:
        CHARGING_POINT = session["CHARGING_POINT"]
        print("CHARGING_POINT:", CHARGING_POINT)
    except AttributeError:
        abort(404)

    try:
        prezzo_carburante_ele = session["prezzo_carburante_ele"]
        print("prezzo_carburante_ele:", prezzo_carburante_ele)
    except AttributeError:
        abort(404)


    try:
        footnote_prezzo_carburante_ele = session["footnote_prezzo_carburante_ele"]
        print("footnote_prezzo_carburante---->:", footnote_prezzo_carburante_ele)
    except AttributeError:
        abort(404)


    session["costo_chilometrico"] = round((float(selected_consumption_value) * prezzo_carburante_ele),2)  ## average electricity price
    print("-------prezzo_carburante_ele:-----------------", prezzo_carburante_ele)
    print("costo chilometrico -----> ", str(session["costo_chilometrico"]))
    costo_finale = str(session["costo_chilometrico"])
    # print(costo_finale + " (EUR)")
    costo_finale_EUR = costo_finale + " (EUR/100 km)"

    data_COSTI_ELETTRICO = [{
        'COSTI_day': selected_COSTI_day,
        'tipo_ricarica': CHARGING_POINT,
        'consumption': consumo_medio # selected_consumption_value
    }]


    data_COSTO_CHILOMETRICO_ELETTRICO = [{
        'COSTO_CHILOMETRICO': costo_finale_EUR
    }]

    print("-----data_COSTO_CHILOMETRICO----------------:",  costo_finale_EUR)

    return render_template("index_costi_chilometrici_elettrico.html",
                           data_COSTI_ELETTRICO=data_COSTI_ELETTRICO,
                           data_COSTO_CHILOMETRICO_ELETTRICO=data_COSTO_CHILOMETRICO_ELETTRICO)






@app.route('/costo_chilometrico/', methods=['GET', 'POST'])
def costo_chilometrico():
    try:
        selected_COSTI_day = session["COSTI_day"].strftime('%Y-%m-%d')
        print("day:", selected_COSTI_day)
    except AttributeError:
        selected_COSTI_day = '2024-02-08'
        selected_COSTI_day = session["COSTI_day"]
        print("using stored variable: ", session["COSTI_day"])

    try:
        selected_FUEL_type = session["FUEL_type"]
        print("selected_FUEL_type:", selected_FUEL_type)
        selected_FUEL_type = str(selected_FUEL_type)
    except AttributeError:
        abort(404)


    try:
        selected_consumption_value = session["CONSUMPTION"]
        print("selected_consumption_value:------->", selected_consumption_value)
    except AttributeError:
        abort(404)


    try:
        consumo_medio = session["AVERAGE_CONSUMPTION_TRADIZIONALE"]
        print("consumo_medio:------------------------------------------->", consumo_medio)
    except AttributeError:
        abort(404)

    try:
        FUEL_TYPE = session["FUEL"]
        print("FUEL TYPE:", FUEL_TYPE)
    except AttributeError:
        abort(404)

    try:
        prezzo_carburante = session["prezzo_carburante"]
        print("prezzo_carburante:", prezzo_carburante)
    except AttributeError:
        abort(404)


    try:
        footnote_prezzo_carburante = session["footnote_prezzo_carburante"]
        print("footnote_prezzo_carburante---->:", footnote_prezzo_carburante)
    except AttributeError:
        abort(404)

    prezzo_carburante_EUR = session['prezzo_carburante_EUR']
    print("-------prezzo_carburante_EUR:-----------------", prezzo_carburante_EUR)
    session["costo_chilometrico"] = round( (float(selected_consumption_value) * prezzo_carburante_EUR), 2) ## average gasoline price
    print("prezzo_carburante_EUR---->:", prezzo_carburante_EUR)
    print("costo chilometrico -----> ", str(session["costo_chilometrico"]))
    costo_finale =  str(session["costo_chilometrico"])
    # print(costo_finale + " (EUR)")
    costo_finale_EUR = costo_finale + " (EUR/100 km)"



    data_COSTI = [{
        'COSTI_day': selected_COSTI_day,
        'alimentazione': FUEL_TYPE,
        'consumption': consumo_medio
    }]


    data_COSTO_CHILOMETRICO = [{
        'COSTO_CHILOMETRICO': costo_finale_EUR
    }]

    print("-----data_COSTO_CHILOMETRICO----------------:",  costo_finale_EUR)

    return render_template("index_costi_chilometrici.html",
                           data_COSTI=data_COSTI,
                           data_COSTO_CHILOMETRICO=data_COSTO_CHILOMETRICO)
'''


#########################################################################################
#########################################################################################
#########################################################################################
#########################################################################################
## questionario ---------------- ########################################################

"""
@app.route('/questionario/', methods=['GET', 'POST'])
def questionario():
    # if request.method == "POST":
        print("----questionario-----")
        # return redirect("http://www.google.com/") ## external site
        return redirect("https://forms.office.com/e/9zugWShe5q?origin=lprLink")
"""



@app.route('/questionario_ENEA/', methods=['GET', 'POST'])
def questionario_ENEA():
    if request.method == "POST":
        print("----questionario-----")
        session["regione"] = 1
        session["alimentazione"] = 1
        session["consumo_medio"] = ''
        session["consumo_medio_ele_plug"] = ''
        session['consumo_medio_ele_plug_nuovo'] = ''
        session["classe_attuale"] = 0
        session["classe_nuovo"] = 0
        session["alimentazione_nuova"] = 1
        session['nome_alimentazione'] = ''
        session['nome_alimentazione_nuova'] = ''
        session["km_percorsi"] = 15000
        session["perc_urbana"] = 40
        session["consumo_medio_nuovo"] = 5.5
        session["KW_attuale"] = 45
        session["KW_nuovo"] = 45
        session['region_name'] = ''
        session['costo_bollo_auto_nuova'] = 0

        print(session["KW_nuovo"])
        ## TRY if session exists (get "regione")


        ##----- scegli REGIONE ----- ####################################
        try:
            session["regione"] = request.form.get("regione")
            selected_region = session["regione"]
            print("selected_region:", selected_region)
            selected_region = int(selected_region)
        except:
            session["regione"] = 1
            selected_region = session["regione"]
            print("selected_region: ", session["regione"])

        if selected_region == 1:
            region = "Abruzzo"
        elif selected_region == 2:
            region = "Basilicata"
        elif selected_region == 3:
            region = "Calabria"
        elif selected_region == 4:
            region = "Emilia Romagna"
        elif selected_region == 5:
            region = "Friuli Venezia Giulia"
        elif selected_region == 6:
            region = "Lazio"
        elif selected_region == 7:
            region = "Liguria"
        elif selected_region == 8:
            region = "Lombardia"
        elif selected_region == 9:
            region = "Marche"
        elif selected_region == 10:
            region = "Molise"
        elif selected_region == 11:
            region = "Piemonte"
        elif selected_region == 12:
            region = "Prov.A.Bolzano"
        elif selected_region == 13:
            region = "Prov.A.Trento"
        elif selected_region == 14:
            region = "Puglia"
        elif selected_region == 15:
            region = "Sardegna"
        elif selected_region == 16:
            region = "Sicilia"
        elif selected_region == 17:
            region = "Toscana"
        elif selected_region == 18:
            region = "Umbria"
        elif selected_region == 19:
            region = "Valle d'Aosta"
        elif selected_region == 20:
            region = "Veneto"


        try:
            session['region_name'] = region
            print("------regione------------>>>:", region)
        except:
            print("----make selection -----")

        #### ---- Km percorsi ---------- ##########################################
        try:
            session["km_percorsi"] = request.form.get("km_percorsi")
            print("----- km percorsi -------:", session["km_percorsi"] )
        except:
            session["km_percorsi"] = 0
            print("----- km percorsi -------:", session["km_percorsi"])

        #### --- % percorrenza urbana ------ ######################################
        try:
            session["perc_urbana"] = request.form.get("perc_urbana")
            print("----- perc_urbana -------:", session["perc_urbana"])
        except:
            session["perc_urbana"] = 40
            print("----- perc_urbana -------:", session["perc_urbana"])


        ##### ----------- alimentazione auto ------------- ########################
        try:
            session["alimentazione"] = request.form.get("alimentazione")
            print("------- alimentazione auto --------:", session["alimentazione"])
            selected_alimentazione = int(session["alimentazione"])
        except:
            session["alimentazione"] = 1
            selected_alimentazione = int(session["alimentazione"])

        if selected_alimentazione == 1:
            alimentazione = "Benzina"
        elif selected_alimentazione == 2:
            alimentazione = "Gasolio"
        elif selected_alimentazione == 3:
            alimentazione = "GPL"
        elif selected_alimentazione == 4:
            alimentazione = "Metano"
        elif selected_alimentazione == 5:
            alimentazione = "Benzina/GPL"
        elif selected_alimentazione == 6:
            alimentazione = "Benzina/Metano"
        elif selected_alimentazione == 7:
            alimentazione = "Gasolio/GPL"
        elif selected_alimentazione == 8:
            alimentazione = "Gasolio/Metano"
        elif selected_alimentazione == 9:
            alimentazione = "Elettrico"
        elif selected_alimentazione == 10:
            alimentazione = "Full Hybrid Elettrico/Benzina"
        elif selected_alimentazione == 11:
            alimentazione = "Ibrido plug-in Elettrico/Benzina"

        try:
            session['nome_alimentazione'] = alimentazione
            print("------nome_alimentazione------------>>>:", alimentazione)
        except:
            print("----make selection -----")

        #### ---- consumo medio attuale ---------- ##########################################
        try:
            session["consumo_medio"] = request.form.get("consumo_medio")
            print("----- consumo_medio -------:", session["consumo_medio"])
        except:
            session["consumo_medio"] = 5.5
            print("----- consumo_medio -------:", session["consumo_medio"])

        ### ---- consumo medio attuale ---------- ##########################################
        try:
            session["consumo_medio_ele_plug"] = request.form.get("consumo_medio_ele_plug")
            print("----- consumo_medio_ele_plug_attuale -------:", session["consumo_medio_ele_plug"])
        except:
            session["consumo_medio_ele_plug"] = 5.5
            print("----- consumo_medio_ele_plug_attuale -------:", session["consumo_medio_ele_plug"])

        #### --- KW attuale ----------------------------######################################
        try:
            session["KW_attuale"] = request.form.get("KW_attuale")
            print("----- KW_attuale -------:", session["KW_attuale"])
        except:
            session["KW_attuale"] = 55
            print("----- KW_attuale -------:", session["KW_attuale"])

        ##### ----------- Classe ambientale auto attuale ------------- ########################
        try:
            session["classe_attuale"] = request.form.get("classe_attuale")
            print("------- classe_attuale auto --------:", session["classe_attuale"])
            selected_classe_attuale = int(session["classe_attuale"])
        except:
            session["classe_attuale"] = 1
            selected_classe_attuale = int(session["classe_attuale"])

        if selected_classe_attuale == 1:
            classe_attuale = "Euro 0"
        elif selected_classe_attuale == 2:
            classe_attuale = "Euro 1"
        elif selected_classe_attuale == 3:
            classe_attuale = "Euro 2"
        elif selected_classe_attuale == 4:
            classe_attuale = "Euro 3"
        elif selected_classe_attuale == 5:
            classe_attuale = "Euro 4"
        elif selected_classe_attuale == 6:
            classe_attuale = "Euro 5"
        elif selected_classe_attuale == 7:
            classe_attuale = "Euro 6"
        elif selected_classe_attuale == 8:
            classe_attuale = "Elettrica"

        try:
            session['nome_classe_attuale'] = classe_attuale
            print("------nome_classe_attuale------------>>>:", classe_attuale)
        except:
            print("--- make selection -------")

        ##### ----------- alimentazione auto nuova  ------------- ########################
        try:
            session["alimentazione_nuova"] = request.form.get("alimentazione_nuova")
            print("------- alimentazione_nuova auto --------:", session["alimentazione_nuova"])
            selected_alimentazione_nuova = int(session["alimentazione_nuova"])
        except:
            session["alimentazione_nuova"] = 1
            selected_alimentazione_nuova = int(session["alimentazione_nuova"])


        if selected_alimentazione_nuova == 1:
            alimentazione_nuova = "Benzina"
        elif selected_alimentazione_nuova == 2:
            alimentazione_nuova = "Gasolio"
        elif selected_alimentazione_nuova == 3:
            alimentazione_nuova = "GPL"
        elif selected_alimentazione_nuova == 4:
            alimentazione_nuova = "Metano"
        elif selected_alimentazione_nuova == 5:
            alimentazione_nuova = "Benzina/GPL"
        elif selected_alimentazione_nuova == 6:
            alimentazione_nuova = "Benzina/Metano"
        elif selected_alimentazione_nuova == 7:
            alimentazione_nuova = "Gasolio/GPL"
        elif selected_alimentazione_nuova == 8:
            alimentazione_nuova = "Gasolio/Metano"
        elif selected_alimentazione_nuova == 9:
            alimentazione_nuova = "Elettrico"
        elif selected_alimentazione_nuova == 10:
            alimentazione_nuova = "Full Hybrid Elettrico/Benzina"
        elif selected_alimentazione_nuova == 11:
            alimentazione_nuova = "Ibrido plug-in Elettrico/Benzina"
        elif selected_alimentazione_nuova == 12:
            alimentazione_nuova = "Full Hybrid Elettrico/Gasolio"
        elif selected_alimentazione_nuova == 13:
            alimentazione_nuova = "Ibrido plug-in Elettrico/Gasolio"
        elif selected_alimentazione_nuova == 14:
            alimentazione_nuova = "Idrogeno-elettrico"
        elif selected_alimentazione_nuova == 15:
            alimentazione_nuova = "Idrogeno/Benzina"

        try:
            session['nome_alimentazione_nuova'] = alimentazione_nuova
            print("------nome_alimentazione_nuova------------>>>:", alimentazione_nuova)
        except:
            print("----make selection----")
            alimentazione_nuova = ''



        #### ---- consumo medio auto nuova ---------- ##########################################
        try:
            session["consumo_medio_nuovo"] = request.form.get("consumo_medio_nuovo")
            print("----- consumo_medio_nuovo -------:", session["consumo_medio_nuovo"])
        except:
            session["consumo_medio_nuovo"] = 5.5
            print("----- consumo_medio_nuovo -------:", session["consumo_medio_nuovo"])

        ### ---- consumo medio attuale ---------- ##########################################
        try:
            session["consumo_medio_ele_plug_nuovo"] = request.form.get("consumo_medio_ele_plug_nuovo")
            print("----- consumo_medio_ele_plug_nuovo -------:", session["consumo_medio_ele_plug_nuovo"])
        except:
            session["consumo_medio_ele_plug_nuovo"] = 5.5
            print("----- consumo_medio_ele_plug_nuovo -------:", session["consumo_medio_ele_plug_nuovo"])

        #### --- KW attuale ----------------------------######################################
        try:
            session["KW_nuovo"] = request.form.get("KW_nuovo")
            print("----- KW_nuovo -------:", session["KW_nuovo"])
            potenza_nuova_auto = session["KW_nuovo"]
        except:
            session["KW_nuovo"] = 45
            print("----- KW_nuovo -------:", session["KW_nuovo"])
            potenza_nuova_auto = session["KW_nuovo"]



            ##### ----------- Classe ambientale auto nuovo ------------- ########################
        try:
            session["classe_nuovo"] = request.form.get("classe_nuovo")
            print("------- classe_nuovo auto --------:", session["classe_nuovo"])
            selected_classe_nuova = int(session["classe_nuovo"])
        except:
            session["classe_nuovo"] = 0
            selected_classe_nuova = int(session["classe_nuovo"])

        if selected_classe_nuova == 1:
            classe_nuova = "Euro 0"
        elif selected_classe_nuova == 2:
            classe_nuova = "Euro 1"
        elif selected_classe_nuova == 3:
            classe_nuova = "Euro 2"
        elif selected_classe_nuova == 4:
            classe_nuova = "Euro 3"
        elif selected_classe_nuova == 5:
            classe_nuova = "Euro 4"
        elif selected_classe_nuova == 6:
            classe_nuova = "Euro 5"
        elif selected_classe_nuova == 7:
            classe_nuova = "Euro 6"
        elif selected_classe_nuova == 8:
            classe_nuova = "Elettrica"

        try:
            session['nome_classe_nuova'] = classe_nuova
            print("------nome_classe_nuova------------>>>:", classe_nuova)
        except:
            print("--- make selection -------")

        user = session.sid
        print("user:", user)



        #### check all variables.......
        try:
            region=region
        except:
            region="Lazio"

        try:
            session["km_percorsi"]=session["km_percorsi"]
        except:
            session["km_percorsi"]=15000


        try:
            alimentazione=alimentazione
        except:
            alimentazione="Benzina"

        try:
            session["perc_urbana"]=session["perc_urbana"]
        except:
            session["perc_urbana"]=40


        try:
            session["consumo_medio"]=session["consumo_medio"]
        except:
            session["consumo_medio"]=6

        try:
            session["consumo_medio_ele_plug"]=session["consumo_medio_ele_plug"]
        except:
            session["consumo_medio_ele_plug"]=4

        try:
            alimentazione_nuova = alimentazione_nuova
        except:
            alimentazione_nuova = "Elettrico"

        try:
            session["consumo_medio_nuovo"]=session["consumo_medio_nuovo"]
        except:
            session["consumo_medio_nuovo"]=5.5

        try:
            session["consumo_medio_ele_plug_nuovo"] = session["consumo_medio_ele_plug_nuovo"]
        except:
            session["consumo_medio_ele_plug_nuovo"] = 3.5

        try:
            session["KW_nuovo"] = session["KW_nuovo"]
        except:
            session["KW_nuovo"] = 55


        data_input_user_costi = [{
            'regione': region,
            'km_percorsi': session["km_percorsi"],
            'perc_urbana': session["perc_urbana"],
            'alimentazione_attuale': alimentazione,
            'consumo_medio_attuale': session["consumo_medio"],
            'consumo_medio_ele_plug': session["consumo_medio_ele_plug"],
            'alimentazione_nuova': alimentazione_nuova,
            'consumo_medio_nuovo': session["consumo_medio_nuovo"],
            'consumo_medio_ele_plug_nuovo': session["consumo_medio_ele_plug_nuovo"],
            'potenza_KW_nuovo': session["KW_nuovo"]
        }]

        session["data_input_user_costi"] = data_input_user_costi
        # print(data_input_user_costi)

    return render_template("index_questionario.html", data_input_user_costi=data_input_user_costi)
    # return render_template("index_costi_energia_bollo.html", data_input_user_costi=data_input_user_costi)




"""
@app.route('/invia_risposte_questionario/', methods=['GET', 'POST'])
def invia_risposte_questionario():
    data_input_user_costi = session["data_input_user_costi"]
    print(data_input_user_costi)

    return render_template("index_costi_energia_bollo.html",
                           data_input_user_costi=data_input_user_costi)
"""


###########################################################################################
###########################################################################################
## elaborazione risposte ---------------- #################################################


@app.route('/risposte_questionario/', methods=['GET', 'POST'])
def risposte_questionario():

    costo_energia = 0
    print("session_data_input_user_costi", session["data_input_user_costi"])
    data_input_user_costi = session["data_input_user_costi"]

    print("----- ciccio..........................")

    #### find cost fo traditional fuels
    import httplib2
    from bs4 import BeautifulSoup, SoupStrainer
    from urllib.request import Request, urlopen
    http = httplib2.Http()
    import requests
    import pandas as pd
    import json
    import re
    from re import sub
    from decimal import Decimal



    """
    ## --->> get link of Ministero dell'ambiente e della sicurezza energetica (Statistiche energetiche e minerarie)
    ### ---->> web scraping.... find the web text containing all the information about fuel prices
    url = "https://dgsaie.mise.gov.it/prezzi-settimanali-carburanti"
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser')

    list_FUELS = []
    for tag in soup.findAll(True, {"class": ["ml-2", "text-right"]}):
        # print(tag)
        print(tag.text.strip())
        list_FUELS.append(tag.text.strip())

    index_Benzina = list_FUELS.index("Benzina")
    price_Benzina = list_FUELS[index_Benzina + 1]
    print("--price Benzina--->:", price_Benzina)
    price_Benzina_EUR = float((price_Benzina.split(','))[0])
    print("--price_Benzina_EUR----------------------->>>>:", float(price_Benzina_EUR))
    # session['price_Benzina'] = price_Benzina

    index_Diesel = list_FUELS.index("Gasolio auto")
    price_Diesel = list_FUELS[index_Diesel + 1]
    print("--price Diesel--->:", price_Diesel)
    price_Diesel_EUR = float((price_Diesel.split(','))[0])
    price_Diesel_EUR = float(Decimal(sub(r'[^\d.]', '', price_Diesel)))
    # session['price_Diesel'] = price_Diesel

    index_GPL = list_FUELS.index("GPL")
    price_GPL = list_FUELS[index_GPL + 1]
    print("--price GPL--->:", price_GPL)
    price_GPL_EUR = float((price_GPL.split(','))[0]) / 1000
    print("---price_GPL_EUR----->:", price_GPL_EUR)
    print("---price_GPL----->:", price_GPL)
    # session['price_GPL'] = price_GPL

    index_Metano = list_FUELS.index("Metano")
    price_Metano = list_FUELS[index_Metano + 1]
    print("--price Metano--->:", price_Metano)
    price_Metano_EUR = float(Decimal(sub(r'[^\d.]', '', price_Metano)))
    # session['price_Metano'] = price_Metano
    """

    #### ---- laod TABELLA CARBURANTI in format .CSV-------- ###############################################
    tabella_carburanti_MASE = pd.read_csv(path_app + "/static/prezzi_carburanti_settimanali_2024_05_20.csv")

    price_Benzina = tabella_carburanti_MASE[tabella_carburanti_MASE['NOME_PRODOTTO'] == "Benzina"]['PREZZO'][0]
    price_Benzina_EUR = float((price_Benzina.split(','))[0])
    print("--price_Benzina_EUR----------------------->>>>:", float(price_Benzina_EUR))
    session['price_Benzina'] = price_Benzina

    price_Diesel = tabella_carburanti_MASE[tabella_carburanti_MASE['NOME_PRODOTTO'] == "Gasolio auto"]['PREZZO'][1]
    price_Diesel_EUR = float((price_Diesel.split(','))[0])
    print("--price_Diesel_EUR----------------------->>>>:", float(price_Diesel_EUR))
    session['price_Diesel'] = price_Diesel

    price_GPL = tabella_carburanti_MASE[tabella_carburanti_MASE['NOME_PRODOTTO'] == "GPL"]['PREZZO'][3]
    price_GPL_EUR = float((price_GPL.split(','))[0])
    print("--price_GPL_EUR----------------------->>>>:", float(price_GPL_EUR))
    session['price_GPL'] = price_GPL

    price_Metano = tabella_carburanti_MASE[tabella_carburanti_MASE['NOME_PRODOTTO'] == "Metano"]['PREZZO'][6]
    price_Metano_EUR = float((price_Metano.split(','))[0])
    print("--price_Metano_EUR----------------------->>>>:", float(price_Metano_EUR))
    session['price_Metano'] = price_Metano

    price_elettrico_casa = 0.254
    price_idrogeno_grigio = 1.5


    ###--------------------------------------------------------- ###################
    ###--------------------------------------------------------- ###################

    ### ------------------------ implement cost algorithm -------------------------- ################################
    #################################################################################################################



    ## ------> alimentazione auto attuale
    alimentazione = session['nome_alimentazione']
    print("---nome_alimentazione---:", session['nome_alimentazione'])
    ## se l'alimentazione è un bifuel 50%-50%) o plug in (% elettrico = % percentuale percorrenza cittadina;   %carburante = 1- perc(città))

    ## -----> consumo auto attuale
    consumo = session["consumo_medio"]
    print("---- consumo attuale----:", session["consumo_medio"])

    ## -----> consumo auto nuova
    consumo_nuovo = session["consumo_medio_nuovo"]
    print("---- consumo nuova auto----:", session["consumo_medio_nuovo"])

    ## -------> km annuali percorsi auto attuale
    percorrenza = session["km_percorsi"]
    print("------ Km percorsi------:", session["km_percorsi"])

    ##----------> SE PLUG IN, inserisci percentuale percorrenza in città AUTO ATTUALE
    perc_percorrenza_citta =  session["perc_urbana"]
    print("----perc_percorrenza_citta------:", perc_percorrenza_citta)

    if alimentazione == "Benzina":
        costo_energia = price_Benzina_EUR
    elif alimentazione == "Gasolio":
        costo_energia = price_Diesel_EUR
    elif alimentazione == "GPL":
        costo_energia = price_GPL_EUR
    elif alimentazione == "Metano":
        costo_energia = price_Metano_EUR
    elif alimentazione == "Benzina/GPL":
        costo_energia = price_Diesel_EUR * 0.5 + price_GPL_EUR * 0.5
    elif alimentazione == "Benzina/Metano":
        costo_energia = price_Benzina_EUR * 0.5 + price_Metano_EUR * 0.5
    elif alimentazione == "Gasolio/GPL":
        costo_energia = price_Diesel_EUR * 0.5 + price_GPL_EUR * 0.5
    elif alimentazione == "Gasolio/Metano":
        costo_energia = price_Diesel_EUR * 0.5 + price_Metano_EUR * 0.5
    elif alimentazione == "Elettrico":
        costo_energia = price_elettrico_casa
    elif alimentazione == "Full Hybrid Elettrico/Benzina":
        costo_energia = price_Benzina_EUR
    elif alimentazione == "Full Hybrid Elettrico/Gasolio":
        costo_energia = price_Diesel_EUR
    elif alimentazione == "Ibrido plug-in Elettrico/Benzina":
        costo_energia = price_elettrico_casa * perc_percorrenza_citta + (1 - price_Benzina_EUR * perc_percorrenza_citta)
    elif alimentazione == "Ibrido plug-in Elettrico/Gasolio":
        costo_energia = price_elettrico_casa * perc_percorrenza_citta + (1 - price_Diesel_EUR * perc_percorrenza_citta)

    elif alimentazione == "Idrogeno-elettrico":
        costo_energia = price_idrogeno_grigio
    elif alimentazione == "Idrogeno/Benzina":
        costo_energia = price_idrogeno_grigio * 0.5 + price_Benzina_EUR * 0.5

    print("------ costo energia -------:", costo_energia)

    ########------ COSTO ENERGIA AUTO ANNUALE -------------------------------###########

    try:
        costo_attuale_annuale = round( (float(percorrenza) / 100) * float(consumo) * (float(costo_energia))/1000 , ndigits= 2 ) ### in EUR
        session['costo_attuale_annuale'] = costo_attuale_annuale
        print("--------- costo_attuale_annuale ---------:", session['costo_attuale_annuale'])
    except:
        session['costo_attuale_annuale'] ='inserisci dati'

        ########------ COSTO ENERGIA AUTO NUOVA -------------------------------###########

    try:
        costo_nuovo_annuale = round((float(percorrenza) / 100) * float(consumo_nuovo) * float(costo_energia),
                                      ndigits=2)  ### in EUR
        session['costo_nuovo_annuale'] = costo_nuovo_annuale
        print("--------- costo_nuovo_annuale ---------:", session['costo_attuale_annuale'])
    except:
        session['costo_nuovo_annuale'] = 'inserisci dati'


    tabella_bollo = pd.read_csv(path_app + "/static/tabella dinamica calcoli_02.csv")


    # regione = "Abruzzo"
    # potenza_nuova_auto = 65
    # nuova_alimentazione = 'Gasolio'

    nuova_alimentazione = session['nome_alimentazione_nuova']
    print("----------- nuova_alimentazione--------------:", nuova_alimentazione)

    potenza_nuova_auto = session["KW_nuovo"]
    if potenza_nuova_auto == None:
        potenza_nuova_auto = 45
    print("potenza_nuova_auto", potenza_nuova_auto)
    try:
        potenza_nuova_auto = float(potenza_nuova_auto)
    except ValueError:
        potenza_nuova_auto = 45

    regione = session['region_name']

    print("--- potenza nuova auto:", potenza_nuova_auto)
    print("--- regione:", regione)

    tab = tabella_bollo[(tabella_bollo["Regione"] == regione)]
    if potenza_nuova_auto < 100:
        tab = tab[tab["level_KW"] == 'L']
    elif potenza_nuova_auto >= 100:
        tab = tab[tab["level_KW"] == 'H']

    print(tab)
    tab = tab.reset_index()



    if nuova_alimentazione == "Elettrico":
        costo_bollo_auto_nuova = round( float(tab[nuova_alimentazione][0] * potenza_nuova_auto), ndigits=2)
        print("----costo_bollo_auto_nuova----:", costo_bollo_auto_nuova)

    elif (nuova_alimentazione == "Benzina") | (nuova_alimentazione == "Gasolio"):
        costo_bollo_auto_nuova = round( tab['Euro 6'][0] * potenza_nuova_auto, ndigits=2)
        print("------ I am here--------------------------------------")

    elif (nuova_alimentazione == "GPL") | \
            (nuova_alimentazione == "Metano") | \
            (nuova_alimentazione == "Benzina/GPL") | \
            (nuova_alimentazione == "Gasolio/GPL") | \
            (nuova_alimentazione == "Gasolio/Metano") | \
            (nuova_alimentazione == "Full Hybrid Elettrico/Benzina") | \
            (nuova_alimentazione == "Full Hybrid Elettrico/Gasolio") | \
            (nuova_alimentazione == "Ibrido plug-in Elettrico/Benzina") | \
            (nuova_alimentazione == "Ibrido plug-in Elettrico/Gasolio") | \
            (nuova_alimentazione == "Idrogeno-Elettrico") | \
            (nuova_alimentazione == "Idrogeno/Benzina"):
        costo_bollo_auto_nuova = tab[nuova_alimentazione][0] * potenza_nuova_auto

    session['costo_bollo_auto_nuova'] = round(costo_bollo_auto_nuova, ndigits=2)

    if (session['costo_attuale_annuale'] and session['costo_nuovo_annuale']) == str('inserisci dati'):
        print("----costo bollo da definire-------")
        session['costo_bollo_auto_nuova'] = '-'

    ### costo energia ANNUALE (auto da acquistare)
    data_COSTI_energia_bollo = [{
        'costo_energia_auto_attuale': session['costo_attuale_annuale'],
        'costo_energia_auto_nuova': session['costo_nuovo_annuale'],
        #  'costo_bollo_auto_attuale': '-',
        'costo_bollo_auto_nuova': session['costo_bollo_auto_nuova']
    }]

    print("data_input_user_costi----------------final-----------------:", data_input_user_costi)

    return render_template("index_costi_energia_bollo.html",
                           data_COSTI_energia_bollo=data_COSTI_energia_bollo,
                           data_input_user_costi=data_input_user_costi)


##########################################################################################
##########################################################################################


if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True, threaded=True, use_reloader=False)



