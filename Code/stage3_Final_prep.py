"""
Teil 3: Data cleaning und erstellen der finalen Version

Output: Ziel ist es einen sauberen Datensatz in einem json-file für die kommende Analyse zu haben.

Die Datengrundlage _stage2 beinhaltet unsaubere Daten. Diese Verunreinigungen werden in diesem Code bereinigt:
#1 "status": Gelandet/Annuliert/Unbekannt --> Nur Gelandet oder Annuliert
#2 "flight_id": Nummer/NaN --> Mindestens der Airlinecode
#3 "departure_destination: Nur in Grossbuchstaben --> normale Schreibweise
#4 "actual_arrival": Zeitangabe/leerer string --> Zeitangabe, sofern gelandet
#5 "airline_name": Nur in Grossbuchstaben --> normale Schreibweise
#6 Duplikate: Doppelte Einträge vorhanden --> keine Duplikate

Die Daten sollen zudem mit folgenden Parameter erweitert werden:
#1 delay_arrival: Differenz zwischen der geschätzten und tatsächlichen Ankunftszeit berechnen
#2 arrival_destination: Für jeden FLug muss der Ankunftsort Genf hinterlegt sein
#3 arrival_date: Das Datum wurde aus Strukturgründen bereits im _stage1-File hinzugefügt.
"""

import pandas as pd                             #Daten mittels panda-frame bearbeiten

# Festlegen der Ausgabe um einzelne Schritte visuell zu prüfen
pd.set_option('display.max_rows', None)         #bei print Aufruf alle Zeilen ausgeben
pd.set_option('display.max_columns', None)      #bei print Aufruf alle Spalten angeben

# Schritt 1: Hinzufügen neuer Spalten
def add_row(df_arrivals):
    #Anzahl Reihen in Variable speichern, um neue Spalten hinzuzufügen
    len_rows = len(df_arrivals)
    print(f'3 Spalten mit {len_rows} Zeilen hinzugefügt.')
    print(50*'*')
    # In allen Felder wird zuerst standardmässig ein leeres string-object angewendet
    df_arrivals["delay_arrival"] = [""]*len_rows        #Für die Zeitdifferenz
    df_arrivals["arrival_destination"] = [""]*len_rows  #Für den Ankunftsflughafen
    df_arrivals["code_share"] = [""]*len_rows           #Für den Codeshare - bei Flughafen Genf nicht vorhanden!
    return df_arrivals

# Schritt 2: Duplikate entfernen
def reduce_duplicates(df_arrivals):
    #Zuerst wird die ursprüngliche Länge der gescrapten Daten in einer Variable gespeichert
    original_length = len(df_arrivals)
    #Nun wird nach Duplikaten anhand der flight_id an den einzelnen Tagen "date_arrival" gesucht
    #Wenn ein Duplikat vorhanden ist, wird der zweite Eintrag verworfen
    df_arrivals.drop_duplicates(subset=['date_arrival', 'flight_id'], keep='first', inplace=True)
    #Vergleich der vorherigen Daten mit den neuen sauberen Daten
    final_length = len(df_arrivals)
    print(f'Duplikate entfernen: Zuvor {original_length} Einträge, nun {final_length} Einträge vorhanden.')
    print(50*'*')
    return df_arrivals

# Schritt 3: Format der Datumsangabe festlegen - wichtig für dne Upload in meine Maria DB
def format_date_arrival(df_arrivals):
    # Konvertieren des 'date_arrival'-Feldes von 'DD.MM.YYYY' zu datetime-Objekten
    df_arrivals['date_arrival'] = pd.to_datetime(df_arrivals['date_arrival'], format='%d.%m.%Y')
    # Umwandlung der datetime-Objekte zurück in Strings, jetzt im 'YYYY-MM-DD'-Format
    df_arrivals['date_arrival'] = df_arrivals['date_arrival'].dt.strftime('%Y-%m-%d')
    return df_arrivals

# Schritt 4: Grossbuchstaben zu normaler Schreibweise ändern
def capital_letters(df_arrivals):
    df_arrivals['departure_destination'] = df_arrivals['departure_destination'].str.title()
    df_arrivals['airline_name'] = df_arrivals['airline_name'].str.title()
    df_arrivals['status'] = df_arrivals['status'].str.title()
    return df_arrivals

# Schritt 5: flight_id Ergänzen aus externe Quelle falls nicht vorhanden
def get_flight_id(df_arrivals):
    # Laden der Airlines-Daten von der Raw GitHub-URL
    # https://github.com/elmoallistair/datasets/blob/main/airlines.csv
    airlines_df = pd.read_csv('https://raw.githubusercontent.com/elmoallistair/datasets/main/airlines.csv') # Pfad zur Airlines CSV-Datei

    missing_flight_id = df_arrivals[df_arrivals['flight_id'].isnull()]
    if not missing_flight_id.empty:
        print(f'Flüge ohne flight id:\n {missing_flight_id}')
        print(50 * '*')
    #Iteration über df_arrivals, um fehlende flight_id zu finden und zu ersetzen mit eindeutigen Flugkürzel
    for i, row in df_arrivals.iterrows():
        if pd.isnull(row['flight_id']):
            #Suche nach dem Eintrag in airlines_df, der dem airline_name aus Github-Quelle entspricht
            match = airlines_df[airlines_df['Name'].str.lower() == row['airline_name'].lower()]
            if not match.empty:
                #Wenn eine Übereinstimmung gefunden wurde, aktualisiere den flight_id mit dem ICAO-Wert
                df_arrivals.at[i, 'flight_id'] = match['ICAO'].values[0]

    missing_flight_id_after = df_arrivals[df_arrivals['flight_id'].isnull()]
    print("Fehlende 'flight_id' Einträge nach Bereinigung:")
    print(missing_flight_id_after[['airline_name']])
    print(50 * '*')
    return df_arrivals

