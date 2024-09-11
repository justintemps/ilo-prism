import sqlite3


def init_db():
    '''Initialize the database'''

    # Connect to the database
    con = sqlite3.connect("ilo-prism-cache.db")

    # Create a cursor
    cur = con.cursor()

    # Drop the table if it exists
    cur.execute("DROP TABLE IF EXISTS dataflows")

    # Create the table
    cur.execute("CREATE TABLE IF NOT EXISTS dataflows(region, dataflow)")

    # Commit the transaction
    con.commit()

    # Close the cursor
    con.close()

    print("Database initialized")
