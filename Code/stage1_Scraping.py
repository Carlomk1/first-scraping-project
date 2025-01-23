"""
Teil 1: Scraping der Webseite und speichern der Rohdaten

Grundlegende Informationen und Quellen:
Ziel Seite des Scraping: https://www.gva.ch/de/Site/Passagers/Vols/Informations/Arrivees
Output: tägliche json files mit der Bezeichnung _stage1

Für Exception-Handling wurde folgende Doku verwendet:
https://www.selenium.dev/selenium/docs/api/py/common/selenium.common.exceptions.html

Für den Umgang mit dynamischen Webseiten & Cookie-Buttons wurden hauptsächlich diese zwei Tutorials verwendet:
# https://youtu.be/j7VZsCCnptM?t=1391
# https://www.youtube.com/watch?v=tRNwTXeJ75U

Folgende Importe sind notwendig um den dynamisch erzeugten Inhalt der Webseite zu verarbeiten und zu speichern:
#0 import json: Modul um JSON-Daten zu speichern, angewendet um Datenstruktur in JSON-String zu konvertieren.
#1 from selenium import webdriver: Automatisierte Steuerung des Webbrowsers
#2 from selenium.webdriver.common.by import By: Lokalisierung von Elementen mittels x-path Angabe
#3 from selenium.webdriver.support.ui import WebDriverWait: Wartebeingungen & Ladezeiten von Webseite
#4 from selenium.webdriver.support import expected_conditions as EC: Wartebedingungen & Ladezeiten von Elementen
#5 from datetime import datetime: Zur Angabe des Ausführungs- respektive Ankunftsdatums
#6 import time: Für Pausierung des Skriptes bei Ladevorgängen der Webseite
#7 from selenium.webdriver.support.select import Select: Notwendig für den Zugriff auf Dropdown-Elemente
#8 from selenium.common.exceptions import NoSuchElementException, TimeoutException: Exception-handling von Selenium
"""

import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException

#Alle Funktionen befinden sich innerhalb der Klasse "FlightScraper"
class FlightScraper():

    #Konstruktor
    def __init__(self, url):
        self.url = url                      #Übernimmt die URL der Webseite
        self.driver = webdriver.Chrome()    #Als Browser (driver) wird Chrome festgelegt
        self.driver.maximize_window()       #Dass alle Elemente sichtbar sind, wir die Fensteranzeige maximiert

    #Schritt 1: Öffnen der Webseite und akzeptieren von Cookies
    def open_website(self):
        self.driver.get(self.url) #Öffnen der Webseite mit Pfad in der Variable "url"
        wait = WebDriverWait(self.driver, 5) #Warten von maximal 5 sek bis Webseite geladen ist
        #Warten (wait.until) bis der Button (siehe x-path) zum Akzeptieren der Cookies klickbar ist (EC.element_to_be_clickable)
        accept_all_cookies_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')))
        accept_all_cookies_button.click()   #Akzeptieren der Cookies durch klicken auf den Button

    #Schritt 2: Festlegen der Sucheinstellungen
    def set_time_and_start_search(self):
        #Anwählen des Feldes "Uhrzeit" um das Dropdown Menu auszuklappen
        time_field = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="p_lt_ctl04_HeaderSearchForm_DateHour"]')))
        time_field.click()
        #Anwählen der frühstmöglichen Ankunftszeit, standardmässig 4 Uhr im Dropdown Menu, diese bseitzt index(1)
        Select(time_field).select_by_index(1)
        #Betätigen des Buttons "Suche" um die ersten Ankünfte des Tages zu laden
        search_button = self.driver.find_element(By.XPATH, '//*[@id="p_lt_ctl04_HeaderSearchForm_searchBtn"]')
        search_button.click()

    #Schritt 3: Tabellenerweiterung
    def expand_flights_table(self):
        #Innerhalb der while-Schleife wird die Tabelle solange erweitert, wie die Bedingung erfüllt ist
        #In diesem Fall ist die Bedingung: Solange der Button zur Tabellenerweiterung erscheint
        while True:
            try:
                #Warten bis der Button "Mehr Flüge laden" clickbar ist
                more_flights_button = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="p_lt_ctl07_pageplaceholder_p_lt_ctl00_FlightsList_MoreFlights"]')))
                #Anwählen des Buttons "Mehr Flüge laden"
                more_flights_button.click()
                #dynamischen Inhalt Zeit zum Laden zu geben, pausieren des Skriptes
                time.sleep(2)
            #Falls kein Button mehr vorhanden ist bzw. die Ladezeit vergangen ist beenden der Funktion
            except (TimeoutException, NoSuchElementException):
                break #Keine weiteren Flüge zu laden, am Ende der Tabelle angelangt

    #Schritt 4: Sammeln der Flugdaten aus der erweiterten Tabelle
    def get_flights(self):
        flights_data = [] #Leeres List-Element um im Anschluss Daten darin zu speichern
        i = 1  #Start bei der ersten Zeile der Flugtabelle, i wird als Variable in den einzelnen x-pathes verwendet
        #Mit der while-Schlaufe die Daten solange in der Liste sammeln, bis die Bedingung nicht mehr erfüllt ist
        #Bedingung: Solange Einträge in der dynamischen Tabelle vorhanden sind (durch Indexangabe)
        while True:
            try:
                #x-path zur fünften Spalte jeder Zeile [i], die die flight_id enthält.
                flights_path = f'//*[@id="flightsList"]/tr[{i}]/td[5]'
                flight_elements = self.driver.find_elements(By.XPATH, flights_path)


                if not flight_elements:
                    break #Beenden der Schleife, wenn keine weiteren Flüge vorhanden sind durch fehlende flight_id

                #Extrahieren der Daten und speichern im dictionary flight (key=Attributname, value=Flugdaten)
                #Zugriff auf die einzelnen Variablen via x-path und spezifischer Zeilennummer {i}
                #Extrahieren des textes mit .text
                flight = {
                    "flight_id": flight_elements[0].text,
                    "airline_name": self.driver.find_element(By.XPATH, f'//*[@id="flightsList"]/tr[{i}]/td[4]').text,
                    #Das Datum wird "manuell" hinzugefügt
                    "date_arrival": datetime.now().strftime("%d.%m.%Y"),
                    "estimated_scheduled_arrival": self.driver.find_element(By.XPATH,f'//*[@id="flightsList"]/tr[{i}]/td[1]/span[1]').text,
                    "actual_arrival": self.driver.find_element(By.XPATH, f'//*[@id="flightsList"]/tr[{i}]/td[2]').text,
                    "departure_destination": self.driver.find_element(By.XPATH,f'//*[@id="flightsList"]/tr[{i}]/td[3]/span').text,
                    "status": self.driver.find_element(By.XPATH, f'//*[@id="flightsList"]/tr[{i}]/td[7]').text,
                }

                #Speichern der FLugdaten (dictionary) in der Liste
                flights_data.append(flight)
                #Sobald eine Zeile beendet ist mit i +=1 zur nächsten Zeile bzw. Ankunft übergehen
                i += 1

            #Wenn beim letzten Element der Tabelle angekommen, dann durch NoSuchElementException beenden
            except NoSuchElementException:
                print(f"Keine weiteren Elemente gefunden, Abbruch bei Flug {i}: {flights_data}.")
                break   #Beim Auftreten von NoSuchElement, Schleife beenden
            #Für alle anderen Arten von Ausnahmen den Index angeben für die manuelle Überprüfung der Zeile
            except Exception:
                print(f"Fehler beim Abrufen von Daten für Flug {i}: {flights_data}.")
                break

        return flights_data #Am Ende zurückgeben der befüllten Liste

    #Schritt 5: Schliessen des Chrome-Browsers nach Scraping Vorgang
    def close_browser(self):
        self.driver.quit()