# Schritt 6: Befüllen der neuen Spalte mit dem Ankunftsflughafen Geneva
def add_arrival_destination(df_arrivals):
    #Hinzufügen des Ankunftflughafen "GENF" in die neue Spalte
    df_arrivals["arrival_destination"] = "Geneva"
    return df_arrivals

# Schritt 7: Ergänzen der tatsächlichen Ankunftszeit, sofern Zeitangabe fehlt
def add_arrival_time(df_arrivals):
    #prüft die Spalte actual_arrival auf fehlende Werte (NaN)
    #Falls NaN-Werte vorhanden, ersetzen durch None. Grund: None zeigt explizit, dass kein Wert vorhanden ist
    #Iterieren über actual_arrival Werte mit lambda Funktion
    df_arrivals['actual_arrival'] = df_arrivals['actual_arrival'].apply(lambda x: None if pd.isna(x) else x)

    #Überprüfen durch Ausgabe der Flüge die ursprünglich keine Zeitangabe hatten
    missing_actual_arrival = df_arrivals[df_arrivals['actual_arrival'].isnull()]
    #Bedingung: Wenn Feld in Spalte actual_arrival leer (=None) ist, dann ausgeben
    if not missing_actual_arrival.empty:
        print(f'Folgende Einträge haben keine Ankunftszeit:\n {missing_actual_arrival}')
    print(50 * '*')

    #Nun die Werte ersetzen durch den 'estimated_scheduled_arrival' Wert
    #fill.na greift nur die Zellen mit None-Werten auf
    df_arrivals['actual_arrival'] = df_arrivals['actual_arrival'].fillna(df_arrivals['estimated_scheduled_arrival'])
    missing_after = df_arrivals[df_arrivals['actual_arrival'].isnull()]
    print("Fehlende 'actual_arrival' Einträge nach der Bereinigung (sollte leer sein):")
    print(missing_after[['date_arrival', 'estimated_scheduled_arrival', 'actual_arrival']])
    print(50 * '*')

    return df_arrivals

# Schritt 8: Berechnen der Differenz der Ankunftszeiten und Hinzufügen der Werte in die neue Spalte
def time_diff_arrival(df_arrivals):
    #Umwandlung der Zeichenketten in datetime um damit Abweichung in Minuten zu berechnen
    #Für den Upload in Maria DB muss das Format HH:MM vorhanden sein
    df_arrivals['estimated_scheduled_arrival'] = pd.to_datetime(df_arrivals['estimated_scheduled_arrival'], format='%H:%M')
    # errors='coerce' wandelt Fehler in Na-Werte um
    df_arrivals['actual_arrival'] = pd.to_datetime(df_arrivals['actual_arrival'], format='%H:%M', errors='coerce')

    #Berechnung der Differenz in Minuten zwischen der realer und geschätzer Ankunftszeit
    df_arrivals['delay_arrival'] = (df_arrivals['actual_arrival'] -
                                    df_arrivals['estimated_scheduled_arrival']).dt.total_seconds() / 60

    #Hier wurde AI verwendet, um den vorherigen Code zu verschlankern, da dies zuvor eine einzelne Funktion war
    #Mittels lamda-Funktion wird eine zusätzliche Funktion def datetime_to_string ersparrt
    #Rückumwandlung in normales Uhrzeit Format xx:xx, wenn keine Uhrzeit vorhanden sein sollte erscheint ein Na-value
    df_arrivals['estimated_scheduled_arrival'] = df_arrivals['estimated_scheduled_arrival'].dt.strftime('%H:%M')
    df_arrivals['actual_arrival'] = df_arrivals['actual_arrival'].apply(
        lambda x: x.strftime('%H:%M') if pd.notnull(x) else 'NaN')
    return df_arrivals

