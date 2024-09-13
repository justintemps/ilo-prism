import sdmx
import sqlite3


def get_dataflows():
    '''Get a list of dataflows and insert them into the database together with their names.'''

    # Connect to the database
    con = sqlite3.connect("store/ilo-prism.db")
    cur = con.cursor()

    # Get a list of languages and their ids
    # {'en': 1, 'fr': 2, 'es': 3}
    cur.execute("SELECT * FROM language")
    languages = cur.fetchall()
    languages = {lang[1]: lang[0] for lang in languages}

    # Create an SDMX Client client
    ilostat = sdmx.Client("ILO")

    # Get a list of all of the data flows
    dataflows_msg = ilostat.dataflow()

    # Get the dataflows
    dataflows = dataflows_msg.dataflow

    for dataflow in dataflows:
        cur.execute(
            "INSERT OR IGNORE INTO dataflow(code) VALUES(?)", (dataflow,))
        dataflow_uid = cur.lastrowid
        con.commit()

        # Get the localized names of the dataflow
        names = dataflows[dataflow].name.localizations
        for lang in names:
            if lang in languages:
                cur.execute('''
                            INSERT OR IGNORE INTO dataflow_name (
                                dataflow_uid, language_uid, name
                            ) VALUES(?, ?, ?)''',
                            (dataflow_uid, languages[lang], dataflows[dataflow].name.localizations[lang]))

        descriptions = dataflows[dataflow].description.localizations
        for lang in descriptions:
            if lang in languages:
                cur.execute('''
                            INSERT OR IGNORE INTO dataflow_description (
                                dataflow_uid, language_uid, description
                            ) VALUES(?, ?, ?)''',
                            (dataflow_uid, languages[lang], dataflows[dataflow].description.localizations[lang]))
    cur.close()


if __name__ == '__main__':
    get_dataflows()
