import pandas as pd
import sdmx


class ILOStatQueryResult:
    def __init__(self, data, codelist, language):
        self._sdmx_data = data
        self._codelist = codelist
        self.language = language
        self._base_df = sdmx.to_pandas(self._sdmx_data).reset_index(name="value")
        self.df = self._format_df()

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

    def _format_df(self):

        # Create a copy of the base dataframe
        formatted_df = pd.DataFrame.copy(self._base_df, deep=True)

        # Format the number with the right multiplier and decimals
        for index, observation in enumerate(self._sdmx_data.obs):
            multiplier = pow(10, int(observation.attached_attribute["UNIT_MULT"].value))
            decimals = int(observation.attached_attribute["DECIMALS"].value)
            # Apply the multiplier and round the value to the specified number of decimals
            formatted_df.loc[index, "value"] = round(
                formatted_df.loc[index, "value"] * multiplier, decimals
            )

        # Apply human-readable names to dimension columns
        for column in formatted_df.columns:
            if column in self._codelist and self._codelist[column] is not None:
                formatted_df[column] = formatted_df[column].apply(
                    lambda x: self._get_readable_name(column, x)
                )

        # Rename columns to human-readable names in the specified language
        column_rename_map = {
            column: self._codelist[column].name.localizations[self.language]
            for column in formatted_df.columns
            if column in self._codelist and hasattr(self._codelist[column], "name")
        }
        formatted_df.rename(columns=column_rename_map, inplace=True)

        return formatted_df

    @property
    def codelist(self):
        return self._codelist

    @property
    def sdmx_data(self):
        return self._sdmx_data


if __name__ == "__main__":
    from ._query import ILOStatQuery

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
    dataframe = result.df

    print(dataframe)