# Schritt 9: Status aktualisieren falls der Wert nicht vorhanden ist
def get_status(df_arrivals):
    #filtert DataFrame, um alle Fälle zu identifizieren mit actual_arrival-Zeit aber fehlender status Angabe
    missing_status = df_arrivals[df_arrivals['actual_arrival'].notnull() & df_arrivals['status'].isnull()]
    #Überprüft, ob die gefilterte Liste leer ist. Falls nicht leer, dann die Flüge ohne status ausgeben
    if not missing_status.empty:
        print(f'Folgende Einträge besitzen unbekannten Status:\n {missing_status}')
    print(50 * '*')

    #Status der Flüge, die eine actual_arrival-Zeit haben, aber keinen Status aufweisen, auf "Gelandet" gesetzt
    #Logik: Wenn eine Landezeit vorhanden, muss der FLug gelandet sein und kann nicht annuliert worden sein.
    df_arrivals.loc[df_arrivals['actual_arrival'].notnull() &
                    (df_arrivals['status'].isnull() | (df_arrivals['status'] == '')), 'status'] = 'Gelandet'
    #Erneute Überprüfung der Liste ob noch fehlende Status vorhanden sind
    missing_status_after = df_arrivals[df_arrivals['actual_arrival'].notnull() & df_arrivals['status'].isnull()]
    print("Fehlende 'status' Einträge nach Bereinigung:")
    print(missing_status_after[['actual_arrival', 'status']])
    print(50 * '*')

    return df_arrivals

# Schritt 10: Fehlende Werte
# NaN-Werte müssen zwigend als null-Werte vorhanden sein, ansonsten kommt eine Fehlermeldung beim Upload in Maria DB
# Grund: Pandas arbeiten mit der Bezeichnung NaN, Maria DB erfordert jedoch die Bezeichnung null/None bei fehlender Werte
def prepare_null_NAN(df_arrivals):
    # lambda Funktion ersetzt NaN in 'flight_id', 'actual_arrival' und 'delay_arrival' mit None
    df_arrivals['flight_id'] = df_arrivals['flight_id'].apply(lambda x: None if pd.isna(x) else x)
    df_arrivals['actual_arrival'] = df_arrivals['actual_arrival'].apply(lambda x: None if pd.isna(x) else x)
    df_arrivals['delay_arrival'] = df_arrivals['delay_arrival'].apply(lambda x: None if pd.isna(x) else x)
    return df_arrivals

# Schritt 11: Speichern des neuen JSON-Files
# Dieses File wird für den Upload in die Maria DB verwendet - siehe Upload_MariaDB.py
def save_as_stage3(df_arrivals):
    #Nochmals alle NaN-Werte zu null-Werten (None) konvertieren, doppelte Sicherheit da oben bereits durchgeführt
    df_arrivals.replace('NaN', pd.NA, inplace=True)
    #Speichern des dataframes in einer neuen JSON-Datei
    #file_path = '03_clean_data/test_arrivals_Geneva_version_stage3.json' #Für Testzwecke
    file_path = '03_clean_data/all_arrivals_Geneva_stage3.json'
    df_arrivals.to_json(file_path, orient='records', date_format='iso', force_ascii=False, lines=False, indent=4)
    # Wichtige Angaben beim speichern des Files: (Wurde mittels Chat GPT verbessert, da zuvor oft Fehler auftraten)
    # orient='records': jede Zeile des DataFrame als eigenes JSON-Objekt speichern
    # date_format='iso': alle Datums- und Zeitangaben im ISO 8601-Format speichern,
    #                    was eine hohe Kompatibilität und einfache Lesbarkeit gewährleistet
    # force_ascii=False: Erlaubt Darstellung von Non-ASCII-Zeichen direkt im JSON, bei internationalem Text wichtig
    # lines=False: Speichert das JSON in einer standardisierten Struktur, nicht als mehrere Zeilen.
    # indent=4: Formatierte Ausgabe mit Einrückungen, die das JSON lesbar macht.
    print("File wurde gespeichert mit Bezeichnung '_stage3' !")
    print(50 * '*')



def main():
    # Laden der JSON-Datei in ein panda-frame und speichern in der Variable df_arrivals
    # df_arrivals = pd.read_json('02_manip_data/test_arrivals_Geneva_version_stage2.json')
    df_arrivals = pd.read_json(f'02_manip_data/all_arrivals_Geneva_stage2.json') 
    # df_arrivals = pd.read_json('test_all_arrivals_Geneva_stage2.json') #Für Testzwecke dieses File benutzen
    # Ansicht der Struktur um neues frame zu überprüfen
    # print(df_arrivals.info)
    # print(df_arrivals.columns)
    # print(df_arrivals.sample(5))
    print("Übersicht der Datenbereinigung:")
    print(50 * '*')

    #Aufruf der jeweiligen Funktionen um am Ende _stage3 File zu erhalten
    df_arrivals = add_row(df_arrivals)                  #Schritt 1
    df_arrivals = reduce_duplicates(df_arrivals)        #Schritt 2
    df_arrivals = format_date_arrival(df_arrivals)      #Schritt 3
    df_arrivals = capital_letters(df_arrivals)          #Schritt 4
    df_arrivals = get_flight_id(df_arrivals)            #Schritt 5
    df_arrivals = add_arrival_destination(df_arrivals)  #Schritt 6
    df_arrivals = add_arrival_time(df_arrivals)         #Schritt 7
    df_arrivals = time_diff_arrival(df_arrivals)        #Schritt 8
    df_arrivals = get_status(df_arrivals)               #Schritt 9
    df_arrivals = prepare_null_NAN(df_arrivals)         #Schritt 10
    save_as_stage3(df_arrivals)                         #Schritt 11

if __name__ == "__main__":
    main()
