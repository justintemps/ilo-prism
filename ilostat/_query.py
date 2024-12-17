from typing import Literal
import sdmx
from ._result import ILOStatQueryResult


class ILOStatQuery:
    def __init__(
        self,
        dataflow: str,
        dimensions: dict[str, str],
        params: dict[str, str],
        language: Literal["en", "fr", "es"] = "en",
    ):
        """
        Initialize an ILOStatQuery instance with specific dataflow, dimensions,
        parameters, and language for localized results.

        Args:
            dataflow (str): Dataflow identifier used to specify the dataset.
            dimensions (dict[str, str]): Mapping of dimension IDs to specific values.
            params (dict[str, str]): Additional parameters for data filtering.
            language (Literal): Language code for localized names ("en", "fr", or "es").
        """
        self.dataflow = dataflow
        self.dimensions = dimensions
        self.params = params
        self._ilostat = sdmx.Client(
            "ILO",
            backend="sqlite",
            fast_save=True,
            expire_after=600,
        )  # Initialize SDMX client for ILO data
        self.language = language

        # Internal attributes to store metadata, multiplier, and code list mappings
        self._dsd = None
        self._codelist = None
        self._multiplier = 0
        self._decimals = 1
        self._url = None

        # Set data structure definition, code list, multiplier and decimals on initialization
        self._set_dsd()
        self._set_codelist()

    def _set_url(self, url):
        """Set the URL for the query based on the dataflow, dimensions, and parameters."""
        self._url = url

    def _set_dsd(self):
        """Retrieve and set the data structure definition (DSD) for the specified dataflow."""
        df_msg = self._ilostat.dataflow(self.dataflow)
        df_flow = df_msg.dataflow[self.dataflow]
        self._dsd = df_flow.structure  # Assign the DSD structure to self._dsd

    def _set_codelist(self):
        """Populate the code list with readable names for each dimension component."""
        codelist = {}
        for dim in self._dsd.dimensions.components:
            dim_id = dim.id
            dim_name = self._dsd.dimensions.get(dim_id).local_representation.enumerated
            codelist[dim_id] = dim_name  # Map each dimension ID to its code list
        self._codelist = codelist

    def data(self) -> ILOStatQueryResult:
        """
        Fetch and return data as a Pandas DataFrame, with human-readable names
        for dimensions and values adjusted by the multiplier.

        Returns:
            pd.DataFrame: DataFrame containing the queried data with formatted values.
        """
        # Retrieve the dataflow message based on specified dimensions and parameters
        data_msg = self._ilostat.data(
            self.dataflow,
            dsd=self._dsd,
            key=self.dimensions,
            params=self.params,
        )

        # Remember the URL for the most recent query
        self._set_url(data_msg.response.url)

        # Convert the SDMX message to a Pandas DataFrame
        data = data_msg.data[0]

        # Instantiate ILOStatQueryResult object
        result = ILOStatQueryResult(
            data=data, codelist=self._codelist, language=self.language
        )

        # Return the object as the result
        return result

    @property
    def url(self):
        """Return the URL for the most recent query. Only available after calling data()."""
        return self._url

    @property
    def codelist(self):
        """Return the code list with human-readable names for each dimension."""
        return self._codelist


if __name__ == "__main__":
    # Define parameters for a sample query
    df = "DF_UNE_2EAP_SEX_AGE_RT"

    dimensions = {
        "SEX": "SEX_T+SEX_M+SEX_F",
        "AGE": "AGE_YTHADULT_YGE15",
        "TIME_PERIOD": "9",
        "REF_AREA": "X01+ITA",
    }
    params = {"startPeriod": "2020", "endPeriod": "2026"}

    # Instantiate and run the query
    query = ILOStatQuery(
        language="en", dataflow=df, dimensions=dimensions, params=params
    )

    # Execute the query
    result = query.data()

    # Get the dataframe of the data
    dataframe = result.dataframe

    print("Query URL", query.url)
    print("dataflow", query.dataflow)
    print("dimensions", query.dimensions)
    print("params", query.params)
    print("codelist", query.codelist)
    print(dataframe)
