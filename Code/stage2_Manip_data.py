"""
Teil 2: Manuelles Verunreinigen der sauberen Daten und zusammenfügen der Datensätze

Da die zur Verfügung gestellten Daten sehr sauber sind, wird hier eine künstliche Verunreinigung herbeigefügt.
Im Anschluss werden die Daten der einzelnen Scraping Vorgänge zusammengefügt.
Output: Zusammenzug der Daten zur weiteren Behandlung in einem json-files _stage2

Vorhandene Verunreinigungen im Output:
#1 "status": Gelandet/Annuliert/Unbekannt
#2 "flight_id": Nummer/NaN
#3 "departure_destination: Nur in Grossbuchstaben
#4 "actual_arrival": Zeitangabe/leerer string
#5 "airline_name": Nur in Grossbuchstaben
#6 Duplikate: Doppelte Einträge vorhanden

Erklärung der Imports:
#1 import pandas as pd: Für die Datenmanipulation wird pandas verwendet, um Dataframes zu erstellen
#2 import numpy as np: Wird verwendet um Verunreinigungen, sprich willkürliche NaN-Werte zu setzen
#3 import random: Verwendung von Zufallauswahlen für die Datenmanipulation
#4 import os: Für die Interaktion mit dem Betriebssystem, in diesem Fall mit dem Dateiverzeichnis
#5 import json: Für das Einlesen und speichern von Daten im json-Format
#6 from datetime import datetime: Für die Handhabung von Datumswerten
"""

import pandas as pd
import numpy as np
import random
import os
import json
from datetime import datetime

day_date = datetime.now().strftime("%d%m%Y")  #aktuelles Datum und Format festlegen, wird in der jeweiligen Originaldatei verwendet bei der Bezeichnung

#Schritt 1: Duplikate einfügen
def insert_duplicates(df_arrivals, min_changes=10, max_changes=20):
    #Zwischen 10 und 20 Duplikate sollen entstehen
    #Aus dem dataframe werden zufällig eine Anzahl Indizes ausgewählt, beschränkt durch min_ und max_changes
    dup_ind = random.sample(list(df_arrivals.index), random.randint(min_changes, max_changes))
    #Kopieren der Einträge aus dup_ind durch Auswahl der Gruppe von Zeilen mittels loc[]
    duplicates = df_arrivals.loc[dup_ind].copy()
    #Mit concat dem dataframe die kopierten Einträge anhängen, den index dabei ignorieren
    df_arrivals = pd.concat([df_arrivals, duplicates], ignore_index=True)
    #print(df_arrivals.head())
    return df_arrivals

#Schritt 2: "status" verunreinigen
def manip_status(df_arrivals, min_changes=10, max_changes=20):
    #Total sollen willkürlich zwischen 10 bis 20 "status" Felder verunreinigt werden
    #Die Indizes werden willkürlich gewählt
    status_indices = random.sample(list(df_arrivals.index), random.randint(min_changes, max_changes))
    # Der Wert der ausgewählten Elemente in der Spalte "status" wird auf NaN gesetzt.
    df_arrivals.loc[status_indices, 'status'] = np.nan
    #print(df_arrivals.head())
    return df_arrivals

#Schritt 3: "flight_id" verunreinigen
def manip_id(df_arrivals, min_changes=10, max_changes=20):
    #Total sollen willkürlich zwischen 10 bis 20 "flight_id" Felder verunreinigt werden
    #mit random zufällig eine Anzahl Indizes auswählen
    flight_id_index = random.sample(list(df_arrivals.index), random.randint(min_changes, max_changes))
    #Der Wert der ausgewählten Elemente in der Spalte "flight_id" wird auf "NaN" gesetzt.
    df_arrivals.loc[flight_id_index, 'flight_id'] = np.nan
    print(df_arrivals.head())
    return df_arrivals

#Schritt 4: Speichern der verunreinigten Daten
def save_stage2(df_arrivals):
    #Daten in folgender json-Datei speichern
    file_path = '02_manip_data/all_arrivals_Geneva_stage2.json'
    # file_path = '02_manip_data/test_arrivals_Geneva_versionb_stage2.json' #Zum Testen dieses File verwenden
    #Zuerst muss überprüft werden, ob die Datei bereits existiert
    if os.path.exists(file_path):
        #Wenn bereits ein File vorhanden ist, dann wird das bestehende File im Pfad ausgewählt
        existing_df = pd.read_json(file_path)
    else:
        #Wenn die Datei nicht existiert (1. Durchgang), wird der aktuelle Dataframe weitervwendet
        existing_df = pd.DataFrame()

    #Füge den neuen DataFrame zum hinzu
    combined_df = pd.concat([existing_df, df_arrivals], ignore_index=True)
    #Speichere den DataFrame in der JSON-Datei
    combined_df.to_json(file_path, orient='records', force_ascii=False, indent=4)
    print("Neue Daten wurden erfolgreich hinzugefügt!")


def main():
    # Einlesen der ursprünlgichen Originaldatei und dessen Inhalt in ein panda dataframne laden.
    file_path = f'01_downloads/{day_date}_arrivals_Geneva_stage1.json'  #Speicherort der Originaldatei
    # file_path = f'01_downloads/{testtag1_arrivals_Geneva_stage1.json' #Für Testzwecke dieses File benutzen
    df_arrivals = pd.read_json(file_path)                               #Laden in DataFrame
    print(df_arrivals.head())                                           #Kontrolle des Aufbaus
    # print(df_arrivals.info)
    # print(df_arrivals.columns)

    df_arrivals = insert_duplicates(df_arrivals)    #Schritt 1: Duplikate einfügen
    df_arrivals = manip_status(df_arrivals)         #Schritt 2: "status" verunreinigen
    df_arrivals = manip_id(df_arrivals)             #Schritt 3: "flight_id" verunreinigen
    save_stage2(df_arrivals)                        #Schritt 4: Speichern

if __name__ == "__main__":
    main()