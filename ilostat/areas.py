import sdmx
import sqlite3


def get_cl_areas():
    '''Get a list of areas from the codelist and insert them into the database
    together with their names.'''

    # Connect to the database
    con = sqlite3.connect("ilo-prism-cache.db")

    # Create a cursor
    cur = con.cursor()

    # Create an SDMX Client client
    ilostat = sdmx.Client("ILO")

    # Get a list of all of the data flows
    codelist_msg = ilostat.codelist("CL_AREA")

    # Get the items
    codelist_items = codelist_msg.codelist.CL_AREA.items

    # For each item in the codelist,
    for key in codelist_items:
        cur.execute(
            "INSERT INTO cl_areas(cl_area, name) VALUES(?, ?)", (key, codelist_items[key].name["en"]))
        con.commit()

    # Close the cursor
    con.close()
