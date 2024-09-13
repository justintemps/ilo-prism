import sqlite3
from ilostat.area import get_cl_areas
from ilostat.dataflow import get_dataflows
from ilostat.area_dataflow import get_area_dataflows


def init_db():
    '''Initialize the database'''
    con = sqlite3.connect("store/ilo-prism.db")
    cur = con.cursor()

    # Initialize the tables from the schema
    with open("store/schema.sql", "r") as f:
        schema = f.read()
        cur.executescript(schema)

    # Commit the transaction
    con.commit()

    # Close the cursor
    con.close()

    print("Database initialized")


if __name__ == "__main__":
    init_db()
    get_cl_areas()
    get_dataflows()
    get_area_dataflows()
