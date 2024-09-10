import sdmx
import inspect

ilostat = sdmx.Client("ILO")

flow_msg = ilostat.dataflow()

flow_df = sdmx.to_pandas(flow_msg.dataflow)

# print(flow_df[flow_df.str.contains("unemployment", case=False)])
# Let's go with
# Unemployment by sex and rural / urban areas
# DF_UNE_TUNE_SEX_GEO_NB

unemp_msg = ilostat.dataflow("DF_UNE_TUNE_SEX_GEO_NB")

# DataFlowDefinition
unemp_flow = unemp_msg.dataflow.DF_UNE_TUNE_SEX_GEO_NB

# DataFlowDefinition Structure
dsd = unemp_flow.structure

# print(dsd.dimensions.components)
# print(dsd.attributes.components)
# print(dsd.measures.components)

cl = dsd.dimensions.get("FREQ").local_representation.enumerated
# print(sdmx.to_pandas(cl))

# Get the constraints
constraints = unemp_msg.constraint

# Get the content region included in the constraints
cr = constraints.CCA_DF_UNE_TUNE_SEX_GEO_NB.data_content_region[0]

c1 = sdmx.to_pandas(cr.member["REF_AREA"].values)
