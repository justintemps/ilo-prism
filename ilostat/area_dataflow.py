import sdmx
import sqlite3
import time


def get_area_dataflows():
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

    # Initialize the number of dataflows processed
    dataflows_processed = 0

    for df in dataflows:
        # Get the uid of the dataflow from the db
        cur.execute(
            "SELECT dataflow_uid FROM dataflow WHERE dataflow.code = ?", (df,))
        dataflow_uid = cur.fetchone()
        dataflow_uid = dataflow_uid[0]

        # Get the dataflow
        dataflow = None

        # If the request fails, retry three more times
        for i in range(4):
            try:
                dataflow = ilostat.dataflow(df)
                break
            except:
                print(f"Retrying {df}...")
                time.sleep(5)
                continue

        dataflow = ilostat.dataflow(df)

        # Get the constraints
        constraints = dataflow.constraint

        for constraint in constraints:

            # Get the content region included in the constraints
            cr = constraints[constraint].data_content_region[0]

            # Get the members of the content region
            members = cr.member

            # Get the first member
            ref_area = members["REF_AREA"]

            # Get the values of the member
            member_values = ref_area.values

            # For each value
            for member_value in member_values:
                area_code = member_value.value

                # Insert the dataflow into the database
                cur.execute(
                    "SELECT cl_area_uid FROM cl_area WHERE cl_area.code = ?", (area_code,))
                cl_area_uid = cur.fetchone()
                # If the area exists in the database
                if cl_area_uid:
                    cl_area_uid = cl_area_uid[0]

                    cur.execute('''INSERT OR IGNORE INTO cl_area_dataflow (
                                    dataflow_uid,
                                    cl_area_uid)
                                    VALUES(?, ?)''',
                                (dataflow_uid, cl_area_uid))
                    con.commit()
                else:
                    print(f"Error: {df} includes Area {
                          area_code} but this is not in the database")

        print(f"Added {len(member_values)} constraints for {df}")

        # Increment the number of dataflows processed
        dataflows_processed += 1


if __name__ == '__main__':
    get_area_dataflows()
