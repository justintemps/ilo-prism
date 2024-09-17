import sqlite3


def validate_db():
    '''Check if the database is initialized and the metadata is downloaded.
    Returns True if the metadata is downloaded and all of the tables are present,
    False otherwise'''
    con = sqlite3.connect("store/ilo-prism.db")
    cur = con.cursor()

    # Check if the tables have been created
    cur.execute(
        """
        SELECT
            CASE
                WHEN (
                    (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='language') = 0 OR
                    (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='cl_area') = 0 OR
                    (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='cl_area_name') = 0 OR
                    (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='dataflow') = 0 OR
                    (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='dataflow_name') = 0 OR
                    (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='dataflow_description') = 0 OR
                    (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='cl_area_dataflow') = 0
                ) THEN 1
            ELSE 0
        END AS table_check;
        """
    )

    tables_not_exist = cur.fetchone()[0]

    if tables_not_exist == 1:
        return False

    # Check if the data exists in the tables
    cur.execute(
        """
        SELECT
            CASE
                WHEN (
                    (SELECT COUNT(*) FROM language) = 0 OR
                    (SELECT COUNT(*) FROM cl_area) = 0 OR
                    (SELECT COUNT(*) FROM cl_area_name) = 0 OR
                    (SELECT COUNT(*) FROM dataflow) = 0 OR
                    (SELECT COUNT(*) FROM dataflow_name) = 0 OR
                    (SELECT COUNT(*) FROM dataflow_description) = 0 OR
                    (SELECT COUNT(*) FROM cl_area_dataflow) = 0
                ) THEN 1
                ELSE 0
        END AS data_exists_check;
        """
    )

    data_not_exist = cur.fetchone()[0]

    con.close()

    if data_not_exist == 1:
        return False

    return True


if __name__ == "__main__":
    print(validate_db())
