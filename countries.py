import sdmx
import sqlite3

ilostat = sdmx.Client("ILO")

# Get a list of all of the data flows
dataflows_msg = ilostat.dataflow()

# Get the dataflow ids
dataflows_ids = list(dataflows_msg.dataflow)

# For each data flow
for dataflow_id in dataflows_ids:

    # Get the data flow
    dataflow = ilostat.dataflow(dataflow_id)

    # Get the constraints
    constraints = dataflow.constraint

    # Get the constraint ids
    constraint_ids = list(constraints)

    # For each constraint
    for constraint_id in constraint_ids:

        # Get the constraint
        constraint = constraints[constraint_id]

        # Get the content region included in the constraints
        cr = constraint.data_content_region[0]

        # Get the members of the content region
        members = cr.member

        # Get the first member
        member = members["REF_AREA"]

        # Get the values of the member
        values = member.values
