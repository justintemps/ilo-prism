def get_dsd(ilostat, df):
    """Retrieve and set the data structure definition (DSD) for the specified dataflow."""
    df_msg = ilostat.dataflow(df)
    df_flow = df_msg.dataflow[df]
    return df_flow.structure
