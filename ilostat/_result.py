import pandas as pd
import sdmx


class ILOStatQueryResult:
    def __init__(self, data, codelist, language):
        """
        Initialize the ILOStatQueryResult class.

        Args:
            data: SDMX data object containing the results of a query.
            codelist (dict): Dictionary mapping dimension IDs to their codelists.
            language (str): Language code for translating codelist names.
        """
        self._sdmx_data = data  # Store the raw SDMX data
        self._codelist = codelist  # Store the codelist for dimension values
        self.language = language  # Set the preferred language for translations

        # Convert SDMX data to a pandas DataFrame and reset the index
        self._base_df = sdmx.to_pandas(self._sdmx_data).reset_index(name="value")

        # Format the base DataFrame into the final readable version
        self.dataframe = self._format_df()

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
            # Return the localized name for the given column and value
            return self._codelist[column][value].name[self.language]
        except KeyError:
            # Return the original value if a name is not found in the codelist
            return value

    def _format_df(self):
        """
        Format the base DataFrame by applying multipliers, decimals,
        and human-readable names to columns.

        Returns:
            pd.DataFrame: Formatted DataFrame with readable values.
        """
        # Create a deep copy of the base dataframe to avoid modifying the original
        formatted_df = pd.DataFrame.copy(self._base_df, deep=True)

        # Drop the FREQ and MEASURE columns if they are present
        if "FREQ" in formatted_df.columns:
            formatted_df.drop(columns=["FREQ"], inplace=True)

        if "MEASURE" in formatted_df.columns:
            formatted_df.drop(columns=["MEASURE"], inplace=True)

        # Process each observation to apply multipliers and decimals
        for index, observation in enumerate(self._sdmx_data.obs):
            multiplier = pow(10, int(observation.attached_attribute["UNIT_MULT"].value))
            decimals = int(observation.attached_attribute["DECIMALS"].value)
            # Multiply and round values to the specified number of decimals
            formatted_df.loc[index, "value"] = round(
                formatted_df.loc[index, "value"] * multiplier, decimals
            )

        # Apply human-readable names to columns with codelists
        for column in formatted_df.columns:
            if column in self._codelist and self._codelist[column] is not None:
                formatted_df[column] = formatted_df[column].apply(
                    lambda x: self._get_readable_name(column, x)
                )

        # Rename columns to their human-readable names
        column_rename_map = {
            column: self._codelist[column].name.localizations[self.language]
            for column in formatted_df.columns
            if column in self._codelist and hasattr(self._codelist[column], "name")
        }
        formatted_df.rename(columns=column_rename_map, inplace=True)

        return formatted_df

    @property
    def base_dataframe(self):
        """Return the base DataFrame before formatting."""
        return self._base_df

    @property
    def nested_dataframe(self):
        """Return a multi-indexed version of the DataFrame."""
        # Create a deep copy of the formatted DataFrame to avoid modifying the original
        indexed_df = pd.DataFrame.copy(self.dataframe, deep=True)

        # Make the index multi-level by combining all columns except the value
        indexed_df.set_index(
            list(indexed_df.columns[:-1]), inplace=True, drop=True, append=False
        )

        return indexed_df

    @property
    def codelist(self):
        """Retrieve the codelist for dimension values."""
        return self._codelist

    @property
    def sdmx_data(self):
        """Retrieve the raw SDMX data object."""
        return self._sdmx_data


if __name__ == "__main__":
    # Import the query class (assumed to be in a local module)
    from ._query import ILOStatQuery

    # Define parameters for a sample query
    df = "DF_UNE_2EAP_SEX_AGE_RT"

    # Specify dimensions for filtering the query
    dimensions = {
        "SEX": "SEX_M+SEX_F",
        "AGE": "AGE_YTHADULT_YGE15",
        "TIME_PERIOD": "9",
        "REF_AREA": "X01+ITA",
    }

    # Define query parameters such as time range
    params = {"startPeriod": "2020", "endPeriod": "2026"}

    # Instantiate the ILOStatQuery object with parameters
    query = ILOStatQuery(
        language="en", dataflow=df, dimensions=dimensions, params=params
    )

    # Execute the query to retrieve the result
    result = query.data()

    # Extract the formatted DataFrame
    dataframe = result.df

    print(dataframe)

    indexed_dataframe = result.nested_dataframe

    print(indexed_dataframe)
