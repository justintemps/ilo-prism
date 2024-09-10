import sdmx

ilostat = sdmx.Client("ILO", use_cache=True)

unemp_msg = ilostat.dataflow("DF_UNE_TUNE_SEX_GEO_NB")

unemp_flow = unemp_msg.dataflow.DF_UNE_TUNE_SEX_GEO_NB

dsd = unemp_flow.structure

key = dict(REF_AREA=["ITA"], FREQ="A")

params = {"startPeriod": "2020", "endPeriod": "2022"}

data_msg = ilostat.data("DF_UNE_TUNE_SEX_GEO_NB",
                        key=key, params=params)

print(sdmx.to_pandas(data_msg.data))
