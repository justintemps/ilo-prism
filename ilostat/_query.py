import sdmx


class ILOStatQuery:
    def __init__(
        self,
        dataflow: str,
        dimensions: dict[str, str],
        params: dict[str, str],
    ):
        self.dataflow = dataflow
        self.dimensions = dimensions
        self.params = params
        self._ilostat = sdmx.Client("ILO")

        self._dsd = None
        self._set_dsd()

    def _set_dsd(self):
        # Get the dataflow message
        df_msg = self._ilostat.dataflow(self.dataflow)

        # Get the dataflow structure
        df_flow = df_msg.dataflow[self.dataflow]

        # Get the DSD
        self._dsd = df_flow.structure

    def data(self):
        # Get the dataflow message
        data_msg = self._ilostat.data(
            self.dataflow,
            dsd=self._dsd,
            key=self.dimensions,
            params=self.params,
        )

        # Return the data message
        return data_msg.response.headers["content-type"]
