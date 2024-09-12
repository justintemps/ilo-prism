import sdmx
import sqlite3


def get_cl_areas():
    '''Get a list of areas from the codelist and insert them into the database
    together with their names.'''

    # Connect to the database
    con = sqlite3.connect("store/ilo-prism.db")
    cur = con.cursor()

    # Create an SDMX Client client
    ilostat = sdmx.Client("ILO")

    # Get a list of all of the data flows
    codelist_msg = ilostat.codelist("CL_AREA")

    # Get the items
    codelist_items = codelist_msg.codelist.CL_AREA.items

    # For each item in the codelist,

    for item in codelist_items:
        name_en = codelist_items[item].name["en"]
        name_fr = codelist_items[item].name["fr"]
        name_es = codelist_items[item].name["es"]

        cur.execute(
            "INSERT INTO cl_area(code, name_en, name_fr, name_es) VALUES(?, ?, ?, ?)",
            (item, name_en, name_fr, name_es))
        con.commit()

    # Close the cursor
    con.close()


if __name__ == '__main__':
    get_cl_areas()
