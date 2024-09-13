import sdmx
import sqlite3


def get_cl_areas():
    '''Get a list of areas from the codelist and insert them into the database
    together with their names.'''

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
    codelist_msg = ilostat.codelist("CL_AREA")

    # Get the items
    codelist_items = codelist_msg.codelist.CL_AREA.items

    # For each item in the codelist,
    for item in codelist_items:
        # Insert the area into the database
        cur.execute("INSERT OR IGNORE INTO cl_area(code) VALUES(?)", (item,))
        cl_area_uid = cur.lastrowid
        con.commit()

        # Get the localized names of the area
        # Example: {'en': 'Egypt', 'es': 'Egipto', 'fr': 'Egypte'}
        names = codelist_items[item].name.localizations

        # Insert the names of the area into the database
        for lang in names:
            if lang in languages:
                cur.execute('''
                            INSERT OR IGNORE INTO cl_area_name (
                                cl_area_uid, language_uid, name
                            ) VALUES(?, ?, ?)''',
                            (cl_area_uid, languages[lang], codelist_items[item].name.localizations[lang]))
                con.commit()

    # Close the cursor
    con.close()


if __name__ == '__main__':
    get_cl_areas()
