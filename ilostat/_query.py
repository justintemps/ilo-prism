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
        self._ilostat = sdmx.Client("ILO")  # Initialize SDMX client for ILO data
        self.language = language

        # Internal attributes to store metadata, multiplier, and code list mappings
        self._dsd = None
        self._codelist = None
        self._multiplier = 1

        # Set data structure definition, code list, and multiplier on initialization
        self._set_dsd()
        self._set_codelist()
        self._set_multiplier()

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

    def _set_multiplier(self):
        """Set the multiplier based on the UNIT_MULT attribute in the DSD, if available."""
        for component in self._dsd.attributes.components:
            if component.id == "UNIT_MULT":
                self._multiplier = 10**component.usage_status.value

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
        data = data_msg.data[0]
        df = sdmx.to_pandas(data).reset_index(name="value")

        # Adjust values by the multiplier if applicable
        df["value"] = df["value"] * self._multiplier

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


if __name__ == "__main__":
    # Define parameters for a sample query
    df = "DF_UNE_TUNE_SEX_MTS_DSB_NB"
    dimensions = {
        "FREQ": "A",
        "MEASURE": "UNE_TUNE_NB",
        "SEX": "SEX_T",
        "MTS": "MTS_DETAILS_MRD",
        "DSB": "DSB_STATUS_NODIS",
        "REF_AREA": "ITA",
    }
    params = {"startPeriod": "2015"}

    # Instantiate and run the query
    query = ILOStatQuery(
        language="en", dataflow=df, dimensions=dimensions, params=params
    )
    result = query.data()

    # Print the query result DataFrame
    print(result)
