import sdmx
import sqlite3


def get_dataflows():
    '''Get a list of dataflows and insert them into the database together with their names.'''

    # Connect to the database
    con = sqlite3.connect("store/ilo-prism.db")
    cur = con.cursor()

    # Create an SDMX Client client
    ilostat = sdmx.Client("ILO")

    # Get a list of all of the data flows
    dataflows_msg = ilostat.dataflow()

    # Get the dataflows
    dataflows = dataflows_msg.dataflow

    print(
        dataflows_msg.dataflow.DF_WBL_3WBL_SEX_WBL_RT.description.localizations["en"])

    # For each dataflow
    for dataflow in dataflows:
        name_en = dataflows[dataflow].name.localizations["en"]
        name_fr = dataflows[dataflow].name.localizations["fr"]
        name_es = dataflows[dataflow].name.localizations["es"]


if __name__ == '__main__':
    get_dataflows()
