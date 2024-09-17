import sqlite3


def init_db():
    '''Initialize the database'''

    print("Initializing database")

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


if __name__ == "__main__":
    init_db()
