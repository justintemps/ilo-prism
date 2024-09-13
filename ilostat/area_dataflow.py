import sdmx
import sqlite3


class Dataflows:
    def __init__(self):
        self.con = sqlite3.connect("ilo-prism-cache.db")
        self.cur = self.con.cursor()
        self.ilostat = sdmx.Client("ILO")
        self.dataflows_msg = self.ilostat.dataflow()
        self.dataflows_ids = list(self.dataflows_msg.dataflow)
        self.dataflows_processed = 0
        self.__get_dataflows()

    def __get_dataflows(self):
        '''Seeds the database with a list of countries for each dataflow'''
        # Connect to the database

        # Get a list of all of the data flows
        dataflows_msg = self.ilostat.dataflow()

        # Get the dataflow ids
        dataflows_ids = list(dataflows_msg.dataflow)

        # Initialize the number of dataflows processed
        dataflows_processed = 0

        # For each data flow
        for dataflow_id in dataflows_ids:

            # Get the data flow
            dataflow = self.ilostat.dataflow(dataflow_id)

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
                ref_area = members["REF_AREA"]

                # Get the values of the member
                member_values = ref_area.values

                # For each value
                for member_value in member_values:
                    # Insert the dataflow into the database
                    self.cur.execute(
                        "INSERT INTO dataflows(region, dataflow) VALUES(?, ?)", (member_value.value, dataflow_id))
                    self.con.commit()

                print(f"Added {len(member_values)
                               } constraints for {dataflow_id}")

            # Increment the number of dataflows processed
            dataflows_processed += 1

            # Print an update message
            print(f"Processed {dataflows_processed} of {
                len(dataflows_ids)} dataflows")
