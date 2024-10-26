import sdmx


def get_dsd(dataflow: str):
    """Get the DSD for the Dataflow and return it"""
    # Create an SDMX Client client
    ilostat = sdmx.Client("ILO")

    # Get the dataflow message
    df_msg = ilostat.dataflow(dataflow)

    # Get the dataflow structure
    df_flow = df_msg.dataflow[dataflow]

    # Get the DSD
    dsd = df_flow.structure

    return dsd