def main():
    url = 'https://www.gva.ch/de/Site/Passagers/Vols/Informations/Arrivees' #Ziel-URL einmalig festlegen
    day_date = datetime.now().strftime("%d%m%Y")                            #Format der Datumsanagben festlegen
    scraper = FlightScraper(url)            #URL in Klasse übergeben für den Funktionsaufruf
    scraper.open_website()                  #Schritt 1: Webseite öffnen
    scraper.set_time_and_start_search()     #Schritt 2: Einstellungen wählen
    scraper.expand_flights_table()          #Schritt 3: Tabellenerweiterung
    flights_data = scraper.get_flights()    #Schritt 4: Starten des Scraping

    #Speicherort der json-Datei
    file_path = f'01_downloads/{day_date}_arrivals_Geneva_stage1.json'
    # file_path = f'01_downloads/{testtag1_arrivals_Geneva_stage1.json' #Für Testzwecke

    #Öffnen der Datei und Daten übertragen
    with open(file_path, 'w', encoding='utf-8') as f:
        #Datenstruktur in JSON-String konvertieren
        json.dump(flights_data, f, ensure_ascii=False, indent=4)
    print("Scraping beendet!")

    scraper.close_browser()                 #Schritt 5: Browser Sitzung schliessen

if __name__ == '__main__':
    main()

"""
Der Aufbau der dynamischen Tabelle bzw. die Verwendung der X-Pathes im Code ist wiefolgt:
// Startet die Suche im gesamten Dokument (Quelltext) --> Quelltextsuche
* Für jeden Knoten, unabhängig vom Knotentyp -->Alle Typen
[@id="Wert"] Sucht die Verknüpfung, deren id-Attribut den in "..." stehenden Wert hat. --> Attribut
/tr[Zahl] Wählt das angegebene tr-Element aus (child der vorhergehenden Verknüpfung) --> Zeile
/td[Zahl] Wählt das angegebene td-Element innerhalb der vorherigen gewählten Zeile --> Spalte
/span[1]: Wählt das erste span-Element innerhalb der ausgewählten Zelle.

Beispiele:
//*[@id="flightsList"]/tr[5]/td[2] --> Suche nach Wert der Zeile 5 in der 2 Spalte: Erwartete Ankunftszeit Flug 1
//*[@id="flightsList"]/tr[6]/td[2] --> Suche nach Wert der Zeile 6 in der 2 Spalte: Erwartete Ankunftszeit Flug 2

//*[@id="flightsList"]/tr[3]/td[1]/span[1] 
--> Suche nach Werte der Zeile 3 in der 1 Spalte und dort das erste Element: Tatsächliche Ankunftszeit
"""