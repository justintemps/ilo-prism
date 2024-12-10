from typing import Literal
import sdmx


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

    def _get_readable_name(self, column, value):
        """
        Retrieve a human-readable name for a code list value.

        Args:
            column (str): Dimension ID for which the readable name is needed.
            value (str): Specific code value to translate to a human-readable name.

        Returns:
            str: Human-readable name or the original value if not found.
        """
        try:
            return self._codelist[column][value].name[self.language]
        except KeyError:
            return value

    def data(self):
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
        df = sdmx.to_pandas(data).reset_index(name="value")

        # Format the number with the right multiplier and decimals
        for index, observation in enumerate(data.obs):
            multiplier = pow(10, int(observation.attached_attribute["UNIT_MULT"].value))
            decimals = int(observation.attached_attribute["DECIMALS"].value)
            # Apply the multiplier and round the value to the specified number of decimals
            df.loc[index, "value"] = round(
                df.loc[index, "value"] * multiplier, decimals
            )

        # Apply human-readable names to dimension columns
        for column in df.columns:
            if column in self._codelist and self._codelist[column] is not None:
                df[column] = df[column].apply(
                    lambda x: self._get_readable_name(column, x)
                )

        # Rename columns to human-readable names in the specified language
        column_rename_map = {
            column: self._codelist[column].name.localizations[self.language]
            for column in df.columns
            if column in self._codelist and hasattr(self._codelist[column], "name")
        }
        df.rename(columns=column_rename_map, inplace=True)

        return df

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
    df = "DF_EAR_4MTH_SEX_CUR_NB"

    dimensions = {
        "FREQ": "A",
        "MEASURE": "EAR_4MTH_NB",
        "SEX": "SEX_T",
        "CUR": "CUR_TYPE_PPP",
        "REF_AREA": "CMR",
    }
    params = {"startPeriod": "2014", "endPeriod": "2024"}

    # Instantiate and run the query
    query = ILOStatQuery(
        language="en", dataflow=df, dimensions=dimensions, params=params
    )

    result = query.data()

    print("Query URL", query.url)
    print("dataflow", query.dataflow)
    print("dimensions", query.dimensions)
    print("params", query.params)
    print("codelist", query.codelist)

    print(result)
