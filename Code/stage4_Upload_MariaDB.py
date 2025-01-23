"""
Teil 4: Upload der Daten in die Maria Datenbank

Output: Daten in der persönlichen Maria DB gespeichert

Mit der Verwendung vom mysql-connector Package können alle Elemente auf einmal hochgeladen werden.
Bei anderen Varianten gab es Probleme. Beschreibung und Verwendung von mysql-connector hier gefunden:
https://www.digitalocean.com/community/tutorials/how-to-store-and-retrieve-data-in-mariadb-using-python-on-ubuntu-18-04

Für das Erstellen der Maria DB & die Formate je Spalte im txt-File "01_create_db_flight_arrivals" nachschauen
"""

import json
import mysql.connector as db

#Funktion mit dem Übergeben des stage3-File als Parameter
def upload_MariaDB(file_path):

    #Hier die Parameter setzen von unserer Maria Database und die neu erstelle Database angeben
    #db.connect stellt den Zugang zur Datenbank her mit den notwendigen Parametern
    connection = db.connect(host='127.0.0.1', user='cip_user', password='cip_pw', database='flight_arrivals')
    #connection.cursor(): Erstellt ein Cursor-Objekt, um SQL-Befehle zur oben spezifizierten DB ausführen zu können
    cursor = connection.cursor()

    #SQL-Befehl zum Einfügen der Daten: INSERT INTO und dann den tbl-Namen in der erstellten database
    #Im Anschluss müssen dieselben Keys, die in der Datenbank vorhanden sind, innerhalb des Strings angegeben werden
    sql = """
    INSERT INTO tbl_arrivals_geneva (flight_id, airline_name, date_arrival, estimated_scheduled_arrival, actual_arrival,
    departure_destination, status, arrival_destination, code_share, delay_arrival)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    #Einlesen der zuvor erstellten JSON-Datei mit with open ("r" = read), gespeichert in Variable file_path
    with open(file_path, 'r') as file:
        #Liest die JSON-Datei und wandelt sie in ein Python-Objekt, sprich ein list-Object um.
        data = json.load(file)

    #Schleife für jedes dictionary im list-Objekt data zu durchlaufen
    for item in data:
        #Erstelt ein tupel dass Werte aus dem dictionary extrahiert.
        #get-Methode notwendig: Konvertiere allfällige NaN-Werte zu null-Werte für die Datenbank
        #Beim Upload eines pd.frames führte dies zu Fehler, da NaN- anstatt null-Werte vorhanden waren
        values = tuple(
            item.get(key) for key in ["flight_id", "airline_name", "date_arrival", "estimated_scheduled_arrival",
                                      "actual_arrival", "departure_destination", "status",
                                      "arrival_destination", "code_share", "delay_arrival"])
        cursor.execute(sql, values)
        #Fügt Werte aus tuple Element "values" in unsere DB (gespeichert in Variable "sql") ein

    #Änderungen in der Datenbank speichern
    connection.commit() #Bestätigt die Transaktion und speichert die Änderungen in der Datenbank.
    cursor.close() #Schließt den Cursor zur Datenbank
    connection.close() #Schließt die Verbindung zur Datenbank
    print("Daten wurden in die persönliche Maria DB übertragen!")

file_path = '03_clean_data/all_arrivals_Geneva_stage3.json' #Angabe zum finalen File stage3
upload_MariaDB(file_path)                                   #Funktionsaufruf mit Angabe der JSON-Datei