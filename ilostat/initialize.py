import sqlite3


def init_db():
    '''Initialize the database'''

    # Connect to the database
    con = sqlite3.connect("ilo-prism-cache.db")

    # Create a cursor
    cur = con.cursor()

    # Drop the tables if they exists
    cur.execute("DROP TABLE IF EXISTS cl_areas")
    cur.execute("DROP TABLE IF EXISTS dataflows")

    # Create the table with the list of ilostat areas
    cur.execute("CREATE TABLE IF NOT EXISTS cl_areas(cl_area, name)")

    # Create the table
    cur.execute("CREATE TABLE IF NOT EXISTS dataflows(cl_area, dataflow)")

    # Commit the transaction
    con.commit()

    # Close the cursor
    con.close()

    print("Database initialized")